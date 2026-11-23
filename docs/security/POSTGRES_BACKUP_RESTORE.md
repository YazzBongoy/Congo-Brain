# Runbook PostgreSQL — sauvegarde, restauration et preuve de reprise

## Objectif

Ce runbook décrit une sauvegarde PostgreSQL vérifiable et une restauration dans
une base vierge pour Congo-Brain. Une sauvegarde n'est considérée valide qu'après
restauration réussie et contrôle des invariants applicatifs et d'audit.

## Exigences de sécurité

- Ne jamais placer de mot de passe ou de DSN dans Git, un ticket ou les logs.
- Fournir les connexions via variables d'environnement protégées, fichier
  `.pgpass` avec mode `0600`, service libpq ou gestionnaire de secrets.
- Exécuter les opérateurs avec `umask 077`.
- Utiliser une archive PostgreSQL custom, sans propriétaire ni privilèges.
- Restaurer par défaut dans une base neuve et vide.
- Ne jamais utiliser `--clean` sans décision explicite et sauvegarde préalable.
- Conserver l'archive et son fichier SHA-256 dans un stockage chiffré, à accès
  restreint et avec une politique de rétention documentée.

## Variables opérateur

Les exemples supposent les variables suivantes déjà injectées sans les afficher :

```bash
export SOURCE_DB_URL='postgresql://...'
export RESTORE_DB_URL='postgresql://...'
export BACKUP_DIR='/chemin/securise/congo-brain'
export BACKUP_FILE="${BACKUP_DIR}/congo-brain-$(date -u +%Y%m%dT%H%M%SZ).dump"
```

`SOURCE_DB_URL` désigne la base à sauvegarder. `RESTORE_DB_URL` doit désigner une
base de validation neuve et vide, jamais la production.

## 1. Précontrôles

```bash
set -Eeuo pipefail
umask 077

test -n "${SOURCE_DB_URL:-}"
test -n "${RESTORE_DB_URL:-}"
test -n "${BACKUP_DIR:-}"
test -n "${BACKUP_FILE:-}"
mkdir -p "$BACKUP_DIR"

pg_dump --version
pg_restore --version
psql --version
alembic current
alembic heads
```

Critères :

- les outils clients ont la même version majeure que PostgreSQL ou une version
  compatible plus récente ;
- la base source est au head Alembic attendu ;
- la cible de restauration est distincte de la source et vide.

Vérification non destructive de la cible :

```bash
source_identity=$(psql "$SOURCE_DB_URL" -Atqc "select current_database()")
restore_identity=$(psql "$RESTORE_DB_URL" -Atqc "select current_database()")
test "$source_identity" != "$restore_identity"
restore_tables=$(psql "$RESTORE_DB_URL" -Atqc \
  "select count(*) from pg_tables where schemaname='public'")
test "$restore_tables" = "0"
```

Ne pas imprimer les URL de connexion.

## 2. Créer et publier atomiquement la sauvegarde

```bash
tmp_file="${BACKUP_FILE}.tmp.$$"
trap 'rm -f "$tmp_file"' EXIT

pg_dump "$SOURCE_DB_URL" \
  --format=custom \
  --no-owner \
  --no-privileges \
  --file="$tmp_file"

pg_restore --list "$tmp_file" >/dev/null
mv "$tmp_file" "$BACKUP_FILE"
sha256sum "$BACKUP_FILE" >"${BACKUP_FILE}.sha256"
chmod 0600 "$BACKUP_FILE" "${BACKUP_FILE}.sha256"
trap - EXIT
```

Critères : l'archive existe, n'est pas vide, son catalogue est lisible et le
fichier SHA-256 est créé après publication atomique.

## 3. Vérifier l'intégrité avant restauration

```bash
sha256sum --check "${BACKUP_FILE}.sha256"
pg_restore --list "$BACKUP_FILE" >/dev/null
```

Tout échec interrompt immédiatement la procédure. Ne jamais tenter une
restauration avec une archive dont l'empreinte ou le catalogue est invalide.

## 4. Restaurer dans la cible vierge

```bash
restore_started_at=$(date -u +%Y-%m-%dT%H:%M:%SZ)
restore_started_epoch=$(date +%s)

pg_restore \
  --dbname="$RESTORE_DB_URL" \
  --exit-on-error \
  --single-transaction \
  --no-owner \
  --no-privileges \
  "$BACKUP_FILE"

restore_finished_at=$(date -u +%Y-%m-%dT%H:%M:%SZ)
restore_finished_epoch=$(date +%s)
restore_rto_seconds=$((restore_finished_epoch - restore_started_epoch))
```

Ne pas ajouter `--clean` ou `--if-exists` à cette procédure normale.

## 5. Vérifier les invariants restaurés

### Révision Alembic

```bash
restored_revision=$(psql "$RESTORE_DB_URL" -Atqc \
  "select version_num from alembic_version")
expected_revision=$(alembic heads | cut -d' ' -f1)
test "$restored_revision" = "$expected_revision"
```

### Présence des tables critiques et des preuves d'audit

```bash
psql "$RESTORE_DB_URL" -v ON_ERROR_STOP=1 <<'SQL'
select to_regclass('public.users') is not null as users_present;
select to_regclass('public.audit_events') is not null as audit_events_present;
select count(*) as audit_event_count from audit_events;
SQL
```

Comparer les comptes critiques source/cible sans exporter les données :

```bash
for table in users budgets transactions audit_events; do
  source_count=$(psql "$SOURCE_DB_URL" -Atqc "select count(*) from $table")
  restore_count=$(psql "$RESTORE_DB_URL" -Atqc "select count(*) from $table")
  test "$source_count" = "$restore_count"
done
```

### Chaîne d'audit et immutabilité

Configurer temporairement l'application et les tests PostgreSQL vers la cible :

```bash
export DATABASE_URL="$RESTORE_DB_URL"
export POSTGRES_TEST_URL="$RESTORE_DB_URL"
.venv/bin/pytest tests/test_postgres_audit_integration.py -v --tb=short
```

Les essais destructifs d'immutabilité doivent toujours être annulés :

```bash
for statement in \
  "UPDATE audit_events SET action='forbidden'" \
  "DELETE FROM audit_events" \
  "TRUNCATE audit_events"; do
  if psql "$RESTORE_DB_URL" -v ON_ERROR_STOP=1 \
    -c "BEGIN; ${statement}; ROLLBACK;" >/dev/null 2>&1; then
    printf 'ECHEC: immutabilité non appliquée pour %s\n' "$statement" >&2
    exit 1
  fi
done
```

### Démarrage et readiness

Démarrer une instance isolée de Congo-Brain avec `DATABASE_URL` dirigé vers la
base restaurée, puis vérifier :

```bash
curl --fail --silent --show-error http://127.0.0.1:8000/health
```

Tester ensuite une route authentifiée de lecture avec un jeton de validation
injecté par le canal sécurisé prévu. Ne pas enregistrer ce jeton dans le rapport.

## 6. Preuves à consigner

Consigner uniquement des éléments non secrets :

- date UTC et opérateur/validateur ;
- version majeure PostgreSQL ;
- révision Alembic source et restaurée ;
- nom d'archive, taille et SHA-256 ;
- heure de début/fin et RTO observé ;
- égalité des comptes des tables critiques ;
- résultat du test de chaîne/immutabilité d'audit ;
- résultat du health/readiness applicatif ;
- emplacement logique du stockage et politique de rétention ;
- anomalies, décision et actions correctives.

Statuts autorisés : `PASS`, `FAIL`, `BLOCKED`, `NOT RUN`. Une archive créée mais
non restaurée porte le statut `NOT RUN` pour la reprise et ne valide pas le gate.

## 7. Nettoyage

Après collecte des preuves :

1. arrêter l'instance applicative isolée ;
2. révoquer les identifiants temporaires ;
3. supprimer la base de validation ;
4. supprimer les copies locales temporaires ;
5. conserver uniquement l'archive publiée et son SHA-256 selon la rétention.

Exemple, avec le nom de base explicitement contrôlé par l'opérateur :

```bash
dropdb --if-exists congo_brain_restore_validation
```

Ne jamais automatiser une suppression à partir d'une valeur non vérifiée ou
d'un motif large.

## 8. Fréquence et responsabilités

- Sauvegarde : quotidienne ou selon le RPO approuvé.
- Test de restauration : au minimum mensuel et avant une release majeure.
- Propriétaire : exploitation PostgreSQL/SRE.
- Validation applicative : responsable Congo-Brain.
- Escalade immédiate : empreinte invalide, restauration échouée, révision
  Alembic incorrecte, perte d'événements d'audit ou trigger d'immutabilité absent.

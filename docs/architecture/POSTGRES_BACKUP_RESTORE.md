# Runbook PostgreSQL — Sauvegarde et restauration

Ce runbook couvre deux unités de reprise distinctes : la base transactionnelle Congo-Brain avec les preuves de sécurité du journal `audit_events`, et la base Keycloak avec les identités et rôles. Un volume Docker/PVC assure la persistance mais ne constitue jamais une sauvegarde. Une sauvegarde n'est considérée exploitable qu'après validation de son catalogue, contrôle d'intégrité et test périodique de restauration.

## Objectifs de service

| Indicateur | Cible initiale |
|---|---:|
| RPO (perte de données maximale) | 24 heures |
| RTO (retour au service) | 4 heures |
| Rétention quotidienne | 30 jours |
| Test de restauration | mensuel et avant chaque release majeure |
| Conservation hors site | stockage chiffré, région/compte distinct |

Ces cibles doivent être réévaluées avec les ministères utilisateurs avant la production nationale.

## Prérequis et responsabilités

- PostgreSQL 16 client : `pg_dump`, `pg_restore`, `psql`.
- Accès réseau à la base et identifiants lus depuis un gestionnaire de secrets.
- Répertoire de sauvegarde chiffré, permission `0700`, capacité surveillée.
- Un opérateur exécute la procédure ; un second valide le test de restauration et le procès-verbal.
- Ne jamais placer un DSN, mot de passe, dump ou jeton dans Git, un ticket ou les logs CI.

Les scripts utilisent `PG_DSN` uniquement depuis l'environnement du processus. Pour éviter sa présence dans l'historique du shell, l'injecter avec le gestionnaire de secrets de la plateforme.

## Sauvegarde manuelle vérifiée

```bash
export PG_DSN="$(secret-manager read congo-brain/postgres/backup-dsn)"
BACKUP_DIR=/srv/congo-brain/backups \
BACKUP_NAME=congo_brain \
  scripts/backup_postgres.sh
unset PG_DSN
```

Le script :

1. crée un dump PostgreSQL au format custom ;
2. exclut les propriétaires et privilèges spécifiques à l'environnement ;
3. valide le catalogue avec `pg_restore --list` ;
4. publie le fichier atomiquement ;
5. génère un fichier `.sha256` ;
6. ne supprime aucun artefact : la rétention est appliquée par une politique de cycle de vie du stockage chiffré.

Exécuter séparément la même procédure avec le DSN Keycloak et `BACKUP_NAME=keycloak`. Copier ensuite chaque dump et son checksum vers le stockage hors site chiffré. Activer le versionnement et, si disponible, l'immutabilité/WORM du bucket.

## Planification

Planifier le script avec le mécanisme natif de la plateforme : cron Kubernetes, tâche Render externe ou ordonnanceur d'infrastructure. La tâche doit :

- utiliser un compte PostgreSQL dédié disposant des droits de lecture nécessaires ;
- monter/injecter le secret au runtime ;
- envoyer une alerte sur toute sortie non nulle ;
- surveiller l'âge de la dernière sauvegarde, sa taille et l'espace disponible ;
- ne jamais publier le DSN dans les logs.

Exemple de politique : sauvegarde quotidienne à 01:00 UTC et test de restauration le premier dimanche du mois.

## Restauration sûre dans une base vide

La procédure normale restaure d'abord dans une **nouvelle base isolée**, jamais directement sur la production :

```bash
export PG_DSN="$(secret-manager read congo-brain/postgres/restore-test-dsn)"
export BACKUP_FILE=/srv/congo-brain/backups/congo-brain-YYYYMMDDTHHMMSSZ.dump
CONFIRM_RESTORE=RESTORE scripts/restore_postgres.sh
unset PG_DSN BACKUP_FILE
```

Le script exige et vérifie le checksum, valide le catalogue puis utilise une transaction unique. Toute cible contenant déjà des tables utilisateur fait échouer l'opération ; aucune dérogation destructive n'est implémentée.

## Validation obligatoire après restauration

```bash
export DATABASE_URL="$PG_DSN"
alembic current
python -m pytest tests/test_postgres_audit_integration.py -v
psql "$PG_DSN" -v ON_ERROR_STOP=1 -c "SELECT COUNT(*) FROM audit_events;"
unset DATABASE_URL
```

Vérifier également :

- la révision Alembic correspond à `head` ;
- les comptes, rôles et rattachements ministériels attendus sont présents ;
- la chaîne de hash du journal d'audit est valide ;
- `UPDATE`, `DELETE` et `TRUNCATE` sur `audit_events` sont refusés ;
- `/health` répond après démarrage de l'application sur la base restaurée ;
- les volumes métier sont cohérents avec le procès-verbal de sauvegarde.

## Reprise après sinistre sur une cible existante

La reprise nécessite une décision d'incident documentée, un arrêt des écritures et une approbation à deux personnes. Le script refuse toute cible non vide et n'offre aucune option `--clean`.

1. Déclarer l'incident et noter le dernier point de restauration sain.
2. Mettre l'application en maintenance et arrêter les producteurs de données.
3. Capturer, si possible, une sauvegarde forensique de l'état défaillant.
4. Créer une nouvelle base vide et basculer ensuite `DATABASE_URL`.
5. Restaurer uniquement vers cette nouvelle cible :

```bash
PG_DSN="$(secret-manager read congo-brain/postgres/recovery-dsn)" \
BACKUP_FILE=/secure/validated.dump \
CONFIRM_RESTORE=RESTORE \
  scripts/restore_postgres.sh
```

6. Exécuter toutes les validations ci-dessus avant la remise en service.
7. Réactiver progressivement le trafic et surveiller erreurs, latence et intégrité d'audit.
8. Conserver les logs et le procès-verbal pour l'analyse post-incident.

## Procès-verbal de test

Pour chaque exercice, enregistrer sans secret :

- identifiant et date de la sauvegarde ;
- taille et empreinte SHA-256 ;
- environnement cible isolé ;
- heure de début/fin et RTO observé ;
- révision Alembic ;
- résultats des contrôles d'intégrité et d'audit ;
- opérateur et validateur ;
- anomalies et actions correctives.

Une release reste bloquée si la dernière restauration testée a échoué ou si elle dépasse la fréquence mensuelle convenue.

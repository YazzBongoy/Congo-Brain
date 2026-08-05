"""Database management CLI commands."""

import typer
from rich.console import Console

console = Console()
db_app = typer.Typer(help="Gestion de la base de donnees.")


@db_app.command("init")
def init_database() -> None:
    """Initialiser la base de donnees (creer les tables)."""
    from congo_brain.core.database import init_db
    init_db()
    console.print("[green]Base de donnees initialisee avec succes.[/]")


@db_app.command("seed")
def seed_database() -> None:
    """Remplir la base de donnees avec les donnees d'exemple."""
    from congo_brain.core.database import SessionLocal, init_db
    from congo_brain.data.seed import seed_all
    init_db()
    db = SessionLocal()
    try:
        seed_all(db)
        console.print("[green]Donnees d'exemple inserees avec succes.[/]")
    finally:
        db.close()


@db_app.command("reset")
def reset_database(
    confirm: bool = typer.Option(False, "--yes", "-y", help="Confirmer la reinitialisation"),
) -> None:
    """Reinitialiser la base de donnees (ATTENTION: supprime toutes les donnees)."""
    if not confirm:
        console.print("[yellow]Utilisez --yes pour confirmer la reinitialisation.[/]")
        raise typer.Exit()
    import congo_brain.models  # noqa: F401
    from congo_brain.core.database import Base, engine, init_db
    Base.metadata.drop_all(bind=engine)
    init_db()
    console.print("[green]Base de donnees reinitialisee.[/]")

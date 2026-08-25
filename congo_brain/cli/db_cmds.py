"""Database management CLI commands."""

from pathlib import Path

import typer
from alembic.config import Config
from rich.console import Console

from alembic import command

console = Console()
db_app = typer.Typer(help="Gestion de la base de donnees.")


def _upgrade_database() -> None:
    """Apply the complete Alembic migration chain."""
    project_root = Path(__file__).resolve().parents[2]
    command.upgrade(Config(str(project_root / "alembic.ini")), "head")


@db_app.command("init")
def init_database() -> None:
    """Initialiser la base avec toutes les migrations Alembic."""
    _upgrade_database()
    console.print("[green]Base de donnees initialisee avec succes.[/]")


@db_app.command("seed")
def seed_database() -> None:
    """Remplir la base de donnees avec les donnees d'exemple."""
    from congo_brain.core.database import SessionLocal, verify_database_migrations
    from congo_brain.data.seed import seed_all

    verify_database_migrations()
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
    """Reinitialiser une base de développement (ATTENTION: supprime toutes les donnees)."""
    if not confirm:
        console.print("[yellow]Utilisez --yes pour confirmer la reinitialisation.[/]")
        raise typer.Exit()

    from congo_brain.core.config import ENVIRONMENT

    if ENVIRONMENT in {"production", "staging"}:
        console.print("[red]La reinitialisation est interdite en production et staging.[/]")
        raise typer.Exit(code=2)

    from sqlalchemy import text

    import congo_brain.models  # noqa: F401
    from congo_brain.core.database import Base, engine

    Base.metadata.drop_all(bind=engine)
    with engine.begin() as connection:
        connection.execute(text("DROP TABLE IF EXISTS alembic_version"))
    _upgrade_database()
    console.print("[green]Base de donnees reinitialisee.[/]")

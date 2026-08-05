"""User management CLI commands."""

import typer
from rich.console import Console
from rich.table import Table

from congo_brain.core.security import hash_password

console = Console()
user_app = typer.Typer(help="Gestion des utilisateurs.")


@user_app.command("create")
def create_user(
    username: str = typer.Option(..., prompt=True, help="Nom d'utilisateur"),
    email: str = typer.Option(..., prompt=True, help="Adresse email"),
    password: str = typer.Option(..., prompt=True, hide_input=True, help="Mot de passe"),
    role: str = typer.Option("viewer", help="Role: admin, analyst, viewer"),
    ministry: str = typer.Option(None, help="Ministere"),
) -> None:
    """Creer un nouvel utilisateur."""
    from congo_brain.core.database import SessionLocal
    from congo_brain.models.user import User

    db = SessionLocal()
    try:
        existing = db.query(User).filter((User.username == username) | (User.email == email)).first()
        if existing:
            console.print("[red]Un utilisateur avec ce nom ou email existe deja.[/]")
            raise typer.Exit(code=1)
        user = User(username=username, email=email, password_hash=hash_password(password), role=role, ministry=ministry)
        db.add(user)
        db.commit()
        console.print(f"[green]Utilisateur '{username}' cree avec succes (role: {role}).[/]")
    finally:
        db.close()


@user_app.command("list")
def list_users() -> None:
    """Lister tous les utilisateurs."""
    from congo_brain.core.database import SessionLocal
    from congo_brain.models.user import User

    db = SessionLocal()
    try:
        users = db.query(User).all()
        if not users:
            console.print("[yellow]Aucun utilisateur trouve.[/]")
            return
        table = Table(title="Utilisateurs", show_lines=True)
        table.add_column("ID", style="dim")
        table.add_column("Username", style="bold cyan")
        table.add_column("Email", style="blue")
        table.add_column("Role", style="green")
        table.add_column("Ministere", style="yellow")
        for u in users:
            table.add_row(str(u.id), u.username, u.email, u.role, u.ministry or "-")
        console.print(table)
    finally:
        db.close()

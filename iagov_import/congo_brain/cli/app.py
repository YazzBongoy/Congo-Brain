"""Congo-Brain CLI — main entry point assembling all sub-commands."""

from typing import Optional

import typer
from rich.console import Console
from rich.panel import Panel

from congo_brain import __app_name__, __version__
from congo_brain.cli.budget_cmds import budget_app
from congo_brain.cli.citizen_cmds import citizen_app
from congo_brain.cli.db_cmds import db_app
from congo_brain.cli.investment_cmds import investment_app
from congo_brain.cli.security_cmds import security_app
from congo_brain.cli.transparency_cmds import transparency_app
from congo_brain.cli.user_cmds import user_app

console = Console()

app = typer.Typer(
    name="congo-brain",
    help="Congo-Brain — Plateforme IA de gouvernance pour la RDC",
    add_completion=False,
)

app.add_typer(db_app, name="db")
app.add_typer(user_app, name="user")
app.add_typer(budget_app, name="budget")
app.add_typer(investment_app, name="investment")
app.add_typer(transparency_app, name="transparency")
app.add_typer(security_app, name="security")
app.add_typer(citizen_app, name="citizen")


def version_callback(value: bool) -> None:
    if value:
        console.print(f"[bold blue]{__app_name__}[/] version [green]{__version__}[/]")
        raise typer.Exit()


@app.callback()
def main(
    version: Optional[bool] = typer.Option(
        None, "--version", "-v",
        help="Afficher la version.",
        callback=version_callback, is_eager=True,
    ),
) -> None:
    """Congo-Brain — Plateforme IA de gouvernance pour la RDC."""


@app.command("health")
def health() -> None:
    """Verifier l'etat de sante du systeme."""
    from congo_brain.core.database import SessionLocal
    try:
        db = SessionLocal()
        db.execute("SELECT 1")  # type: ignore[arg-type]
        db.close()
        console.print(Panel(
            "[bold green]Systeme operationnel[/]\nBase de donnees: OK",
            title="Health Check", border_style="green",
        ))
    except Exception as e:
        console.print(Panel(f"[bold red]Erreur[/]\n{e}", title="Health Check", border_style="red"))
        raise typer.Exit(code=1)


@app.command("about")
def about() -> None:
    """Afficher les informations sur Congo-Brain."""
    console.print(
        Panel(
            f"[bold blue]{__app_name__}[/] v{__version__}\n\n"
            "Plateforme IA de gouvernance pour la\n"
            "Republique Democratique du Congo.\n\n"
            "[bold]Modules:[/]\n"
            "  [cyan]BudgetGuard[/]  — Controle budgetaire & detection d'anomalies\n"
            "  [cyan]InvestSmart[/]  — Optimisation des investissements publics\n"
            "  [cyan]TranspaFin[/]   — Transparence financiere & conformite\n"
            "  [cyan]PeaceNet[/]     — Securite & cohesion sociale\n"
            "  [cyan]Services Citoyens[/] — Procedures, contacts, droits, FAQ",
            title="A Propos",
            border_style="blue",
        )
    )

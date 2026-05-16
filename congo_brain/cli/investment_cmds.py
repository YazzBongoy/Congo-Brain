"""InvestSmart CLI commands."""

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

console = Console()
investment_app = typer.Typer(help="InvestSmart — Optimisation des investissements publics.")


@investment_app.command("list")
def list_investments(
    status: str = typer.Option(None, "--status", "-s", help="Filtrer par statut"),
    province: str = typer.Option(None, "--province", "-p", help="Filtrer par province"),
) -> None:
    """Lister tous les projets d'investissement."""
    from congo_brain.core.database import SessionLocal
    from congo_brain.services.investment_service import InvestmentService

    db = SessionLocal()
    try:
        svc = InvestmentService(db)
        investments = svc.list_investments(status=status, province=province)
        if not investments:
            console.print("[yellow]Aucun investissement trouve.[/]")
            return
        table = Table(title="Projets d'Investissement", show_lines=True)
        table.add_column("ID", style="dim")
        table.add_column("Projet", style="bold cyan", min_width=25)
        table.add_column("Province", style="green")
        table.add_column("Secteur", style="blue")
        table.add_column("Budget (FC)", style="yellow", justify="right")
        table.add_column("ROI", style="magenta", justify="right")
        table.add_column("Statut", style="white")
        for inv in investments:
            table.add_row(
                str(inv.id), inv.project_name, inv.province,
                inv.sector, f"{inv.total_budget:,.0f}",
                f"{inv.roi_score}%", inv.status,
            )
        console.print(table)
    finally:
        db.close()


@investment_app.command("optimize")
def optimize(
    budget: float = typer.Option(..., "--budget", "-b", help="Budget limite en FC"),
) -> None:
    """Optimiser le portefeuille d'investissements."""
    from congo_brain.core.database import SessionLocal
    from congo_brain.services.investment_service import InvestmentService

    db = SessionLocal()
    try:
        svc = InvestmentService(db)
        result = svc.optimize(budget)

        info = Text()
        info.append("\nBudget limite: ", style="bold")
        info.append(f"{budget:,.0f} FC\n", style="cyan")
        info.append("Cout total selectionne: ", style="bold")
        info.append(f"{result['total_cost']:,.0f} FC\n", style="green")
        info.append("ROI total attendu: ", style="bold")
        info.append(f"{result['expected_total_roi']}%\n", style="yellow")
        console.print(Panel(info, title="Optimisation du Portefeuille", border_style="green"))

        if result["selected_projects"]:
            table = Table(title="Projets Selectionnes", show_lines=True)
            table.add_column("Projet", style="bold cyan")
            table.add_column("Province", style="green")
            table.add_column("Budget (FC)", style="yellow", justify="right")
            table.add_column("ROI", style="magenta", justify="right")
            for inv in result["selected_projects"]:
                table.add_row(inv.project_name, inv.province, f"{inv.total_budget:,.0f}", f"{inv.roi_score}%")
            console.print(table)
    finally:
        db.close()


@investment_app.command("summary")
def investment_summary() -> None:
    """Afficher le resume des investissements."""
    from congo_brain.core.database import SessionLocal
    from congo_brain.services.investment_service import InvestmentService

    db = SessionLocal()
    try:
        svc = InvestmentService(db)
        summary = svc.get_summary()
        info = Text()
        info.append("\nTotal projets: ", style="bold")
        info.append(f"{summary['total_projects']}\n", style="cyan")
        info.append("Budget total: ", style="bold")
        info.append(f"{summary['total_budget']:,.0f} FC\n", style="green")
        info.append("Depense totale: ", style="bold")
        info.append(f"{summary['total_spent']:,.0f} FC\n", style="yellow")
        info.append("ROI moyen: ", style="bold")
        info.append(f"{summary['avg_roi']}%\n", style="magenta")
        if summary["by_status"]:
            info.append("\nPar statut: ", style="bold")
            for st, cnt in summary["by_status"].items():
                info.append(f"{st}={cnt}  ", style="blue")
            info.append("\n")
        console.print(Panel(info, title="Resume des Investissements", border_style="blue"))
    finally:
        db.close()

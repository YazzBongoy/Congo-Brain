"""TranspaFin CLI commands."""

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

console = Console()
transparency_app = typer.Typer(help="TranspaFin — Transparence financiere et conformite.")


@transparency_app.command("list")
def list_reports(
    ministry: str = typer.Option(None, "--ministry", "-m", help="Filtrer par ministere"),
    status: str = typer.Option(None, "--status", "-s", help="Filtrer par statut"),
) -> None:
    """Lister les rapports de transparence."""
    from congo_brain.core.database import SessionLocal
    from congo_brain.services.transparency_service import TransparencyService

    db = SessionLocal()
    try:
        svc = TransparencyService(db)
        reports = svc.list_reports(ministry, status)
        if not reports:
            console.print("[yellow]Aucun rapport trouve.[/]")
            return
        table = Table(title="Rapports de Transparence", show_lines=True)
        table.add_column("ID", style="dim")
        table.add_column("Ministere", style="bold cyan", min_width=25)
        table.add_column("Periode", style="green")
        table.add_column("Transparence", style="yellow", justify="right")
        table.add_column("Conformite", style="magenta", justify="right")
        table.add_column("Statut", style="blue")
        for r in reports:
            table.add_row(
                str(r.id),
                r.ministry,
                r.period,
                f"{r.transparency_score}%",
                f"{r.compliance_rate}%",
                r.status,
            )
        console.print(table)
    finally:
        db.close()


@transparency_app.command("dashboard")
def transparency_dashboard() -> None:
    """Afficher le tableau de bord de transparence."""
    from congo_brain.core.database import SessionLocal
    from congo_brain.services.transparency_service import TransparencyService

    db = SessionLocal()
    try:
        svc = TransparencyService(db)
        dash = svc.get_dashboard()

        info = Text()
        info.append("\nTotal rapports: ", style="bold")
        info.append(f"{dash['total_reports']}\n", style="cyan")
        info.append("Score de transparence moyen: ", style="bold")
        info.append(f"{dash['avg_transparency_score']}%\n", style="green")
        info.append("Taux de conformite moyen: ", style="bold")
        info.append(f"{dash['avg_compliance_rate']}%\n", style="yellow")
        console.print(Panel(info, title="Tableau de Bord Transparence (TranspaFin)", border_style="blue"))

        if dash.get("by_ministry"):
            table = Table(title="Par Ministere", show_lines=True)
            table.add_column("Ministere", style="bold cyan", min_width=25)
            table.add_column("Rapports", style="yellow", justify="right")
            table.add_column("Transparence", style="green", justify="right")
            table.add_column("Conformite", style="magenta", justify="right")
            for entry in dash["by_ministry"]:
                table.add_row(
                    entry["ministry"],
                    str(entry["report_count"]),
                    f"{entry['avg_transparency_score']}%",
                    f"{entry['avg_compliance_rate']}%",
                )
            console.print(table)
    finally:
        db.close()

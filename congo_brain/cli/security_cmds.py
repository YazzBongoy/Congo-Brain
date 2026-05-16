"""PeaceNet CLI commands."""

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

console = Console()
security_app = typer.Typer(help="PeaceNet — Securite et cohesion sociale.")


@security_app.command("list")
def list_alerts(
    province: str = typer.Option(None, "--province", "-p", help="Filtrer par province"),
    severity: str = typer.Option(None, "--severity", "-s", help="Filtrer par severite"),
    active: bool = typer.Option(False, "--active", "-a", help="Uniquement les alertes actives"),
) -> None:
    """Lister les alertes de securite."""
    from congo_brain.core.database import SessionLocal
    from congo_brain.services.security_service import SecurityService

    db = SessionLocal()
    try:
        svc = SecurityService(db)
        alerts = svc.list_alerts(province, severity, active)
        if not alerts:
            console.print("[yellow]Aucune alerte trouvee.[/]")
            return
        table = Table(title="Alertes de Securite", show_lines=True)
        table.add_column("ID", style="dim")
        table.add_column("Type", style="bold cyan")
        table.add_column("Severite", style="red")
        table.add_column("Province", style="green")
        table.add_column("Risque", style="magenta", justify="right")
        table.add_column("Statut", style="yellow")
        for a in alerts:
            sev_map = {
                "critical": "bold red",
                "high": "red",
                "medium": "yellow",
                "low": "green",
            }
            sev_style = sev_map.get(a.severity, "white")
            status = "Resolu" if a.is_resolved else "Actif"
            table.add_row(
                str(a.id),
                a.alert_type,
                Text(a.severity, style=sev_style),
                a.province,
                f"{a.risk_score:.1f}",
                status,
            )
        console.print(table)
    finally:
        db.close()


@security_app.command("dashboard")
def security_dashboard() -> None:
    """Afficher le tableau de bord de securite."""
    from congo_brain.core.database import SessionLocal
    from congo_brain.services.security_service import SecurityService

    db = SessionLocal()
    try:
        svc = SecurityService(db)
        dash = svc.get_dashboard()

        info = Text()
        info.append("\nTotal alertes: ", style="bold")
        info.append(f"{dash['total_alerts']}\n", style="cyan")
        info.append("Alertes actives: ", style="bold")
        info.append(f"{dash['active_alerts']}\n", style="red")
        info.append("Alertes resolues: ", style="bold")
        info.append(f"{dash['resolved_alerts']}\n", style="green")
        info.append("Score de risque moyen: ", style="bold")
        info.append(f"{dash['avg_risk_score']}\n", style="yellow")
        info.append("\nPar severite: ", style="bold")
        info.append(f"Critique={dash.get('critical_count', 0)} ", style="red")
        info.append(f"Haut={dash.get('high_count', 0)} ", style="yellow")
        info.append(f"Moyen={dash.get('medium_count', 0)} ", style="cyan")
        info.append(f"Bas={dash.get('low_count', 0)}\n", style="green")
        console.print(Panel(info, title="Tableau de Bord Securite (PeaceNet)", border_style="red"))

        if dash.get("by_province"):
            table = Table(title="Alertes par Province", show_lines=True)
            table.add_column("Province", style="bold cyan")
            table.add_column("Alertes", style="yellow", justify="right")
            table.add_column("Indice Risque", style="red", justify="right")
            for entry in dash["by_province"]:
                table.add_row(
                    entry["province"],
                    str(entry["total_alerts"]),
                    f"{entry['risk_index']:.1f}",
                )
            console.print(table)
    finally:
        db.close()


@security_app.command("resolve")
def resolve_alert(
    alert_id: int = typer.Argument(..., help="ID de l'alerte a resoudre"),
) -> None:
    """Marquer une alerte comme resolue."""
    from congo_brain.core.database import SessionLocal
    from congo_brain.services.security_service import SecurityService

    db = SessionLocal()
    try:
        svc = SecurityService(db)
        alert = svc.resolve_alert(alert_id)
        if not alert:
            console.print(f"[red]Alerte {alert_id} non trouvee.[/]")
            raise typer.Exit(code=1)
        console.print(f"[green]Alerte {alert_id} marquee comme resolue.[/]")
    finally:
        db.close()

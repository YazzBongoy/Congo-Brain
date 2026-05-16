"""BudgetGuard CLI commands."""

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

console = Console()
budget_app = typer.Typer(help="BudgetGuard — Controle budgetaire et detection d'anomalies.")


@budget_app.command("status")
def budget_status() -> None:
    """Afficher le statut budgetaire global."""
    from congo_brain.core.database import SessionLocal
    from congo_brain.services.budget_service import BudgetService

    db = SessionLocal()
    try:
        svc = BudgetService(db)
        status = svc.get_status()

        info = Text()
        info.append("\nBudgets: ", style="bold")
        info.append(f"{status['total_budgets']}\n", style="cyan")
        info.append("Total alloue: ", style="bold")
        info.append(f"{status['total_allocated']:,.0f} FC\n", style="green")
        info.append("Total depense: ", style="bold")
        info.append(f"{status['total_spent']:,.0f} FC\n", style="yellow")
        info.append("Taux d'execution: ", style="bold")
        rate = status['overall_execution_rate']
        color = "green" if rate < 80 else "yellow" if rate < 100 else "red"
        info.append(f"{rate}%\n", style=color)
        console.print(Panel(info, title="Statut Budgetaire Global", border_style="cyan"))

        if status["by_ministry"]:
            table = Table(title="Par Ministere", show_lines=True)
            table.add_column("Ministere", style="bold cyan", min_width=25)
            table.add_column("Alloue (FC)", style="green", justify="right")
            table.add_column("Depense (FC)", style="yellow", justify="right")
            table.add_column("Execution", style="magenta", justify="right")
            for m in status["by_ministry"]:
                table.add_row(m["ministry"], f"{m['allocated']:,.0f}", f"{m['spent']:,.0f}", f"{m['execution_rate']}%")
            console.print(table)
    finally:
        db.close()


@budget_app.command("anomalies")
def detect_anomalies() -> None:
    """Detecter les anomalies dans les transactions."""
    from congo_brain.core.database import SessionLocal
    from congo_brain.services.budget_service import BudgetService

    db = SessionLocal()
    try:
        svc = BudgetService(db)
        report = svc.run_anomaly_detection()

        info = Text()
        info.append("\nTransactions analysees: ", style="bold")
        info.append(f"{report['total_transactions']}\n", style="cyan")
        info.append("Anomalies detectees: ", style="bold")
        info.append(f"{report['anomalies_detected']}\n", style="red" if report['anomalies_detected'] else "green")
        info.append("Taux d'anomalie: ", style="bold")
        info.append(f"{report['anomaly_rate']}%\n", style="yellow")
        console.print(Panel(info, title="Rapport de Detection d'Anomalies", border_style="red"))

        if report.get("rules_applied"):
            console.print("\n[bold]Regles appliquees:[/]")
            for rule in report["rules_applied"]:
                console.print(f"  [dim]•[/] {rule}")

        if report["anomalies"]:
            table = Table(title="\nTransactions Suspectes", show_lines=True)
            table.add_column("Ref", style="dim")
            table.add_column("Montant (FC)", style="red", justify="right")
            table.add_column("Description", style="white", max_width=35)
            table.add_column("Beneficiaire", style="yellow", max_width=20)
            table.add_column("Score", style="magenta", justify="right")
            table.add_column("Raisons", style="bright_red", max_width=50)
            for t in report["anomalies"]:
                reasons = t.anomaly_reason or "-"
                table.add_row(
                    t.reference_number, f"{t.amount:,.0f}",
                    t.description[:35], t.beneficiary or "-",
                    f"{t.anomaly_score:.2f}",
                    reasons,
                )
            console.print(table)
    finally:
        db.close()


@budget_app.command("list")
def list_budgets() -> None:
    """Lister tous les budgets."""
    from congo_brain.core.database import SessionLocal
    from congo_brain.services.budget_service import BudgetService

    db = SessionLocal()
    try:
        svc = BudgetService(db)
        budgets = svc.list_budgets()
        if not budgets:
            console.print("[yellow]Aucun budget trouve.[/]")
            return
        table = Table(title="Budgets", show_lines=True)
        table.add_column("ID", style="dim")
        table.add_column("Ministere", style="bold cyan", min_width=25)
        table.add_column("Secteur", style="green")
        table.add_column("Alloue (FC)", style="yellow", justify="right")
        table.add_column("Depense (FC)", style="red", justify="right")
        table.add_column("Execution", style="magenta", justify="right")
        table.add_column("Annee", style="blue")
        for b in budgets:
            table.add_row(
                str(b.id), b.ministry, b.sector,
                f"{b.allocated_amount:,.0f}",
                f"{b.spent_amount:,.0f}",
                f"{b.execution_rate}%", str(b.fiscal_year),
            )
        console.print(table)
    finally:
        db.close()

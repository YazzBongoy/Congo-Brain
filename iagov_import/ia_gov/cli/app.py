"""CLI application using Typer and Rich."""

from typing import Optional

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from ia_gov import __app_name__, __version__
from ia_gov.services.gov_service import GovService

console = Console()
app = typer.Typer(
    name="ia-gov",
    help="🏛️  IA Gouvernementale II — Assistant IA des services gouvernementaux de la RDC",
    add_completion=False,
)
service = GovService()


def version_callback(value: bool) -> None:
    if value:
        console.print(f"[bold blue]{__app_name__}[/] version [green]{__version__}[/]")
        raise typer.Exit()


@app.callback()
def main(
    version: Optional[bool] = typer.Option(
        None,
        "--version",
        "-v",
        help="Afficher la version de l'application.",
        callback=version_callback,
        is_eager=True,
    ),
) -> None:
    """IA Gouvernementale II — Votre assistant pour les services publics de la RDC."""


# ─── Procedures ───────────────────────────────────────────────


@app.command("procedures")
def list_procedures(
    category: Optional[str] = typer.Option(None, "--category", "-c", help="Filtrer par catégorie"),
) -> None:
    """Lister toutes les procédures administratives."""
    procedures = service.list_procedures(category)
    if not procedures:
        console.print("[yellow]Aucune procédure trouvée.[/]")
        raise typer.Exit()

    table = Table(title="Procédures Administratives", show_lines=True)
    table.add_column("ID", style="dim", width=10)
    table.add_column("Nom", style="bold cyan", min_width=25)
    table.add_column("Catégorie", style="green")
    table.add_column("Frais", style="yellow")
    table.add_column("Délai", style="magenta")

    for proc in procedures:
        table.add_row(
            proc["id"],
            proc["name"],
            proc["category"],
            proc["fees"],
            proc["processing_time"],
        )

    console.print(table)


@app.command("procedure")
def show_procedure(
    proc_id: str = typer.Argument(help="ID de la procédure (ex: proc-001)"),
) -> None:
    """Afficher les détails d'une procédure spécifique."""
    proc = service.get_procedure(proc_id)
    if not proc:
        console.print(f"[red]Procédure '{proc_id}' non trouvée.[/]")
        raise typer.Exit(code=1)

    panel_content = Text()
    panel_content.append(f"\n{proc['description']}\n\n", style="italic")
    panel_content.append("Catégorie: ", style="bold")
    panel_content.append(f"{proc['category']}\n", style="green")
    panel_content.append("Autorité: ", style="bold")
    panel_content.append(f"{proc['authority']}\n", style="blue")
    panel_content.append("Frais: ", style="bold")
    panel_content.append(f"{proc['fees']}\n", style="yellow")
    panel_content.append("Délai: ", style="bold")
    panel_content.append(f"{proc['processing_time']}\n", style="magenta")

    console.print(Panel(panel_content, title=f"[bold]{proc['name']}[/]", border_style="cyan"))

    # Steps
    steps_table = Table(title="Étapes", show_lines=True)
    steps_table.add_column("#", style="bold", width=4)
    steps_table.add_column("Étape", style="white")
    for i, step in enumerate(proc["steps"], 1):
        steps_table.add_row(str(i), step)
    console.print(steps_table)

    # Documents
    docs_table = Table(title="Documents Requis", show_lines=True)
    docs_table.add_column("#", style="bold", width=4)
    docs_table.add_column("Document", style="white")
    for i, doc in enumerate(proc["documents_required"], 1):
        docs_table.add_row(str(i), doc)
    console.print(docs_table)


@app.command("search")
def search_procedures_cmd(
    query: str = typer.Argument(help="Terme de recherche"),
    category: Optional[str] = typer.Option(None, "--category", "-c", help="Filtrer par catégorie"),
) -> None:
    """Rechercher des procédures par mot-clé."""
    results = service.find_procedures(query, category)
    if not results:
        console.print(f"[yellow]Aucun résultat pour '{query}'.[/]")
        raise typer.Exit()

    table = Table(title=f"Résultats pour '{query}'", show_lines=True)
    table.add_column("ID", style="dim", width=10)
    table.add_column("Nom", style="bold cyan", min_width=25)
    table.add_column("Catégorie", style="green")
    table.add_column("Description", style="white")

    for proc in results:
        table.add_row(proc["id"], proc["name"], proc["category"], proc["description"])

    console.print(table)


# ─── Contacts ─────────────────────────────────────────────────


@app.command("contacts")
def list_contacts() -> None:
    """Lister tous les contacts des institutions gouvernementales."""
    contacts = service.list_contacts()

    table = Table(title="Annuaire des Institutions Gouvernementales", show_lines=True)
    table.add_column("ID", style="dim", width=12)
    table.add_column("Institution", style="bold cyan", min_width=30)
    table.add_column("Téléphone", style="green")
    table.add_column("Email", style="blue")
    table.add_column("Horaires", style="yellow")

    for contact in contacts:
        table.add_row(
            contact["id"],
            contact["institution"],
            contact["phone"],
            contact["email"],
            contact["hours"],
        )

    console.print(table)


@app.command("contact")
def show_contact(
    contact_id: str = typer.Argument(help="ID du contact (ex: contact-001)"),
) -> None:
    """Afficher les détails d'un contact spécifique."""
    contact = service.get_contact(contact_id)
    if not contact:
        console.print(f"[red]Contact '{contact_id}' non trouvé.[/]")
        raise typer.Exit(code=1)

    panel_content = Text()
    panel_content.append("\nAdresse: ", style="bold")
    panel_content.append(f"{contact['address']}\n", style="white")
    panel_content.append("Téléphone: ", style="bold")
    panel_content.append(f"{contact['phone']}\n", style="green")
    panel_content.append("Email: ", style="bold")
    panel_content.append(f"{contact['email']}\n", style="blue")
    panel_content.append("Horaires: ", style="bold")
    panel_content.append(f"{contact['hours']}\n\n", style="yellow")
    panel_content.append("Services:\n", style="bold")
    for svc in contact["services"]:
        panel_content.append(f"  • {svc}\n", style="cyan")

    console.print(Panel(panel_content, title=f"[bold]{contact['institution']}[/]", border_style="cyan"))


# ─── Rights ───────────────────────────────────────────────────


@app.command("rights")
def list_rights(
    category: Optional[str] = typer.Option(None, "--category", "-c", help="Filtrer par catégorie"),
) -> None:
    """Lister les droits et devoirs des citoyens."""
    rights = service.list_rights(category)
    if not rights:
        console.print("[yellow]Aucun droit trouvé.[/]")
        raise typer.Exit()

    table = Table(title="Droits et Devoirs des Citoyens", show_lines=True)
    table.add_column("Titre", style="bold cyan", min_width=20)
    table.add_column("Article", style="green")
    table.add_column("Catégorie", style="yellow")
    table.add_column("Description", style="white", max_width=50)

    for right in rights:
        table.add_row(right["title"], right["article"], right["category"], right["description"])

    console.print(table)


# ─── FAQ ──────────────────────────────────────────────────────


@app.command("faq")
def list_faq(
    query: Optional[str] = typer.Argument(None, help="Rechercher dans la FAQ"),
) -> None:
    """Consulter la Foire Aux Questions."""
    if query:
        items = service.find_faq(query)
    else:
        items = service.list_faq()

    if not items:
        console.print("[yellow]Aucune question trouvée.[/]")
        raise typer.Exit()

    for item in items:
        console.print(
            Panel(
                f"[bold white]{item['question']}[/]\n\n{item['answer']}",
                title=f"[dim]{item['id']}[/] — [green]{item['category']}[/]",
                border_style="blue",
            )
        )


# ─── Categories ───────────────────────────────────────────────


@app.command("categories")
def list_categories() -> None:
    """Lister toutes les catégories de procédures."""
    categories = service.get_categories()

    table = Table(title="Catégories de Procédures", show_lines=True)
    table.add_column("#", style="bold", width=4)
    table.add_column("Catégorie", style="bold cyan")

    for i, cat in enumerate(categories, 1):
        table.add_row(str(i), cat)

    console.print(table)


# ─── Stats ────────────────────────────────────────────────────


@app.command("stats")
def show_stats() -> None:
    """Afficher les statistiques de la plateforme."""
    stats = service.get_statistics()

    panel_content = Text()
    panel_content.append("\nProcédures: ", style="bold")
    panel_content.append(f"{stats['total_procedures']}\n", style="cyan")
    panel_content.append("Contacts: ", style="bold")
    panel_content.append(f"{stats['total_contacts']}\n", style="green")
    panel_content.append("Droits citoyens: ", style="bold")
    panel_content.append(f"{stats['total_rights']}\n", style="yellow")
    panel_content.append("FAQ: ", style="bold")
    panel_content.append(f"{stats['total_faq']}\n\n", style="magenta")
    panel_content.append("Catégories: ", style="bold")
    panel_content.append(", ".join(stats["categories"]), style="blue")
    panel_content.append("\n")

    console.print(
        Panel(
            panel_content,
            title="[bold]Statistiques de la Plateforme[/]",
            border_style="green",
        )
    )


# ─── About ────────────────────────────────────────────────────


@app.command("about")
def about() -> None:
    """Afficher les informations sur l'application."""
    console.print(
        Panel(
            f"[bold blue]{__app_name__}[/] v{__version__}\n\n"
            "Assistant IA pour les services gouvernementaux\n"
            "de la République Démocratique du Congo.\n\n"
            "[dim]Développé pour faciliter l'accès des citoyens\n"
            "aux informations administratives et gouvernementales.[/]",
            title="[bold]A Propos[/]",
            border_style="blue",
        )
    )

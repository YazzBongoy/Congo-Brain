"""Citizen services CLI commands."""

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

console = Console()
citizen_app = typer.Typer(help="Services Citoyens — Procedures, contacts, droits, FAQ.")


@citizen_app.command("procedures")
def list_procedures(
    category: str = typer.Option(None, "--category", "-c", help="Filtrer par categorie"),
) -> None:
    """Lister les procedures administratives."""
    from congo_brain.core.database import SessionLocal
    from congo_brain.services.citizen_service import CitizenService

    db = SessionLocal()
    try:
        svc = CitizenService(db)
        procs = svc.list_procedures(category)
        if not procs:
            console.print("[yellow]Aucune procedure trouvee.[/]")
            return
        table = Table(title="Procedures Administratives", show_lines=True)
        table.add_column("Code", style="dim")
        table.add_column("Nom", style="bold cyan", min_width=30)
        table.add_column("Categorie", style="green")
        table.add_column("Delai", style="yellow")
        table.add_column("Frais", style="magenta")
        for p in procs:
            table.add_row(
                p.get("code", ""), p.get("name", ""),
                p.get("category", ""),
                p.get("processing_time", ""),
                p.get("fees", ""),
            )
        console.print(table)
    finally:
        db.close()


@citizen_app.command("contacts")
def list_contacts() -> None:
    """Lister les contacts institutionnels."""
    from congo_brain.core.database import SessionLocal
    from congo_brain.services.citizen_service import CitizenService

    db = SessionLocal()
    try:
        svc = CitizenService(db)
        contacts = svc.list_contacts()
        if not contacts:
            console.print("[yellow]Aucun contact trouve.[/]")
            return
        table = Table(title="Contacts Institutionnels", show_lines=True)
        table.add_column("Code", style="dim")
        table.add_column("Institution", style="bold cyan", min_width=30)
        table.add_column("Adresse", style="green")
        table.add_column("Telephone", style="yellow")
        table.add_column("Email", style="blue")
        for c in contacts:
            table.add_row(
                c.get("code", ""), c.get("institution", ""),
                c.get("address", ""), c.get("phone", ""),
                c.get("email", ""),
            )
        console.print(table)
    finally:
        db.close()


@citizen_app.command("rights")
def list_rights(
    category: str = typer.Option(None, "--category", "-c", help="Filtrer par categorie"),
) -> None:
    """Lister les droits des citoyens."""
    from congo_brain.core.database import SessionLocal
    from congo_brain.services.citizen_service import CitizenService

    db = SessionLocal()
    try:
        svc = CitizenService(db)
        rights = svc.list_rights(category)
        if not rights:
            console.print("[yellow]Aucun droit trouve.[/]")
            return
        table = Table(title="Droits des Citoyens", show_lines=True)
        table.add_column("Code", style="dim")
        table.add_column("Titre", style="bold cyan", min_width=30)
        table.add_column("Article", style="green")
        table.add_column("Categorie", style="yellow")
        for r in rights:
            table.add_row(r.get("code", ""), r.get("title", ""), r.get("article", ""), r.get("category", ""))
        console.print(table)
    finally:
        db.close()


@citizen_app.command("faq")
def list_faq() -> None:
    """Afficher la FAQ."""
    from congo_brain.core.database import SessionLocal
    from congo_brain.services.citizen_service import CitizenService

    db = SessionLocal()
    try:
        svc = CitizenService(db)
        items = svc.list_faq()
        if not items:
            console.print("[yellow]Aucune FAQ trouvee.[/]")
            return
        for item in items:
            console.print(Panel(
                f"[bold]{item.get('question', '')}[/]\n\n{item.get('answer', '')}",
                title=f"FAQ - {item.get('category', '')}",
                border_style="cyan",
            ))
    finally:
        db.close()


@citizen_app.command("search")
def search(
    query: str = typer.Argument(..., help="Terme de recherche"),
) -> None:
    """Rechercher dans les services citoyens."""
    from congo_brain.core.database import SessionLocal
    from congo_brain.services.citizen_service import CitizenService

    db = SessionLocal()
    try:
        svc = CitizenService(db)
        procs = svc.search_procedures(query)
        contacts = svc.search_contacts(query)
        rights = svc.search_rights(query)
        faq = svc.search_faq(query)
        total = len(procs) + len(contacts) + len(rights) + len(faq)
        console.print(f"\n[bold]Resultats pour '[cyan]{query}[/]': {total} trouve(s)[/]\n")
        if procs:
            console.print(f"  [green]Procedures:[/] {len(procs)}")
        if contacts:
            console.print(f"  [green]Contacts:[/] {len(contacts)}")
        if rights:
            console.print(f"  [green]Droits:[/] {len(rights)}")
        if faq:
            console.print(f"  [green]FAQ:[/] {len(faq)}")
        if total == 0:
            console.print("[yellow]Aucun resultat.[/]")
    finally:
        db.close()

import shutil
from pathlib import Path
from typing import Optional

import questionary
import typer

app = typer.Typer()

STORIES_DIR = Path(__file__).parent.parent.parent / "stories"


def _list_stories() -> list[Path]:
    if not STORIES_DIR.exists():
        return []
    return sorted(
        p for p in STORIES_DIR.glob("*.md") if p.name != "README.md"
    )


def _find_story(topic: str) -> Path | None:
    for p in _list_stories():
        if p.stem == topic or p.name == topic:
            return p
    return None


@app.callback(invoke_without_command=True)
def learn(
    ctx: typer.Context,
    topic: Optional[str] = typer.Argument(default=None, help="Tema (slug). Omite para seleccionar interactivamente."),
    copy: bool = typer.Option(True, "--copy/--no-copy", help="Copiar markdown al proyecto actual."),
):
    """Muestra tutoriales de configuración externa y los copia al proyecto."""
    if ctx.invoked_subcommand is not None:
        return

    if topic == "list":
        list_stories()
        return

    stories = _list_stories()
    if not stories:
        typer.echo("No hay tutoriales disponibles.")
        raise typer.Exit(1)

    if topic is None:
        selected = questionary.select(
            "¿Qué quieres aprender?",
            choices=[p.stem for p in stories],
        ).ask()
        if selected is None:
            raise typer.Exit(0)
        story = _find_story(selected)
    else:
        story = _find_story(topic)
        if story is None:
            typer.secho(f"Tutorial '{topic}' no encontrado.", fg=typer.colors.RED, err=True)
            typer.echo("Disponibles: " + ", ".join(p.stem for p in stories))
            raise typer.Exit(1)

    typer.echo(story.read_text(encoding="utf-8"))

    if copy:
        dest_dir = Path.cwd() / "learn"
        dest_dir.mkdir(exist_ok=True)
        dest = dest_dir / story.name
        shutil.copy2(story, dest)
        typer.secho(f"\nCopiado → {dest}", fg=typer.colors.GREEN)


@app.command("list")
def list_stories():
    """Lista todos los tutoriales disponibles."""
    stories = _list_stories()
    if not stories:
        typer.echo("No hay tutoriales disponibles.")
        return
    typer.secho("Tutoriales disponibles:", fg=typer.colors.BRIGHT_CYAN)
    for s in stories:
        typer.echo(f"  {s.stem}")

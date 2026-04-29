"""Comandos `spa authorizer ...` — gestión de Lambda Authorizers para modo container."""
from pathlib import Path
from typing import cast

import os
import typer

from ...globals import load_config

app = typer.Typer(help="Gestiona lambda authorizers para deploy en container.")

TEMPLATES_DIR = Path(__file__).resolve().parent.parent.parent / 'templates'
HANDLER_TEMPLATE = TEMPLATES_DIR / 'authorizers' / 'handler.py.txt'


def _normalize_name(name: str) -> str:
    return name.replace("-", "_").replace(" ", "_")


def _render_handler(name: str, app_name: str) -> str:
    text = HANDLER_TEMPLATE.read_text(encoding="utf-8")
    return text.format(authorizer_name=name, app_name=app_name)


def _append_toml_entry(toml_path: Path, name: str, role_name: str, lambda_name: str, module: str) -> bool:
    entry_header = f"[spa.api.lambda-authorizers.{name}]"
    current = toml_path.read_text(encoding="utf-8") if toml_path.exists() else ""
    if entry_header in current:
        return False
    block = (
        f"\n{entry_header}\n"
        f'role_name = "{role_name}"\n'
        f'lambda_name = "{lambda_name}"\n'
        f'module = "{module}"\n'
    )
    if not current.endswith("\n"):
        block = "\n" + block
    toml_path.write_text(current + block, encoding="utf-8")
    return True


@app.command('add')
def add_authorizer(
    name: str = typer.Argument(..., help="Nombre del authorizer (matchea el prefijo del securityScheme)."),
    role_name: str = typer.Option(None, '--role-name', help="Nombre del IAM role. Default: <name>-authorizer-role."),
    lambda_name: str = typer.Option(None, '--lambda-name', help="Nombre de la función Lambda. Default: <name>-authorizer."),
):
    """Genera handler stub en `src/authorizers/<name>/handler.py` y lo registra en spa_project.toml."""
    name = _normalize_name(name)
    if not HANDLER_TEMPLATE.exists():
        typer.echo(f"Template no encontrado: {HANDLER_TEMPLATE}", color=typer.colors.RED)
        raise typer.Abort()

    try:
        config = load_config()
    except Exception:
        typer.echo('No se pudo leer la configuración del proyecto.', color=typer.colors.RED)
        raise typer.Abort()

    app_name = cast(str, config.project.definition.name) or 'spa-app'
    role_name = role_name or f"{name}-authorizer-role"
    lambda_name = lambda_name or f"{name}-authorizer"
    module = f"src.authorizers.{name}.handler"

    target_dir = Path(os.getcwd()) / 'src' / 'authorizers' / name
    target_dir.mkdir(parents=True, exist_ok=True)
    init_file = target_dir.parent / '__init__.py'
    if not init_file.exists():
        init_file.write_text("", encoding="utf-8")
    pkg_init = target_dir / '__init__.py'
    if not pkg_init.exists():
        pkg_init.write_text("", encoding="utf-8")

    handler_path = target_dir / 'handler.py'
    if handler_path.exists():
        typer.echo(f"[skip] {handler_path} ya existe.")
    else:
        handler_path.write_text(_render_handler(name, app_name), encoding="utf-8")
        typer.echo(f"[+] Generado handler: {handler_path}")

    toml_path = Path(os.getcwd()) / 'spa_project.toml'
    added = _append_toml_entry(toml_path, name, role_name, lambda_name, module)
    if added:
        typer.echo(f"[+] Registrado [spa.api.lambda-authorizers.{name}] en {toml_path}")
    else:
        typer.echo(f"[skip] Entry [spa.api.lambda-authorizers.{name}] ya existe en {toml_path}")

    typer.echo(
        f"Listo. Asegúrate que el securityScheme '{name}_authorizer' esté declarado "
        f"en api.yaml para que el bridge lo enlace.",
        color=typer.colors.GREEN,
    )

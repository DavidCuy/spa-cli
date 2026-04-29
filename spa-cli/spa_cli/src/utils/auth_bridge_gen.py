"""Genera `auth_bridge.py` y `auth_bridge.config.json` dentro del build container."""
import json
from pathlib import Path
from shutil import copy2
from typing import cast

import typer

from ...globals import Config

TEMPLATE_PATH = Path(__file__).resolve().parent.parent.parent / 'templates' / 'auth_bridge.py.txt'


def generate_auth_bridge(api_local_dir: Path, project_config: Config) -> None:
    """Copia el bridge runtime a `api_local_dir/auth_bridge.py` y emite el registry.

    El registry es un dict `{authorizer_key: {module, handler, role_name, lambda_name}}`
    serializado a JSON al lado del bridge para que este lo lea en runtime sin
    re-parsear `spa_project.toml`.
    """
    api_local_dir.mkdir(parents=True, exist_ok=True)

    if not TEMPLATE_PATH.exists():
        typer.echo(f"[!] Template auth_bridge no encontrado: {TEMPLATE_PATH}", color=typer.colors.RED)
        return

    bridge_dest = api_local_dir / 'auth_bridge.py'
    copy2(TEMPLATE_PATH, bridge_dest)
    typer.echo(f"Copiado auth_bridge.py → {bridge_dest}")

    registry = {}
    if project_config.api and project_config.api.lambda_authorizers:
        for key, auth in project_config.api.lambda_authorizers.items():
            registry[key] = {
                "module": auth.module,
                "handler": auth.handler or "lambda_handler",
                "role_name": auth.role_name,
                "lambda_name": auth.lambda_name,
            }

    config_dest = api_local_dir / 'auth_bridge.config.json'
    config_dest.write_text(json.dumps(registry, indent=2), encoding="utf-8")
    typer.echo(f"Generado registry de authorizers ({len(registry)}) → {config_dest}")

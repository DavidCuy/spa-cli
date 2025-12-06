import os
import sys
import typer
import signal
import subprocess
import shutil
from pathlib import Path
from .install_local_layers import install_layers
from .build_local_api import build_local_api
from .build_api_json import build_api_json
from ...globals import Config

def on_cancel():
    typer.echo("\n[+] Cancelado por el usuario. Ejecutando limpieza…")
def on_error(code: int):
    typer.echo(f"[!] El servidor terminó con error (código {code}).")

def on_ok():
    typer.echo("[✓] El servidor terminó normalmente.")

def main(project_config: Config, extra_args: list[str] = []):
    lambdas_path = Path(os.getcwd()).joinpath(project_config.project.folders.lambdas)
    api_path = Path(os.getcwd()).joinpath(project_config.project.folders.root).parent.joinpath('api.yaml')
    base_path = Path(os.getcwd()).joinpath(project_config.project.folders.root).parent

    typer.echo('Instalando bibliotecas locales…')
    build_local_api(lambdas_path, base_path)

    typer.echo('Generando definición OpenAPI…')
    build_api_json(api_path, lambdas_path, base_path)
    shutil.copy(Path(__file__).parent / "main_server.py", base_path / "src/api_local/main_server.py")

    # Construir comando base
    cmd = [sys.executable, "-m", "fastapi", "dev", str(base_path / "src/api_local/main_server.py")]

    # Extraer configuraciones de los argumentos para pasarlas como variables de entorno
    server_config = {
        'host': '127.0.0.1',
        'port': '8000',
        'reload': 'true',
        'log_level': 'info',
        'root_path': '',
        'proxy_headers': 'false'
    }

    # Parsear argumentos adicionales
    if extra_args:
        i = 0
        while i < len(extra_args):
            arg = extra_args[i]
            if arg == '--host' and i + 1 < len(extra_args):
                server_config['host'] = extra_args[i + 1]
                i += 2
            elif arg == '--port' and i + 1 < len(extra_args):
                server_config['port'] = extra_args[i + 1]
                i += 2
            elif arg == '--reload':
                server_config['reload'] = 'true'
                i += 1
            elif arg == '--no-reload':
                server_config['reload'] = 'false'
                i += 1
            elif arg == '--log-level' and i + 1 < len(extra_args):
                server_config['log_level'] = extra_args[i + 1]
                i += 2
            elif arg == '--root-path' and i + 1 < len(extra_args):
                server_config['root_path'] = extra_args[i + 1]
                i += 2
            elif arg == '--proxy-headers':
                server_config['proxy_headers'] = 'true'
                i += 1
            elif arg == '--no-proxy-headers':
                server_config['proxy_headers'] = 'false'
                i += 1
            else:
                i += 1

        cmd.extend(extra_args)

    # Preparar variables de entorno
    env = os.environ.copy()
    env['SERVER_HOST'] = server_config['host']
    env['SERVER_PORT'] = server_config['port']
    env['SERVER_RELOAD'] = server_config['reload']
    env['SERVER_LOG_LEVEL'] = server_config['log_level']
    env['SERVER_ROOT_PATH'] = server_config['root_path']
    env['SERVER_PROXY_HEADERS'] = server_config['proxy_headers']

    # Lanzamos el proceso para poder controlarlo en Ctrl+C
    proc = subprocess.Popen(cmd, env=env)

    try:
        proc.wait()  # Espera a que termine
    except KeyboardInterrupt:
        # Usuario presionó Ctrl+C: pedimos al hijo que se cierre y corremos tu bloque
        typer.echo("\n[!] Ctrl+C detectado. Deteniendo servidor…")
        if os.name == "nt":
            # En Windows manda CTRL_BREAK (más fiable que CTRL_C a veces)
            proc.send_signal(signal.CTRL_BREAK_EVENT)
        else:
            proc.send_signal(signal.SIGINT)
        try:
            proc.wait(timeout=10)
        except subprocess.TimeoutExpired:
            proc.kill()
            proc.wait()
        on_cancel()
        return

    # Si no fue KeyboardInterrupt, revisamos cómo terminó
    rc = proc.returncode
    if rc == 0:
        on_ok()
    elif rc < 0 and abs(rc) == signal.SIGINT:
        # Algunos entornos devuelven código negativo si terminó por SIGINT
        on_cancel()
    else:
        on_error(rc)

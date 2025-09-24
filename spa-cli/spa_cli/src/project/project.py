from ...globals import Constants, DRIVERS, load_config
from ..utils.template_gen import generate_project_template, read_project_config
from ..utils.install_local_layers import install_layers

import os
import sys
import json
import typer
from typing import cast
from click.types import Choice
from pathlib import Path
from shutil import which

app = typer.Typer()

@app.command('init')
def init_project(
        pattern_version: str = typer.Option(help='Version del patron.', default='latest')
    ):
    """
    Genera un nuevo proyecto con template
    """
    db_config = {
        "db_engine": None,
        "db_driver": None,
        "secret_name": '',
    }
    project_name = typer.prompt("Nombre del proyecto")
    project_description = typer.prompt("Descripción del proyecto")
    
    author_name = typer.prompt("Nombre del autor", default=os.getlogin())
    author_email = typer.prompt("Email del autor", default="")

    dbChoices = Choice([
        Constants.MYSQL_ENGINE.value,
        Constants.POSTGRESQL_ENGINE.value
    ])
    db_config['db_engine'] = typer.prompt(
        "Elija su motor de base de datos",
        Constants.MYSQL_ENGINE.value,
        show_choices=True,
        type=dbChoices
    )
    
    aws_region = typer.prompt("Región de AWS", default="us-east-1")
    
    db_config['db_driver'] = DRIVERS[Constants.MYSQL_ENGINE.value]
    db_config['secret_name'] = typer.prompt("Escriba el nombre del secreto para las credenciales de la base de datos - Revise la documentación para el formato correcto")
    
    generate_project_template(
        project_name,
        author_name=author_name,
        author_email=author_email,
        **db_config,
        aws_region=aws_region,
        pattern_version=pattern_version,
        project_description=project_description
    )
        
    
    local_project_dir = Path(os.getcwd()).joinpath(project_name).joinpath('.spa')
    if not local_project_dir.exists():
        os.mkdir(local_project_dir)
    
    with open(local_project_dir.joinpath('project.json'), 'w') as f:
        json.dump({
            "project_name": project_name,
            "dbDialect": db_config['db_engine'],
            "pattern_version": pattern_version
        }, f)
    

@app.command('configure')
def read_config():
    try:
        project_config = read_project_config()
    except:
        typer.echo('No se puedo leer la configuracion del proyecto', color=typer.colors.RED)
        raise typer.Abort()
    
    output_str = ""
    for key in project_config.keys():
        output_str += f"{key} = {project_config[key]}\n"
    
    typer.echo(output_str)


@app.command('install')
def install_project():
    try:
        project_config = load_config()
    except:
        typer.echo('No se puedo leer la configuracion del proyecto', color=typer.colors.RED)
        raise typer.Abort()
    python_path = __get_venv_python_path()
    typer.echo('Instalando bibliotecas')
    install_layers(project_config, Path(Path.cwd() / python_path))

@app.command('run')
def run_app(
        method: str = typer.Option(help='Método para levantar la aplicación', default='flask-run'),
        only_project_app: bool = typer.Option(help='Indica si solo se levanta la app usando docker', default=False),
        rebuild_docker: bool = typer.Option(help='Indica si solo se levanta o se construye la app usando docker', default=False)):
    if only_project_app and not (method == 'docker'):
        typer.echo('Solo se puede usar "only-docker-app" seleccionando docker como método de ejecución')
        raise typer.Abort()
    if rebuild_docker and not (method == 'docker'):
        typer.echo('Solo se puede usar "rebuild_docker" seleccionando docker como método de ejecución')
        raise typer.Abort()
    try:
        project_config = read_project_config()
    except:
        typer.echo('No se puedo leer la configuracion del proyecto', color=typer.colors.RED)
        raise typer.Abort()
    if method == 'flask-run':
        python_path = __get_venv_python_path()
        __set_flask_env()

        os.system(f'{python_path} -m flask run --host=0.0.0.0')
    else:
        typer.echo('El método especificado no está permitido [flask-run, docker]')


def __set_flask_env():
    os.environ['FLASK_APP'] = 'api'
    os.environ['FLASK_RUN_HOST'] = '0.0.0.0'
    os.environ['FLASK_ENV'] = 'development'


def __verify_venv():
    if sys.prefix != sys.base_prefix:
        typer.echo('No se reconocio ambiente virtual')
        if not Path.exists(Path(os.getcwd()).joinpath('venv')):
            typer.echo('No se encontró carpeta de ambiente virtual')
            os.system('python -m venv venv')


def __get_venv_python_path():
    __verify_venv()
    return '.\\venv\\Scripts\\python' if sys.platform.lower().startswith('win') else './venv/bin/python'

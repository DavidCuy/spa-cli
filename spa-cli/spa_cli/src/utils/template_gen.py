import os
import json
import typer
from typing import cast
from cookiecutter.main import cookiecutter
from functools import wraps
from typing import Any, Callable, Dict
from pathlib import Path
from ...globals import Constants

def generate_project_template(project_name: str,
                            db_engine: str,
                            db_driver: str,
                            db_host: str,
                            db_port: int,
                            db_user: str,
                            db_pass: str,
                            db_name: str,
                            from_secret: bool = False,
                            secret_name: str = '',
                            pattern_version = 'main'):
    """Descarga y configura el template de patron para flask

    Args:
        project_name (str): Nombre del proyecto
        db_engine (str): Motor de base de datos
        db_driver (str): Driver de base de datos
        db_host (str): Host de base de datos
        db_port (int): Puerto de base de datos
        db_user (str): Usuario de base de datos
        db_pass (str): Contraseña de base de datos
        db_name (str): Nombre de base de datos
        pattern_version (str, optional): Rama o tag de github a utilizar del template. Lates utiliza la rama main.
    """
    config_override = {
        "directory_name": project_name,
        "develop_branch": "main",
        "dbDialect": db_engine,
        "_dbDriver": db_driver,
    }
    if not from_secret:
        config_override.update({
            "db_host": db_host,
            "db_user": db_user,
            "db_pass": db_pass,
            "db_name": db_name,
            "_db_port": db_port
        })
    else:
        config_override.update({
            "from_secret": from_secret,
            "secret_name": secret_name
        })
    cookiecutter_kwargs = {
        "directory": "code",
        "overwrite_if_exists": True,
        "no_input": True,
        "extra_context": config_override
    }
    if pattern_version != 'latest':
        cookiecutter_kwargs.update({"checkout": pattern_version})
    
    template_url = Constants.PROJECT_TEMPLATE.value
    cookiecutter(template_url, **cookiecutter_kwargs)

def add_code_to_module(template_path: Path, module_path: Path, modelName: str, code_format_override: dict):
    module_code = template_path.read_text().format(**code_format_override)
    module_path.joinpath(f'{modelName}.py').write_text(module_code)

def add_file_to_module(module_path: Path, modelName: str, replace_import: str = None):
    module_text = module_path.joinpath('__init__.py').read_text()
    module_text += f"\nfrom .{modelName} import {modelName}" if replace_import is None else f"\nfrom .{modelName} import {replace_import}"
    module_path.joinpath('__init__.py').write_text(module_text)


def read_project_config():
    local_project_dir = Path(os.getcwd()).joinpath('.spa')

    try:
        with open(local_project_dir.joinpath('project.json'), 'r') as f:
            project_config = cast(dict, json.load(f))
    except Exception as e:
        raise e
    
    return project_config



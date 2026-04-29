from importlib.metadata import version as v

import typer
from dotenv import load_dotenv

from .src.project import project
from .src.model import model
from .src.endpoint import endpoint
from .src.lambda_function import lambda_function
from .src.authorizer import authorizer

load_dotenv()

app = typer.Typer()
app.add_typer(project.app, name='project')
# app.add_typer(model.app, name='model')
app.add_typer(endpoint.app, name='endpoint')
app.add_typer(lambda_function.app, name='lambda')
app.add_typer(authorizer.app, name='authorizer')


@app.callback(invoke_without_command=True)
def callback_version(version: bool = False):
    """
    Imprime la versión del CLI.
    """
    if version:
        typer.echo(f'version: {v("spa-cli")}')

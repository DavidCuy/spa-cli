from typing import cast
from pathlib import Path
from .build import get_api_config, get_api_initial_definition
import json
import typer

def build_api_json(api_path: Path, lambdas_path: Path, base_path: Path, output_path: Path = None):
    if output_path is None:
        output_path = base_path / "src/api_local" / "openapi.json"
    api_definition = get_api_initial_definition(api_path)
    _, endpoint_list = get_api_config(lambdas_path)

    for ep in endpoint_list:
        for route_path, methods in ep['definition'].items():
            if route_path in api_definition['paths']:
                # Deep merge — add new methods to existing path without overwriting
                cast(dict, api_definition['paths'][route_path]).update(methods)
            else:
                cast(dict, api_definition['paths'])[route_path] = methods

    with open(output_path, "w+", encoding="utf-8") as f:
        json.dump(api_definition, f, indent=2)

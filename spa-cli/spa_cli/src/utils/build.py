import os
import yaml
from pathlib import Path
from typing import List

def get_lambda_dirs_with_endpoint(base_path: Path) -> List[str]:
    result = []
    if not os.path.exists(base_path):
        raise FileNotFoundError(f"La ruta base no existe: {base_path}")

    for entry in os.listdir(base_path):
        dir_path = os.path.join(base_path, entry)
        endpoint_file = os.path.join(dir_path, "endpoint.yaml")
        if os.path.isdir(dir_path) and os.path.isfile(endpoint_file):
            result.append(entry)

    return result

def get_api_initial_definition(dir_name: Path):
    with open(dir_name, 'r', encoding="utf-8") as f:
        return yaml.safe_load(f)

def get_api_config(lambdas_path: Path):
    endpoint_dirs = get_lambda_dirs_with_endpoint(lambdas_path)
    import_lambdas = []
    endpoint_list = []
    for dir_name in endpoint_dirs:
        import_lambdas.append(f"from src.lambdas.{dir_name}.lambda_function import lambda_handler as {dir_name}_handler")

        with open(Path(lambdas_path / dir_name / "endpoint.yaml"), 'r', encoding="utf-8") as f:
            endpoint_list.append({"definition": yaml.safe_load(f), "name": dir_name})

    return import_lambdas, endpoint_list
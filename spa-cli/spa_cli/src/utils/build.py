import os
import json
import tqdm
import yaml
import typer
from pathlib import Path
from typing import List
from shutil import copytree, copy2
from typing import cast

from ...globals import load_config, Config

DOCKER_TEMPLATES_DIR = Path(__file__).resolve().parent.parent.parent / 'templates' / 'docker'
DOCKER_ARTIFACTS = ('Dockerfile', 'docker-compose.yml', 'entrypoint.sh', '.dockerignore')

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

def build_api_config(lambdas_path: Path, environment: str = None, app_name: str = None, aws_account: str = None, aws_region: str = None):
    endpoint_dirs = get_lambda_dirs_with_endpoint(lambdas_path)
    endpoint_list = []
    for dir_name in endpoint_dirs:

        with open(Path(lambdas_path / dir_name / "endpoint.yaml"), 'r', encoding="utf-8") as f:
            endpoint_node = cast(dict, yaml.safe_load(f))
            for endpoint_name in endpoint_node.keys():
                for method in endpoint_node[endpoint_name]:
                    if 'x-amazon-apigateway-integration' in endpoint_node[endpoint_name][method]:
                        integration = endpoint_node[endpoint_name][method]['x-amazon-apigateway-integration']
                        if 'uri' in integration and environment is not None:
                            integration['uri'] = f'arn:aws:apigateway:{aws_region}:lambda:path/2015-03-31/functions/arn:aws:lambda:{aws_region}:{aws_account}:function:{environment}-{app_name}-{dir_name}/invocations'
                        if 'credentials' in integration and environment is not None:
                            integration['credentials'] = f'arn:aws:iam::{aws_account}:role/{environment}-{app_name}-apigw-invoke-lambda-role'
            endpoint_list.append(endpoint_node)

    return endpoint_list

def build_lambdas(lambdas_path: Path, build_path: Path):
    """
    Copia toda la estructura de src/lambdas a infra/components/lambdas,
    manteniendo la jerarquía de carpetas.
    """

    # Crear destino si no existe
    build_path.mkdir(parents=True, exist_ok=True)

    # Iterar sobre cada subcarpeta dentro de src/lambdas
    for lambda_dir in tqdm.tqdm(lambdas_path.iterdir()):
        if lambda_dir.is_dir():
            target = build_path / lambda_dir.name
            # copytree falla si ya existe el destino → usamos dirs_exist_ok
            copytree(lambda_dir, target, dirs_exist_ok=True)
            typer.echo(f"Copiado {lambda_dir} → {target}")


def build_lambda_stack(build_lambdas_path: Path, environment: str, app_name: str):
    lambdas_init = build_lambdas_path / "__init__.py"

    excluded_dirs = [
        "__pycache__"
    ]

    for lambda_dir in tqdm.tqdm(build_lambdas_path.iterdir()):
        if lambda_dir.is_dir() and lambda_dir.name not in excluded_dirs:
            typer.echo(f"Procesando {lambda_dir.name} para __init__.py")

            lambda_camel_case = lambda_dir.name.replace("-", "_").title().replace("_", "")

            infra_config = ""
            with open(lambdas_init, "r") as f:
                infra_config = f.read()

            with open(lambdas_init, "a") as f:
                header = f"############ Lambda{lambda_camel_case}Stack ############"
                if header in infra_config:
                    typer.echo(f"Sección {header} ya existe en __init__.py, se omite.")
                    continue
                f.write(f"""
        {header}
        from .{lambda_dir.name}.infra_config import Lambda{lambda_camel_case}Stack

        Lambda{lambda_camel_case}Stack(
            name="{environment}-{app_name}-{lambda_camel_case}Stack",
            environment="{environment}",
            app_name="{app_name}",
            lambda_execution_role_arn=lambda_execution_role_arn,
            layers=layers,
            sg_ids=sg_ids,
            subnets_ids=subnets_ids,
            tags=DEFAULT_TAGS
        )\n\n""")

def build_api(api_path: Path, lambdas_path: Path, output_file: Path, build_mode: str = 'serverless'):

    config = load_config()
    api_definition = get_api_initial_definition(api_path)

    environment = os.getenv("ENVIRONMENT") or "dev"
    app_name = os.getenv("APP_NAME") or "myapp"
    aws_account = os.getenv("AWS_ACCOUNT_ID") or "123456789012"
    aws_region = os.getenv("AWS_REGION") or "us-east-1"

    endpoint_list = build_api_config(
        lambdas_path,
        environment=environment,
        app_name=app_name,
        aws_account=aws_account,
        aws_region=aws_region
    )

    for ep in endpoint_list:
        for path_key, methods in ep.items():
            if path_key in api_definition['paths']:
                api_definition['paths'][path_key].update(methods)
            else:
                api_definition['paths'][path_key] = methods

    # Replace authorizer placeholders in securityDefinitions (Swagger 2.0)
    # Support both 'securityDefinitions' (Swagger 2.0) and 'components.securitySchemes' (OpenAPI 3.0) for compatibility
    security_schemes = None
    if 'securityDefinitions' in api_definition:
        security_schemes = api_definition['securityDefinitions']
    elif 'components' in api_definition and 'securitySchemes' in api_definition['components']:
        security_schemes = api_definition['components']['securitySchemes']

    if security_schemes and build_mode != 'container':
        for scheme_name, scheme_config in security_schemes.items():
            if 'x-amazon-apigateway-authorizer' in scheme_config:
                authorizer = scheme_config['x-amazon-apigateway-authorizer']

                # Extract the authorizer key by removing '_authorizer' suffix if present
                authorizer_key = scheme_name.replace('_authorizer', '')

                # Check if there's a custom authorizer configuration for this scheme
                custom_authorizer = None
                if config and config.api and config.api.lambda_authorizers:
                    custom_authorizer = config.api.lambda_authorizers.get(authorizer_key)

                # Replace authorizerUri
                if 'authorizerUri' in authorizer:
                    if custom_authorizer:
                        # Use the lambda_name from configuration
                        lambda_name = custom_authorizer.lambda_name
                        authorizer['authorizerUri'] = f'arn:aws:apigateway:{aws_region}:lambda:path/2015-03-31/functions/arn:aws:lambda:{aws_region}:{aws_account}:function:{environment}-{app_name}-{lambda_name}/invocations'
                    else:
                        # Default behavior for non-configured authorizers
                        authorizer['authorizerUri'] = f'arn:aws:apigateway:{aws_region}:lambda:path/2015-03-31/functions/arn:aws:lambda:{aws_region}:{aws_account}:function:{environment}-{app_name}-authorizer/invocations'

                # Replace authorizerCredentials
                if 'authorizerCredentials' in authorizer:
                    if custom_authorizer:
                        # Use the role_name from configuration
                        role_name = custom_authorizer.role_name
                        authorizer['authorizerCredentials'] = f'arn:aws:iam::{aws_account}:role/{environment}-{app_name}-{role_name}'
                    else:
                        # Default behavior for non-configured authorizers
                        authorizer['authorizerCredentials'] = f'arn:aws:iam::{aws_account}:role/{environment}-{app_name}-authorizer-role'

    with open(output_file, "w+", encoding="utf-8") as f:
        json.dump(api_definition, f, indent=2)


def generate_docker_files(project_root: Path, project_config: Config, force: bool = False):
    """Genera Dockerfile, docker-compose.yml, entrypoint.sh y .dockerignore en project_root."""
    from .template_gen import copy_template_file

    targets = {
        'Dockerfile': DOCKER_TEMPLATES_DIR / 'Dockerfile.txt',
        'docker-compose.yml': DOCKER_TEMPLATES_DIR / 'docker-compose.txt',
        'entrypoint.sh': DOCKER_TEMPLATES_DIR / 'entrypoint.txt',
        '.dockerignore': DOCKER_TEMPLATES_DIR / 'dockerignore.txt',
    }
    overrides = {
        'app_name': project_config.project.definition.name or 'spa-app',
    }

    for filename, template_path in targets.items():
        dest = project_root / filename
        if dest.exists() and not force:
            typer.echo(f"[skip] {filename} ya existe (usa --force para sobreescribir).")
            continue
        if not template_path.exists():
            typer.echo(f"[!] Template no encontrado: {template_path}", color=typer.colors.RED)
            continue
        copy_template_file(template_path, dest, overrides)
        typer.echo(f"[+] Generado: {dest}")


def bake_container_runtime(project_root: Path, build_path: Path, project_config: Config):
    """Prepara dentro de build/ los archivos que el container necesita en runtime:
    src/ (lambdas + layers), src/api_local/{router.py, openapi.json, main_server.py},
    spa_project.toml y api.yaml.
    """
    from .build_local_api import build_local_api
    from .build_api_json import build_api_json

    src_root = project_root / project_config.project.folders.root
    if src_root.exists():
        target_src = build_path / src_root.name
        copytree(src_root, target_src, dirs_exist_ok=True)
        typer.echo(f"Copiado {src_root} → {target_src}")
    else:
        typer.echo(f"[!] No se encontró carpeta de fuentes: {src_root}", color=typer.colors.YELLOW)

    lambdas_path = project_root / project_config.project.folders.lambdas
    api_path = project_root / project_config.project.definition.base_api

    typer.echo('Generando router FastAPI local…')
    build_local_api(lambdas_path, build_path)

    typer.echo('Generando openapi.json para api_local…')
    build_api_json(api_path, lambdas_path, build_path)

    main_server_template = Path(__file__).resolve().parent / 'main_server.py'
    api_local_dir = build_path / 'src' / 'api_local'
    api_local_dir.mkdir(parents=True, exist_ok=True)
    copy2(main_server_template, api_local_dir / 'main_server.py')
    typer.echo(f"Copiado main_server.py → {api_local_dir}")

    typer.echo('Generando auth_bridge.py …')
    from .auth_bridge_gen import generate_auth_bridge
    generate_auth_bridge(api_local_dir, project_config)

    authorizers_path = project_root / 'src' / 'authorizers'
    if authorizers_path.exists():
        target_auth = build_path / 'src' / 'authorizers'
        copytree(authorizers_path, target_auth, dirs_exist_ok=True)
        typer.echo(f"Copiado {authorizers_path} → {target_auth}")

    legacy_auth = project_root / 'infra' / 'components' / 'authorizers'
    if legacy_auth.exists():
        target_legacy = build_path / 'infra' / 'components' / 'authorizers'
        copytree(legacy_auth, target_legacy, dirs_exist_ok=True)
        typer.echo(f"Copiado authorizers legacy → {target_legacy}")

    for filename in ('spa_project.toml', 'api.yaml'):
        src = project_root / filename
        if src.exists():
            copy2(src, build_path / filename)
            typer.echo(f"Copiado {filename} → {build_path}")


def copy_container_artifacts(project_root: Path, build_path: Path):
    """Copia Dockerfile / docker-compose.yml / entrypoint.sh / .dockerignore desde la raíz del
    proyecto al build_path. Si faltan, sugiere correr `spa project docker-init`.
    """
    missing = []
    for filename in DOCKER_ARTIFACTS:
        src = project_root / filename
        if not src.exists():
            missing.append(filename)
            continue
        copy2(src, build_path / filename)
        typer.echo(f"Copiado {filename} → {build_path}")

    if missing:
        typer.echo(
            f"[!] Faltan archivos en la raíz del proyecto: {', '.join(missing)}. "
            f"Ejecuta `spa project docker-init` para generarlos.",
            color=typer.colors.YELLOW,
        )

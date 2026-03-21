# spa-cli — Documentación para Agentes de IA

> Este documento está optimizado para ser consumido por modelos de lenguaje (LLMs). Describe el proyecto, sus capacidades, su estructura interna y las operaciones que un agente puede ejecutar mediante prompts.

---

## 1. ¿Qué es spa-cli?

`spa-cli` es una herramienta de línea de comandos (CLI) para Python que automatiza la creación y gestión de proyectos serverless en **AWS Lambda** con **Pulumi** como infraestructura como código (IaC).

**Problema que resuelve:** Un desarrollador que quiere publicar una función Lambda en AWS debe gestionar manualmente capas (layers), ARNs, archivos de infraestructura, definiciones OpenAPI y configuración de API Gateway. spa-cli elimina esa fricción con comandos simples.

**Stack generado:** Python 3.11+ · FastAPI (local) · AWS Lambda · API Gateway · Pulumi · MySQL/PostgreSQL

**Binarios disponibles después de `pip install spa-cli`:**
- `spa` (alias principal)
- `spa-cli` (alias alternativo)

---

## 2. Árbol de comandos

```
spa
├── --version                    # Muestra versión instalada
├── project
│   ├── init                     # Crea un proyecto nuevo (interactivo)
│   ├── install                  # Instala layers locales como paquete pip
│   ├── run-api                  # Levanta servidor FastAPI local (simula Lambda)
│   └── build                    # Empaqueta proyecto para deployment en AWS
├── endpoint
│   └── add                      # Crea endpoint HTTP + Lambda asociada
└── lambda
    └── add                      # Crea Lambda standalone (sin HTTP)
```

> **Nota:** El grupo `model` existe en el código fuente pero está **deshabilitado** (comentado en `cli.py`). No ejecutar.

---

## 3. Prerequisitos del entorno

| Requisito | Motivo |
|-----------|--------|
| Python ≥ 3.11 | Versión mínima de runtime |
| pip / Poetry | Gestión de dependencias |
| Ejecutar comandos dentro del directorio raíz del proyecto | `load_config()` busca `spa_project.toml` en `Path.cwd()` |
| Archivo `spa_project.toml` presente | Todos los comandos excepto `init` lo requieren |
| Variables de entorno AWS para `build` | `ENVIRONMENT`, `APP_NAME`, `AWS_ACCOUNT_ID`, `AWS_REGION` |

---

## 4. Operaciones disponibles (prompt → comando)

Cada operación incluye: propósito, comando exacto, parámetros, restricciones, archivos afectados y salida esperada.

---

### 4.1 `spa project init` — Crear proyecto nuevo

**Cuándo usarlo:** El usuario quiere iniciar un proyecto serverless desde cero.

**Comando:**
```bash
spa project init
# Opcional: especificar versión del template
spa project init --pattern-version v2.0.0
```

**Parámetros CLI:**
| Parámetro | Tipo | Default | Descripción |
|-----------|------|---------|-------------|
| `--pattern-version` | string | `latest` | Rama o tag del repositorio template en GitHub |

**Prompts interactivos (en orden):**
1. `Nombre del proyecto` — Nombre del directorio a crear (sin espacios)
2. `Descripción del proyecto` — Descripción libre
3. `Nombre del autor` — Default: usuario del SO (`os.getlogin()`)
4. `Email del autor` — Default: vacío
5. `Elija su motor de base de datos [mysql/postgresql]` — Default: `mysql`
6. `Región de AWS` — Default: `us-east-1`
7. `Escriba el nombre del secreto para las credenciales de la base de datos` — Nombre en AWS Secrets Manager

**Restricciones:**
- Solo soporta `mysql` y `postgresql` como motores
- El driver se asigna automáticamente: `mysql` → `pymysql`, `postgresql` → `psycopg2`
- Descarga el template desde `https://github.com/DavidCuy/serverless-python-application-pattern.git`
- `pattern_version='latest'` usa la rama `main`; cualquier otro valor usa ese tag/rama como `checkout`

**Archivos/directorios generados:**
```
{nombre_proyecto}/
├── src/
│   ├── layers/
│   │   ├── databases/python/core_db/   # ORM y modelos DB
│   │   └── core/python/core_http/      # Utilidades HTTP
│   ├── lambdas/                        # Funciones Lambda
│   └── infra/                          # Código Pulumi
├── .spa/
│   ├── templates/                      # Plantillas de código
│   └── project.json                    # Metadatos del proyecto
├── api.yaml                            # Definición OpenAPI base
├── spa_project.toml                    # Configuración spa-cli
└── pyproject.toml
```

**`.spa/project.json` generado:**
```json
{
  "project_name": "nombre_proyecto",
  "dbDialect": "mysql",
  "pattern_version": "latest"
}
```

---

### 4.2 `spa project install` — Instalar layers localmente

**Cuándo usarlo:** Primera vez que se trabaja en el proyecto o cuando cambian dependencias en `src/layers/`. Necesario antes de `run-api`.

**Comando:**
```bash
cd {directorio_proyecto}
spa project install
```

**Sin parámetros CLI.**

**Qué hace internamente:**
1. Lee `spa_project.toml`
2. Descubre todas las subcarpetas en `src/layers/*/python/` (excluyendo `__pycache__`)
3. Genera un paquete pip temporal en `./tmp/` con `setup.py`, `README.md`, `LICENSE`
4. Ejecuta `python setup.py sdist bdist_wheel`
5. Desinstala la versión anterior de `layers-extras` si existe
6. Instala el wheel generado con `pip install`
7. Elimina el directorio `./tmp/`

**Salida esperada:**
```
[cmd] pip install setuptools wheel
[cmd] python setup.py sdist bdist_wheel
[cmd] pip uninstall -y layers-extras
[cmd] pip install dist/layers_extras-1.0.0-py3-none-any.whl
Se han instalado las siguientes layers: ['databases', 'core']
```

**Restricciones:**
- Debe ejecutarse desde el directorio raíz del proyecto (donde está `spa_project.toml`)
- Requiere `src/layers/` con la estructura generada por `init`

---

### 4.3 `spa project run-api` — Servidor local de desarrollo

**Cuándo usarlo:** Para probar endpoints localmente sin hacer deploy a AWS.

**Comandos de ejemplo:**
```bash
# Básico (127.0.0.1:8000 con reload)
spa project run-api

# Puerto y host personalizados
spa project run-api --host 0.0.0.0 --port 8080

# Con logs detallados y reload
spa project run-api --reload --log-level debug

# Sin reload, para staging local
spa project run-api --host 0.0.0.0 --port 9000 --no-reload

# Con proxy headers (detrás de nginx/ALB)
spa project run-api --proxy-headers --root-path /api
```

**Parámetros CLI:**
| Parámetro | Tipo | Default | Descripción |
|-----------|------|---------|-------------|
| `--host` | string | `127.0.0.1` | Host de escucha |
| `--port` | integer | `8000` | Puerto de escucha |
| `--reload / --no-reload` | flag | `reload` activo | Auto-reload al cambiar código |
| `--log-level` | string | `info` | `critical`, `error`, `warning`, `info`, `debug`, `trace` |
| `--root-path` | string | `""` | Path raíz de la app (útil con proxy) |
| `--proxy-headers / --no-proxy-headers` | flag | `no-proxy-headers` | Headers X-Forwarded-For |

**Qué hace internamente:**
1. Lee `spa_project.toml`
2. Ejecuta `build_local_api()`: genera `src/api_local/router.py` con rutas FastAPI creadas a partir de cada `endpoint.yaml` en `src/lambdas/`
3. Ejecuta `build_api_json()`: genera `src/api_local/openapi.json` combinando `api.yaml` con los endpoints
4. Copia `main_server.py` a `src/api_local/main_server.py`
5. Lanza `python -m fastapi dev src/api_local/main_server.py [args]` como subprocess
6. Expone cada Lambda como una ruta FastAPI que construye un evento Lambda v2.0 y llama al `lambda_handler`

**Variables de entorno inyectadas al proceso:**
```
SERVER_HOST, SERVER_PORT, SERVER_RELOAD, SERVER_LOG_LEVEL,
SERVER_ROOT_PATH, SERVER_PROXY_HEADERS
```

**Estructura de rutas generadas:**
- Prefix: `/{ENVIRONMENT}` (default `dev` si no hay `ENVIRONMENT` env var)
- Endpoint raíz: `GET /` → retorna configuración del servidor

**Respuesta del endpoint raíz:**
```json
{
  "Message": "Api deployed",
  "Configuration": {
    "environment": "dev",
    "server": { "host": "127.0.0.1", "port": "8000", "reload": true, "log_level": "info" },
    "api": { "prefix": "/dev", "docs_url": "/docs", "openapi_url": "/openapi.json" }
  }
}
```

**Documentación interactiva disponible en:**
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`
- OpenAPI JSON: `http://localhost:8000/openapi.json`

**Detener el servidor:** `Ctrl+C` (maneja limpieza automáticamente en Windows y Unix)

---

### 4.4 `spa project build` — Construir para deployment

**Cuándo usarlo:** Antes de hacer deploy a AWS con Pulumi.

**Comando:**
```bash
# Con variables de entorno para AWS
export ENVIRONMENT=prod
export APP_NAME=mi-api
export AWS_ACCOUNT_ID=123456789012
export AWS_REGION=us-east-1
spa project build
```

**Sin parámetros CLI requeridos** (usa variables de entorno).

**Variables de entorno relevantes:**
| Variable | Default | Descripción |
|----------|---------|-------------|
| `ENVIRONMENT` | `dev` | Prefijo de entorno para nombres AWS |
| `APP_NAME` | valor de `spa_project.toml` → `definition.name` | Nombre base de la app |
| `AWS_ACCOUNT_ID` | `123456789012` | ID de cuenta AWS |
| `AWS_REGION` | `us-east-1` | Región AWS |

**Qué hace internamente (en orden):**
1. Limpia `build/` si existe
2. Crea `build/`
3. Copia `infra/` → `build/infra/`
4. Copia archivos `Pulumi.*` → `build/`
5. Copia `pyproject.toml` → `build/`
6. **Build layers:** copia `src/layers/` → `build/tmp_build_layer/` y ejecuta `pip install -r requirements.txt -t {layer_path}` por cada layer
7. **Build lambdas:** copia `src/lambdas/` → `build/infra/components/lambdas/`
8. **Build lambda stack:** por cada lambda, agrega a `build/infra/components/lambdas/__init__.py` el código de instanciación Pulumi del stack
9. **Build API:** combina `api.yaml` con cada `endpoint.yaml` de las lambdas, inyecta ARNs reales, reemplaza placeholders de Lambda Authorizers, guarda como `build/infra/components/openapi.json`

**Estructura de `build/` generada:**
```
build/
├── infra/
│   └── components/
│       ├── lambdas/
│       │   ├── __init__.py          # Stack Pulumi con todas las Lambdas
│       │   ├── {lambda_name}/
│       │   │   ├── lambda_function.py
│       │   │   ├── infra_config.py
│       │   │   └── endpoint.yaml (si aplica)
│       │   └── ...
│       └── openapi.json             # Definición OpenAPI con ARNs reales
├── tmp_build_layer/
│   └── {layer_name}/python/         # Layer con deps instaladas
├── Pulumi.yaml
├── Pulumi.{stack}.yaml
└── pyproject.toml
```

**Formato de ARNs generados para endpoints:**
```
arn:aws:apigateway:{AWS_REGION}:lambda:path/2015-03-31/functions/arn:aws:lambda:{AWS_REGION}:{AWS_ACCOUNT_ID}:function:{ENVIRONMENT}-{APP_NAME}-{lambda_name}/invocations
```

**Salida esperada:**
```
Construyendo proyecto
Deleted directory: /ruta/build
Building layers from src/layers into build/tmp_build_layer...
Building lambdas from src/lambdas...
Building lambda stack...
Building API definition...
Build completed.
```

---

### 4.5 `spa endpoint add` — Crear endpoint HTTP con Lambda

**Cuándo usarlo:** Para exponer una función Lambda como endpoint REST en API Gateway.

**Comando:**
```bash
spa endpoint add --method METHOD --path PATH --endpoint-name NAME
```

**Parámetros CLI:**
| Parámetro | Tipo | Requerido | Descripción |
|-----------|------|-----------|-------------|
| `--method` | string | ✅ | Método HTTP: `GET`, `POST`, `PUT`, `PATCH`, `DELETE` |
| `--path` | string | ✅ | Ruta REST (ej: `/usuarios`, `/usuarios/{id}`) |
| `--endpoint-name` | string | ✅ | Nombre de la Lambda (se normaliza a snake_case) |

**Normalización de nombres:**
- Espacios → `_`
- Guiones (`-`) → `_`
- Ejemplo: `"crear-usuario nuevo"` → `crear_usuario_nuevo`

**Conversión a CamelCase:** `listar_usuarios` → `ListarUsuarios` (usado en `infra_config.py` y tests)

**Restricciones:**
- El `endpoint-name` debe ser único dentro de `src/lambdas/` (es el nombre de directorio)
- Métodos válidos: `GET`, `POST`, `PUT`, `PATCH`, `DELETE`
- Parámetros de ruta soportados: `{id}`, `{usuario_id}`, etc.
- Debe ejecutarse desde el directorio raíz del proyecto

**Archivos generados en `src/lambdas/{endpoint_name}/`:**
```
src/lambdas/{endpoint_name}/
├── lambda_function.py       # Handler Lambda (editar para lógica de negocio)
├── test_lambda_function.py  # Tests unitarios
├── infra_config.py          # Configuración Pulumi del stack Lambda
└── endpoint.yaml            # Definición OpenAPI del endpoint
```

**Contenido de `endpoint.yaml` generado:**
```yaml
/{path}:
  {method}:
    x-amazon-apigateway-integration:
      # ... configuración API Gateway
```

**Ejemplos de uso comunes:**

```bash
# CRUD completo para una entidad
spa endpoint add --method GET    --path /usuarios          --endpoint-name listar_usuarios
spa endpoint add --method POST   --path /usuarios          --endpoint-name crear_usuario
spa endpoint add --method GET    --path /usuarios/{id}     --endpoint-name obtener_usuario
spa endpoint add --method PUT    --path /usuarios/{id}     --endpoint-name actualizar_usuario
spa endpoint add --method DELETE --path /usuarios/{id}     --endpoint-name eliminar_usuario

# Con ruta anidada
spa endpoint add --method GET --path /usuarios/{uid}/pedidos/{pid} --endpoint-name obtener_pedido_usuario
```

**Salida esperada:**
```
La ruta /usuarios [POST] se agrego correctamente!
```

**Error más común:**
```
Ya existe una ruta con nombre: listar_usuarios
```
→ Cada `endpoint-name` debe ser único. Usar nombre diferente.

---

### 4.6 `spa lambda add` — Crear Lambda standalone

**Cuándo usarlo:** Para tareas en background (SQS, CloudWatch Events, S3 triggers, DynamoDB Streams) que NO requieren un endpoint HTTP.

**Diferencia clave con `endpoint add`:** No genera `endpoint.yaml`, por lo tanto esta Lambda no aparece en API Gateway ni es accesible vía HTTP.

**Comando:**
```bash
spa lambda add --lambda-name NAME
```

**Parámetros CLI:**
| Parámetro | Tipo | Requerido | Descripción |
|-----------|------|-----------|-------------|
| `--lambda-name` | string | ✅ | Nombre de la función Lambda |

**Mismas reglas de normalización** que `endpoint add` (espacios y guiones → `_`).

**Archivos generados en `src/lambdas/{lambda_name}/`:**
```
src/lambdas/{lambda_name}/
├── lambda_function.py       # Handler Lambda
├── test_lambda_function.py  # Tests unitarios
└── infra_config.py          # Configuración Pulumi del stack Lambda
```

**Casos de uso típicos:**
```bash
spa lambda add --lambda-name procesar_cola_sqs
spa lambda add --lambda-name enviar_notificaciones_push
spa lambda add --lambda-name limpiar_cache_diario
spa lambda add --lambda-name procesar_imagenes_s3
spa lambda add --lambda-name sincronizar_base_datos
```

**Salida esperada:**
```
La lambda procesar_cola_sqs se agrego correctamente!
```

---

## 5. Archivo de configuración `spa_project.toml`

Archivo TOML en la raíz del proyecto. Si no existe, `load_config()` lo crea con valores por defecto.

**Estructura completa:**
```toml
[spa.project.definition]
name = "nombre-proyecto"
description = "Descripción"
author = "Nombre Autor"
author_email = "email@ejemplo.com"
base_api = "api.yaml"              # Ruta a la definición OpenAPI base

[spa.template.files]
model       = ".spa/templates/models/model.txt"
service     = ".spa/templates/models/service.txt"
controller  = ".spa/templates/models/controller.txt"
endpoint    = ".spa/templates/lambda_endpoint.txt"
lambda_function = ".spa/templates/lambda.txt"
test_lambda = ".spa/templates/test_lambda_function.txt"
lambda_conf = ".spa/templates/lambda_conf.txt"

[spa.project.folders]
root        = "src"
models      = "src/layers/databases/python/core_db/models"
services    = "src/layers/databases/python/core_db/services"
controllers = "src/layers/core/python/core_http/controllers"
lambdas     = "src/lambdas"
layers      = "src/layers"
jsons       = ".spa/templates/json"

# Lambda Authorizers (opcional)
[spa.api.lambda-authorizers.{clave}]
role_name   = "nombre-rol-iam"
lambda_name = "nombre-lambda-auth"
```

---

## 6. Lambda Authorizers — Configuración avanzada

Permite configurar múltiples Lambda Authorizers para API Gateway.

**Convención de nombres (crítica):**
- En `api.yaml` el security scheme se llama `{clave}_authorizer`
- En `spa_project.toml` la sección es `[spa.api.lambda-authorizers.{clave}]`
- Ejemplo: scheme `custom1_authorizer` → clave `custom1`

**Ejemplo en `spa_project.toml`:**
```toml
[spa.api.lambda-authorizers.custom1]
role_name   = "custom-auth-role"
lambda_name = "custom-auth"

[spa.api.lambda-authorizers.admin]
role_name   = "admin-auth-role"
lambda_name = "admin-auth"
```

**Ejemplo en `api.yaml`:**
```yaml
components:
  securitySchemes:
    custom1_authorizer:
      type: apiKey
      name: Authorization
      in: header
      x-amazon-apigateway-authorizer:
        type: token
        authorizerUri: PLACEHOLDER
        authorizerCredentials: PLACEHOLDER
```

**ARNs generados por `spa project build`:**
```
authorizerUri:         arn:aws:apigateway:{region}:lambda:path/.../function:{ENVIRONMENT}-{APP_NAME}-{lambda_name}/invocations
authorizerCredentials: arn:aws:iam::{account}:role/{ENVIRONMENT}-{APP_NAME}-{role_name}
```

**Comportamiento sin configuración:** Si un security scheme no tiene entrada en `spa_project.toml`, el build usa el nombre genérico `{env}-{app}-authorizer`.

---

## 7. Flujos completos de trabajo

### Flujo 1: Nuevo proyecto desde cero

```bash
# 1. Instalar CLI
pip install spa-cli

# 2. Crear proyecto (responder prompts interactivos)
spa project init

# 3. Entrar al proyecto
cd {nombre_proyecto}

# 4. Instalar layers locales
spa project install

# 5. Agregar endpoints
spa endpoint add --method GET  --path /items      --endpoint-name listar_items
spa endpoint add --method POST --path /items      --endpoint-name crear_item
spa endpoint add --method GET  --path /items/{id} --endpoint-name obtener_item

# 6. Agregar lambdas background
spa lambda add --lambda-name procesar_cola

# 7. Desarrollar (editar src/lambdas/*/lambda_function.py)

# 8. Probar localmente
spa project run-api

# 9. Build para AWS
export ENVIRONMENT=prod APP_NAME=mi-api AWS_ACCOUNT_ID=123456789012 AWS_REGION=us-east-1
spa project build

# 10. Deploy con Pulumi (fuera del scope del CLI)
cd build && pulumi up
```

### Flujo 2: Agregar funcionalidad a proyecto existente

```bash
cd {directorio_proyecto}

# Agregar nuevo endpoint
spa endpoint add --method POST --path /pagos --endpoint-name procesar_pago

# Editar lógica en src/lambdas/procesar_pago/lambda_function.py

# Probar
spa project run-api

# Rebuild
spa project build
```

---

## 8. Estructura interna del CLI (para modificaciones)

```
spa-cli/spa_cli/
├── cli.py                    # Registro de grupos Typer
├── globals.py                # Config dataclasses + load_config()
├── __main__.py
└── src/
    ├── project/project.py    # Comandos: init, install, run-api, build
    ├── endpoint/endpoint.py  # Comando: add (con endpoint.yaml)
    ├── lambda_function/lambda_function.py  # Comando: add (sin endpoint.yaml)
    ├── model/                # Deshabilitado
    └── utils/
        ├── build.py          # Lógica build: layers, lambdas, openapi
        ├── build_local_api.py # Genera router.py FastAPI dinámico
        ├── build_api_json.py  # Genera openapi.json local
        ├── up_local_server.py # Lanza subprocess FastAPI dev
        ├── install_local_layers.py # Empaqueta e instala layers como pip
        ├── main_server.py     # Template FastAPI copiado al proyecto
        ├── template_gen.py    # cookiecutter + copy_template_file
        ├── folders.py         # Utilidades de paths
        └── strings.py         # camel_case(), etc.
```

**Clase Config (globals.py):**
```python
Config
├── project: Project
│   ├── definition: Definition (name, description, author, author_email, base_api)
│   └── folders: Folders (models, services, controllers, lambdas, layers, root, jsons)
├── template: Template
│   └── files: Files (model, service, controller, endpoint, lambda_function, test_lambda, lambda_conf)
└── api: Api | None
    └── lambda_authorizers: dict[str, LambdaAuthorizer(role_name, lambda_name)]
```

---

## 9. Errores comunes y soluciones

| Error | Causa | Solución |
|-------|-------|----------|
| `No se puedo leer la configuracion del proyecto` | No hay `spa_project.toml` en `cwd` | Ejecutar desde directorio raíz del proyecto o correr `spa project init` |
| `Ya existe una ruta con nombre: {name}` | `src/lambdas/{name}/` ya existe | Usar un nombre de endpoint/lambda diferente |
| `La lambda no debe contener espacios o guiones` | Advertencia, no error | El nombre se normaliza automáticamente a `_` |
| ARNs incorrectos en build | Variables de entorno no definidas | Definir `ENVIRONMENT`, `APP_NAME`, `AWS_ACCOUNT_ID`, `AWS_REGION` |
| `AttributeError: lambda_name` en authorizers | Config antigua con `lambda_placeholder` | Migrar a `lambda_name` / `role_name` en `spa_project.toml` |
| `El servidor terminó con error` | Puerto en uso o error en lambda_function.py | Verificar puerto libre; revisar errores de importación en handlers |

---

## 10. Ejemplos de prompts para un agente

Los siguientes prompts representan instrucciones típicas que un agente puede recibir y ejecutar con este CLI:

| Prompt del usuario | Comando a ejecutar |
|--------------------|-------------------|
| "Crea un proyecto serverless llamado user-api con MySQL" | `spa project init` (responder prompts: nombre=user-api, db=mysql) |
| "Instala las dependencias del proyecto" | `spa project install` |
| "Agrega un endpoint GET /productos que liste productos" | `spa endpoint add --method GET --path /productos --endpoint-name listar_productos` |
| "Crea un CRUD completo para la entidad Pedido" | 5 comandos `endpoint add` con GET/POST/GET{id}/PUT{id}/DELETE{id} |
| "Agrega una lambda para procesar mensajes SQS de facturación" | `spa lambda add --lambda-name procesar_facturas_sqs` |
| "Levanta el servidor local en el puerto 9000" | `spa project run-api --host 0.0.0.0 --port 9000` |
| "Construye el proyecto para producción en us-west-2" | `export ENVIRONMENT=prod AWS_REGION=us-west-2 ... && spa project build` |
| "¿Qué versión de spa-cli está instalada?" | `spa --version` |

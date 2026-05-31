# spa-cli

**Una herramienta CLI para manejar proyectos serverless en AWS con Python**

spa-cli es una herramienta de línea de comandos que facilita la creación, desarrollo y deployment de aplicaciones serverless en AWS utilizando Python. Proporciona comandos intuitivos para generar proyectos, crear endpoints, funciones Lambda y gestionar la configuración de la infraestructura.

## Instalación

```bash
pip install spa-cli
```

## Comandos Principales

### Comandos del Proyecto (`spa project`)

#### `spa project init`

Crea un nuevo proyecto serverless con el patrón definido.

**Descripción:** Este comando inicializa un nuevo proyecto siguiendo el patrón serverless-python-application-pattern. Te guiará a través de la configuración inicial del proyecto incluyendo la selección de base de datos, región AWS y configuración del autor.

```bash
spa project init
```

**Ejemplo de uso:**
```bash
$ spa project init
Nombre del proyecto: mi-proyecto-serverless
Descripción del proyecto: API REST para gestionar usuarios
Nombre del autor: Juan Pérez
Email del autor: juan@ejemplo.com
Elija su motor de base de datos [mysql/postgresql]: mysql
Región de AWS [us-east-1]: 
Escriba el nombre del secreto para las credenciales de la base de datos: db-credentials
```

#### `spa project install`

Instala las capas locales del proyecto, incluyendo dependencias y configuración necesaria.

**Descripción:** Configura e instala las capas (layers) locales del proyecto, incluyendo dependencias de Python y configuración específica para el entorno de desarrollo.

```bash
spa project install
```

#### `spa project run-api`

Ejecuta un servidor local para desarrollo y pruebas de la API.

**Descripción:** Inicia un servidor HTTP local que simula el comportamiento de las funciones Lambda, permitiendo desarrollo y pruebas sin necesidad de desplegar en AWS. El servidor utiliza FastAPI y Uvicorn con soporte completo para auto-reload durante el desarrollo.

```bash
spa project run-api
```

**Opciones disponibles:**

- `--host TEXT` - Host para el servidor (default: 127.0.0.1)
- `--port INTEGER` - Puerto para el servidor (default: 8000)
- `--reload / --no-reload` - Habilitar auto-reload en cambios de código (default: habilitado)
- `--log-level TEXT` - Nivel de log: critical, error, warning, info, debug, trace (default: info)
- `--root-path TEXT` - Path raíz para la aplicación
- `--proxy-headers / --no-proxy-headers` - Habilitar headers de proxy (X-Forwarded-For, etc.)

**Ejemplos de uso:**

```bash
# Servidor básico en puerto por defecto
spa project run-api

# Servidor en host y puerto específicos
spa project run-api --host 0.0.0.0 --port 8080

# Servidor con auto-reload y logs detallados
spa project run-api --reload --log-level debug

# Servidor sin auto-reload para producción local
spa project run-api --host 0.0.0.0 --port 9000 --no-reload

# Servidor con configuración de proxy
spa project run-api --proxy-headers --root-path /api
```

**Ejemplo de salida:**
```
Iniciando servidor local
Generando definición OpenAPI…

INFO:     Will watch for changes in these directories: ['/ruta/proyecto']
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [12345] using WatchFiles
INFO:     Started server process [12346]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

**Endpoint raíz:**

Al acceder a `http://localhost:8000/` obtendrás información de configuración del servidor:

```json
{
  "Message": "Api deployed",
  "Configuration": {
    "environment": "v1",
    "server": {
      "host": "127.0.0.1",
      "port": "8000",
      "reload": true,
      "log_level": "info",
      "root_path": "",
      "proxy_headers": false
    },
    "request": {
      "client_host": "127.0.0.1",
      "base_url": "http://localhost:8000/",
      "url": "http://localhost:8000/"
    },
    "api": {
      "prefix": "/v1",
      "openapi_url": "/openapi.json",
      "docs_url": "/docs",
      "redoc_url": "/redoc"
    }
  }
}
```

#### `spa project build`

Construye el proyecto para deployment, generando los archivos necesarios y preparando la infraestructura.

**Descripción:** Compila el proyecto creando los archivos de deployment necesarios, construye las capas (layers), genera las funciones Lambda y crea la configuración de la API.

```bash
spa project build
```

**Ejemplo de salida:**
```
Construyendo proyecto
Building layers from src/layers into build/tmp_build_layer...
Building lambdas from src/lambdas...
Building lambda stack...
Building API definition...
Build completed.
```

### Comandos de Endpoints (`spa endpoint`)

#### `spa endpoint add`

Agrega un nuevo endpoint a la API.

**Descripción:** Crea un nuevo endpoint HTTP con su correspondiente función Lambda. Genera automáticamente el handler de la función, archivos de configuración de infraestructura y archivos de prueba.

```bash
spa endpoint add --method POST --path /usuarios --endpoint-name crear_usuario
```

**Parámetros:**
- `--method`: Método HTTP (GET, POST, PUT, PATCH, DELETE)
- `--path`: Ruta del endpoint
- `--endpoint-name`: Nombre de la función Lambda

**Ejemplo de uso:**
```bash
spa endpoint add --method GET --path /usuarios --endpoint-name listar_usuarios
spa endpoint add --method POST --path /usuarios --endpoint-name crear_usuario
spa endpoint add --method PUT --path /usuarios/{id} --endpoint-name actualizar_usuario
```

### Comandos de Lambda (`spa lambda`)

#### `spa lambda add`

Crea una nueva función Lambda sin endpoint HTTP asociado.

**Descripción:** Genera una nueva función Lambda para procesamiento de background, procesamiento de colas SQS, eventos CloudWatch, etc.

```bash
spa lambda add --lambda-name procesar_datos
```

**Parámetros:**
- `--lambda-name`: Nombre de la función Lambda

**Ejemplo de uso:**
```bash
spa lambda add --lambda-name procesar_facturas
spa lambda add --lambda-name enviar_notificaciones
```

### Comando de Versión

#### Ver la versión

```bash
spa --version
spa-cli --version
```

Muestra la versión actual de spa-cli instalada.

## Comandos No Disponibles

### Comandos de Modelo (`spa model`) - 🔒 **No Habilitado Actualmente**

Los comandos para gestionar modelos de base de datos están implementados pero no habilitados en la versión actual. Estos comandos estarán disponibles en futuras versiones:

- `spa model new` - Crear nuevos modelos de datos
- `spa model fromJson` - Crear modelos desde archivos JSON

## Estructura del Proyecto

Después de ejecutar `spa project init`, se genera la siguiente estructura:

```
mi-proyecto-serverless/
├── src/
│   ├── layers/               # Capas Lambda
│   │   ├── databases/       # Acceso a base de datos
│   │   └── core/           # Funciones centrales
│   ├── lambdas/            # Funciones Lambda
│   │   └── [nombre-lambda]/
│   │       ├── lambda_function.py
│   │       ├── test_lambda_function.py
│   │       └── infra_config.py
│   └── infra/              # Configuración de infraestructura
├── .spa/                   # Configuración de spa-cli
│   ├── templates/         # Plantillas de código
│   │   ├── lambda_conf.txt
│   │   ├── lambda_endpoint.txt
│   │   ├── test_lambda_function.txt
│   │   └── lambda.txt
│   └── project.json       # Configuración del proyecto
└── spa_project.toml       # Archivo de configuración principal
```

## Configuración

### Archivo `spa_project.toml`

Este archivo contiene toda la configuración del proyecto. Se crea automáticamente cuando inicializas un proyecto.

```toml
[spa.project.definition]
name = "mi-proyecto"
description = "Descripción del proyecto"
author = "Tu Nombre"
author_email = "tu@email.com"
base_api = "api.yaml"
api_build_mode = "serverless"

[spa.template.files]
model = ".spa/templates/models/model.txt"
service = ".spa/templates/models/service.txt"
controller = ".spa/templates/models/controller.txt"
endpoint = ".spa/templates/lambda_endpoint.txt"
lambda_function = ".spa/templates/lambda.txt"
test_lambda = ".spa/templates/test_lambda_function.txt"
lambda_conf = ".spa/templates/lambda_conf.txt"

[spa.project.folders]
models = "src/layers/databases/python/core_db/models"
services = "src/layers/databases/python/core_db/services"
controllers = "src/layers/core/python/core_http/controllers"
lambdas = "src/lambdas"
layers = "src/layers"
root = "src"
jsons = ".spa/templates/json"
```

## Comandos Completos

### Secuencia de desarrollo típica:

```bash
# 1. Crear nuevo proyecto
spa project init

# 2. Instalar dependencias locales
spa project install

# 3. Agregar endpoints
spa endpoint add --method GET --path /usuarios --endpoint-name listar_usuarios
spa endpoint add --method POST --path /usuarios --endpoint-name crear_usuario

# 4. Agregar funciones Lambda adicionales
spa lambda add --lambda-name procesar_imagenes

# 5. Desarrollar y probar localmente
spa project run-api --reload --log-level debug

# 6. Construir para deployment
spa project build
```

## Características

- ✅ **Generación automática** de funciones Lambda desde comandos CLI
- ✅ **Plantillas preconfiguradas** para proyectos serverless
- ✅ **Soporte para bases de datos** MySQL y PostgreSQL
- ✅ **Configuración automática** de AWS Lambda layers
- ✅ **Servidor local FastAPI** con auto-reload para desarrollo y pruebas
- ✅ **Integración con AWS** SAM/CDK/Pulumi
- ✅ **Generación automática** de documentación API (OpenAPI/Swagger)
- ✅ **Tests unitarios** incluidos
- ✅ **Configuración de infraestructura** as a code
- ✅ **Servidor configurable** con opciones de host, puerto, logging y más

## Requisitos del Sistema

- Python 3.11+
- AWS CLI configurado (para deployment)
- Poetry (para gestión de dependencias)

## Autor

**David Cuy** - david.cuy.sanchez@gmail.com

## Enlaces

- **Repositorio:** https://github.com/DavidCuy/spa-cli
- **Documentación:** https://github.com/DavidCuy/spa-cli
- **PyPI:** https://pypi.org/project/spa-cli/

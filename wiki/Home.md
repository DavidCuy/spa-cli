# spa-cli — Guía rápida

Esta página documenta los comandos reales del proyecto `spa-cli` (CLI para proyectos serverless en Python).

> Ejecutables instalados: `spa` y `spa-cli` (ambos apuntan al mismo `spa_cli.cli:app`).

```markdown
spa
├─ project
│  ├─ init        # Inicializar proyecto (interactive)
│  ├─ install     # Instalar capas locales (layers)
│  ├─ run-api     # Iniciar servidor local para la API
│  └─ build       # Construir proyecto para deployment
├─ endpoint
│  └─ add         # Agregar endpoint HTTP y lambda asociada (--method --path --endpoint-name)
└─ lambda
   └─ add         # Crear lambda independiente (--lambda-name)

```

## Versión

Muestra la versión del CLI:

```bash
spa --version
spa-cli --version
```

## Comandos principales

El CLI tiene tres grupos de subcomandos principales: `project`, `endpoint` y `lambda`.

### 1) Comandos del proyecto (`spa project`)

- `spa project init`
  - Genera un nuevo proyecto a partir del template.
  - Opciones: `pattern_version` (por defecto `latest`).
  - El comando interactivo pedirá: nombre del proyecto, descripción, autor, email, motor de BD, región AWS y nombre del secreto para credenciales.

  Ejemplo:
  ```bash
  spa project init
  ```

- `spa project install`
  - Instala las capas (layers) locales del proyecto y sus dependencias.

  Ejemplo:
  ```bash
  spa project install
  ```

- `spa project run-api`
  - Inicia el servidor local para desarrollo y pruebas de la API (simula Lambdas localmente).

  Ejemplo:
  ```bash
  spa project run-api
  ```

- `spa project build`
  - Construye el proyecto para deployment: empaqueta layers, lambdas, copia infra y genera openapi.json en el build.

  Ejemplo:
  ```bash
  spa project build
  ```

### 2) Comandos de endpoints (`spa endpoint`)

- `spa endpoint add`
  - Agrega un nuevo endpoint HTTP y su carpeta de Lambda asociada.
  - Opciones (requeridas):
    - `--method` : Método HTTP (GET, POST, PUT, PATCH, DELETE)
    - `--path` : Ruta del endpoint (por ejemplo `/usuarios`)
    - `--endpoint-name` : Nombre de la función lambda (sin espacios ni guiones)

  Ejemplo:
  ```bash
  spa endpoint add --method POST --path /usuarios --endpoint-name crear_usuario
  ```

### 3) Comandos de Lambda (`spa lambda`)

- `spa lambda add`
  - Crea una nueva función Lambda (sin endpoint HTTP asociado).
  - Opciones:
    - `--lambda-name` : Nombre de la función lambda (sin espacios ni guiones)

  Ejemplo:
  ```bash
  spa lambda add --lambda-name procesar_facturas
  ```

## Comandos no habilitados

El grupo `model` existe en el código base pero no está activado en el CLI principal (comentado en `spa_cli/cli.py`). Por eso las instrucciones de `spa model` no están disponibles en la versión actual.

## Configuración del proyecto

El archivo de configuración se llama `spa_project.toml`. Si `spa project init` no encuentra uno, el comando `load_config` crea un `spa_project.toml` con valores por defecto en el directorio del proyecto.

## Ejemplo de flujo de trabajo típico

```bash
# 1. Inicializar proyecto
spa project init

# 2. Instalar capas locales
spa project install

# 3. Agregar endpoints
spa endpoint add --method GET --path /usuarios --endpoint-name listar_usuarios
spa endpoint add --method POST --path /usuarios --endpoint-name crear_usuario

# 4. Agregar funciones lambda adicionales
spa lambda add --lambda-name procesar_imagenes

# 5. Probar localmente
spa project run-api

# 6. Construir para deployment
spa project build
```

## Notas y recomendaciones

- Los nombres de lambda/endpoint no deben contener espacios ni guiones; el CLI los sustituye por guiones bajos si los detecta.
- Si necesitas ver ayuda detallada de cualquier comando: `spa <grupo> --help` o `spa <grupo> <comando> --help`.

---

Documento generado para coincidir con los subcomandos reales definidos en el código fuente del proyecto (vistas en `spa_cli/cli.py` y en `spa_cli/src/*`).

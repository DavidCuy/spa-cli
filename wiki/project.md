# Comandos de Proyecto - `spa project`

Los comandos de proyecto en spa-cli permiten gestionar el ciclo de vida completo de una aplicación serverless, desde la inicialización hasta el deployment.

## Descripción General

Los comandos del módulo `project` se utilizan para configurar, gestionar y construir proyectos serverless siguiendo el patrón serverless-python-application-pattern.

## Subcomandos Disponibles

### `spa project init`

**Inicializa un nuevo proyecto serverless**

Este comando crea un nuevo proyecto completo con la estructura necesaria para desarrollar aplicaciones serverless en Python con integración a AWS.

#### Sintaxis
```bash
spa project init [--pattern-version PATTERN_VERSION]
```

#### Parámetros
- `--pattern-version`: Versión del patrón a utilizar (opcional, por defecto 'latest')

#### Funcionamiento
1. Solicita información del proyecto al usuario de forma interactiva
2. Genera la estructura completa del proyecto
3. Configura la base de datos seleccionada 
4. Crea el archivo de configuración `spa_project.toml`
5. Configura las capas (layers) locales

#### Prompts Interactivos
El comando solicita la siguiente información:

```
Nombre del proyecto: [nombre_proyecto]
Descripción del proyecto: [descripción]
Nombre del autor: [autor] (por defecto el usuario del sistema)
Email del autor: [email]
Elija su motor de base de datos [mysql/postgresql]: mysql
Región de AWS [us-east-1]: [región]
Escriba el nombre del secreto para las credenciales de la base de datos: [nombre_secreto]
```

#### Ejemplo de Uso
```bash
spa project init
```

**Salida:**
```
Nombre del proyecto: mi-api-serverless
Descripción del proyecto: API REST para gestión de usuarios
Nombre del autor: Juan Pérez
Email del autor: juan@example.com
Elija su motor de base de datos [mysql/postgresql]: mysql
Región de AWS [us-east-1]: us-west-2
Escriba el nombre del secreto para las credenciales de la base de datos: my-db-credentials
```

#### Estructura Generada
```
mi-api-serverless/
├── src/
│   ├── layers/               # Capas Lambda
│   │   ├── databases/        # Acceso a base de datos
│   │   └── core/            # Funciones centrales
│   ├── lambdas/            # Funciones Lambda
│   └── infra/              # Configuración de infraestructura
├── .spa/                   # Configuración de spa-cli
│   ├── templates/          # Plantillas de código
│   └── project.json        # Configuración del proyecto
└── spa_project.toml        # Archivo de configuración principal
```

---

### `spa project install`

**Instala las dependencias locales del proyecto**

Este comando configura e instala las capas (layers) locales del proyecto, incluyendo todas las dependencias de Python necesarias y la configuración específica para el entorno de desarrollo.

#### Sintaxis
```bash
spa project install
```

#### Funcionamiento
1. Lee la configuración del proyecto desde `spa_project.toml`
2. Instala las capas locales del proyecto
3. Configura las dependencias necesarias
4. Prepara el entorno de desarrollo

#### Prerequisitos
- Debe ejecutarse dentro del directorio de un proyecto inicializado
- Se requiere el archivo `spa_project.toml`

#### Ejemplo de Uso
```bash
cd mi-proyecto-serverless
spa project install
```

**Salida esperada:**
```
Instalando capas locales...
Dependencias instaladas correctamente.
Configuración de proyecto completada.
```

---

### `spa project run-api`

**Ejecuta el servidor local para desarrollo**

Inicia un servidor HTTP local que simula el comportamiento de las funciones Lambda, permitiendo desarrollo y pruebas sin necesidad de desplegar código en AWS.

#### Sintaxis
```bash
spa project run-api
```

#### Funcionamiento
1. Lee la configuración del proyecto
2. Inicia un servidor HTTP local
3. Simula las funciones Lambda en el entorno local
4. Permite probar endpoints sin deploy en AWS

#### Características
- **Puerto por defecto**: 8000
- **Simulación completa** del entorno Lambda
- **Hot reload** para desarrollo
- **Debug** habilitado por defecto

#### Ejemplo de Uso
```bash
spa project run-api
```

**Salida:**
```
Iniciando servidor local
Servidor ejecutándose en http://localhost:8000
[INFO] Aplicación iniciada
[INFO] Endpoints públicos:
  GET  http://localhost:8000/usuarios
  POST http://localhost:8000/usuarios
```

#### Acceso a Endpoints
Los endpoints pueden probarse usando herramientas como curl o Postman:

```bash
curl http://localhost:8000/usuarios
curl -X POST http://localhost:8000/usuarios \
  -H "Content-Type: application/json" \
  -d '{"nombre":"Juan","email":"juan@example.com"}'
```

---

### `spa project build`

**Construye el proyecto para deployment**

Compila el proyecto y genera todos los archivos necesarios para el deployment en AWS, incluyendo las capas Lambda, funciones Lambda y documentación de la API.

#### Sintaxis
```bash
spa project build
```

#### Funcionamiento
1. Limpia el directorio de build anterior si existe
2. Crea la estructura de directorios de build
3. Construye las capas (layers) Lambda
4. Procesa y empaqueta las funciones Lambda
5. Construye la documentación de la API
6. Genera archivos de configuración de infraestructura

#### Archivos Generados
```
build/
├── infra/
│   ├── components/
│   │   ├── lambdas/
│   │   └── openapi.json
│   └── template.yaml
├── tmp_build_layer/
│   └── python/
└── pyproject.toml
```

#### Ejemplo de Uso
```bash
spa project build
```

**Salida detallada:**
```
Construyendo proyecto
Deleted directory: build
Building layers from src/layers into build/tmp_build_layer...
Building lambdas from src/lambdas...
Building lambda stack...
Building API definition...
Build completed.
```

#### Pasos de Build Detallados
1. **Limpieza**: Elimina ejecuites previos
2. **Copia de infraestructura**: Copia archivos de infraestructura
3. **Construcción de layers**: Empaqueta dependencias en capas
4. **Procesamiento de lambdas**: Prepara funciones Lambda
5. **Generación de API**: Crea documentación OpenAPI
6. **Configuración de stack**: Prepara templates de despliegue

## Casos de Uso Comunes

### Flujo de Desarrollo Completo

1. **Inicialización del proyecto**
```bash
mkdir my-serverless-app
cd my-serverless-app
spa project init
```

2. **Configuración del entorno**
```bash
spa project install
```

3. **Desarrollo con servidor local**
```bash
spa project run-api
# Desarrolla y prueba endpoints en http://localhost:8000
```

4. **Construcción para deployment**
```bash
spa project build
```

### Manejo de Errores

#### Error: "No se pudo leer la configuración del proyecto"
```bash
spa project install
# Error: No se pudo leer la configuracion del proyecto
```
**Solución**: Asegúrate de ejecutar el comando dentro de un proyecto inicializado que contenga el archivo `spa_project.toml`.

#### Error: "Ya existe un proyecto con este nombre"
Al intentar `spa project init` en un directorio que ya contiene un proyecto init:

**Solución**: Mueve el proyecto existente o usa un nombre diferente.

#### Error: "Directorio de build ocupado"
Durante `spa project build`:

**Solución**: El comando limpiará automáticamente el build anterior, pero asegúrate de que no tengas procesos usando archivos del directorio `build`.

## Configuración Avanzada

### Variables de Entorno
Puedes configurar variables de entorno para personalizar el build:

```bash
export ENVIRONMENT=production
export APP_NAME=mi-app-serverless
spa project build
```

### Configuración Personalizada
El archivo `spa_project.toml` permite personalizar rutas y configuraciones:

```toml
[spa.project.folders]
layers = "src/layers"
lambdas = "src/lambdas"  
models = "src/models"
```

## Tips y Mejores Prácticas

- **Siempre ejecuta `install`** antes de `run-api` o `build`
- **Usa `run-api` durante el desarrollo** para pruebas locales
- **Ejecuta `build` antes del deployment** para generar archivos finales
- **Mantén el archivo `spa_project.toml` actualizado** con la configuración del proyecto
- **Verifica las dependencies** instaladas en las capas antes del deployment

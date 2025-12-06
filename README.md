# spa-cli

**Una herramienta CLI para manejar proyectos serverless en AWS con Python**

spa-cli es una herramienta de línea de comandos que facilita la creación, desarrollo y deployment de aplicaciones serverless en AWS utilizando Python.

## Descripción

spa-cli proporciona comandos intuitivos para:
- Generar proyectos serverless
- Crear endpoints HTTP con funciones Lambda correspondientes
- Gestionar funciones Lambda para tareas en background
- Configurar la infraestructura de forma automatizada

## Funcionalidades Principales

- ⚡ **Generación automática** de funciones Lambda desde comandos CLI
- 🏗️ **Plantillas preconfiguradas** para proyectos serverless  
- 🗄️ **Soporte para bases de datos** MySQL y PostgreSQL
- ⚙️ **Configuración automática** de AWS Lambda layers
- 🖥️ **Servidor local** para desarrollo y pruebas
- ☁️ **Integración con AWS** SAM/CDK/Pulumi
- 📚 **Generación automática** de documentación API
- 🧪 **Tests unitarios** incluidos
- 🔧 **Configuración de infraestructura** as a code

## Instalación Rápida

```bash
pip install spa-cli
```

## Comandos Principales

### Trabajo con Proyectos
```bash
spa project init          # Crear nuevo proyecto
spa project install      # Instalar dependencias
spa project run-api      # Ejecutar servidor local
spa project build        # Construir para deployment
```

#### Opciones del servidor local (`run-api`)
```bash
spa project run-api --host 0.0.0.0 --port 8080
spa project run-api --reload --log-level debug
spa project run-api --host 0.0.0.0 --port 9000 --no-reload
```

**Opciones disponibles:**
- `--host TEXT` - Host para el servidor (default: 127.0.0.1)
- `--port INTEGER` - Puerto para el servidor (default: 8000)
- `--reload / --no-reload` - Habilitar auto-reload en cambios de código
- `--log-level TEXT` - Nivel de log: critical, error, warning, info, debug, trace
- `--root-path TEXT` - Path raíz para la aplicación
- `--proxy-headers / --no-proxy-headers` - Habilitar headers de proxy

### Gestión de Endpoints
```bash
spa endpoint add --method POST --path /usuarios --endpoint-name crear_usuario
```

### Funciones Lambda
```bash
spa lambda add --lambda-name procesar_datos
```

## Flujo de Desarrollo Típico

```bash
# 1. Crear nuevo proyecto
spa project init

# 2. Instalar dependencias locales  
spa project install

# 3. Agregar endpoints
spa endpoint add --method GET --path /usuarios --endpoint-name listar_usuarios

# 4. Desarrollar y probar localmente
spa project run-api --reload --log-level debug

# 5. Construir para deployment
spa project build
```

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

---

Para información detallada, comandos avanzados y configuración, consulta la [documentación completa](/spa-cli/README.md).

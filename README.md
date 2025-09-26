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
spa project run-api

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

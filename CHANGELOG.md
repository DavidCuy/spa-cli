# Changelog

Todos los cambios notables de este proyecto serán documentados en este archivo.

El formato está basado en [Keep a Changelog](https://keepachangelog.com/es-ES/1.0.0/),
y este proyecto se adhiere a [Semantic Versioning](https://semver.org/lang/es/).

## [1.0.11] - 2025-12-06

### Añadido

- Opciones configurables para el comando `spa project run-api`:
  - `--host`: Configurar el host del servidor (default: 127.0.0.1)
  - `--port`: Configurar el puerto del servidor (default: 8000)
  - `--reload / --no-reload`: Habilitar/deshabilitar auto-reload durante desarrollo
  - `--log-level`: Configurar nivel de logging (critical, error, warning, info, debug, trace)
  - `--root-path`: Configurar path raíz de la aplicación
  - `--proxy-headers / --no-proxy-headers`: Habilitar/deshabilitar headers de proxy
- Endpoint raíz (`/`) ahora retorna información detallada de configuración del servidor:
  - Información del entorno
  - Configuración del servidor (host, port, reload, log level, etc.)
  - Información de la request (client host, base URL, URL actual)
  - Configuración de la API (prefix, openapi_url, docs_url, redoc_url)
- Nuevas dependencias agregadas:
  - FastAPI ^0.116.1 con extras estándar
  - Mangum ^0.19.0 para integración Lambda-ASGI
  - Uvicorn ^0.35.0 como servidor ASGI

### Mejorado

- El comando `spa project run-api` ahora pasa argumentos configurables a FastAPI/Uvicorn
- Sistema de configuración del servidor mediante variables de entorno
- Documentación actualizada con ejemplos detallados de uso del servidor local
- Mejor experiencia de desarrollo con opciones flexibles de configuración

### Cambiado

- Versión actualizada de 1.0.10 a 1.0.11

## [1.0.10] - 2025-XX-XX

### Añadido

- Soporte para custom authorizers en esquemas de seguridad
- Compatibilidad con Swagger 2.0

### Corregido

- Problemas con esquemas de seguridad en API Gateway

---

[1.0.11]: https://github.com/DavidCuy/spa-cli/compare/v1.0.10...v1.0.11
[1.0.10]: https://github.com/DavidCuy/spa-cli/releases/tag/v1.0.10

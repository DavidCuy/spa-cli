# Comandos de Endpoint - `spa endpoint`

Los comandos de endpoint en spa-cli permiten crear y gestionar endpoints HTTP REST de manera fácil y automática, generando automáticamente la infraestructura necesaria tanto en código como en configuración.

## Descripción General

Los comandos del módulo `endpoint` automatizan la creación de endpoints HTTP con su correspondiente función Lambda, archivos de configuración y archivos de prueba.

## Subcomandos Disponibles

### `spa endpoint add`

**Agrega un nuevo endpoint HTTP a la API**

Este comando crea automáticamente todos los componentes necesarios para un nuevo endpoint REST: función Lambda, configuración de infraestructura, archivos de prueba y documentación.

#### Sintaxis
```bash
spa endpoint add --method METHOD --path PATH --endpoint-name ENDPOINT_NAME
```

#### Parámetros

| Parámetro | Descripción | Valores Válidos | Requerido |
|-----------|-------------|-----------------|-----------|
| `--method` | Método HTTP del endpoint | GET, POST, PUT, PATCH, DELETE | ✅ Sí |
| `--path` | Ruta del endpoint | Cualquier ruta válida (ej: `/usuarios`, `/usuarios/{id}`) | ✅ Sí |
| `--endpoint-name` | Nombre de la función Lambda | Cualquier nombre (espacios se convierten a guiones bajos) | ✅ Sí |

#### Funcionamiento Detallado

1. **Validación de nombres**: Convierte espacios y guiones a guiones bajos para consistencia
2. **Lectura de configuración**: Obtiene la configuración del proyecto desde `spa_project.toml`
3. **Verificación de existencia**: Comprueba que no exista un endpoint con el mismo nombre
4. **Generación de archivos**: Crea automáticamente:
   - Función Lambda (`lambda_function.py`)
   - Archivo de pruebas (`test_lambda_function.py`)
   - Configuración de infraestructura (`infra_config.py`)
   - Configuración del endpoint (`endpoint.yaml`)

#### Archivos Generados

Cada endpoint crea la siguiente estructura en `src/lambdas/[endpoint_name]/`:

```
src/lambdas/[endpoint_name]/
├── lambda_function.py       # Handler principal de la función
├── test_lambda_function.py  # Archivo de pruebas unitarias
├── infra_config.py         # Configuración de infraestructura
└── endpoint.yaml           # Configuración del endpoint HTTP
```

#### Ejemplos de Uso

##### Ejemplo 1: Endpoint para obtener lista de usuarios
```bash
spa endpoint add --method GET --path /usuarios --endpoint-name listar_usuarios
```

**Resultado:**
- Endpoint HTTP: `GET /usuarios`
- Función Lambda: `listar_usuarios`
- Archivos creados en `src/lambdas/listar_usuarios/`

##### Ejemplo 2: Endpoint para crear usuario
```bash
spa endpoint add --method POST --path /usuarios --endpoint-name crear_usuario
```

##### Ejemplo 3: Endpoint con parámetro de ruta
```bash
spa endpoint add --method GET --path /usuarios/{id} --endpoint-name obtener_usuario_por_id
```

##### Ejemplo 4: Endpoint para actualizar usuario
```bash
spa endpoint add --method PUT --path /usuarios/{id} --endpoint-name actualizar_usuario
```

##### Ejemplo 5: Endpoint para eliminar usuario
```bash
spa endpoint add --method DELETE --path /usuarios/{id} --endpoint-name eliminar_usuario
```

##### Ejemplo 6: Manejo de nombres con espacios
```bash
spa endpoint add --method POST --path /productos --endpoint-name "crear producto nuevo"
```

**Nota:** El nombre se convertirá automáticamente a `crear_producto_nuevo`

#### Contenido de los Archivos Generados

##### `lambda_function.py`
```python
def lambda_handler(event, context):
    # Tu lógica de negocio aquí
    return {
        'statusCode': 200,
        'body': 'Hello from Lambda!'
    }
```

##### `test_lambda_function.py`
```python
import pytest
from lambda_function import lambda_handler

def test_crear_usuario():
    event = {
        'httpMethod': 'POST',
        'path': '/usuarios',
        'body': '{"nombre":"Juan"}'
    }
    result = lambda_handler(event, None)
    assert result['statusCode'] == 200
```

##### `infra_config.py`
```python
lambda_name = "crear_usuario"
camel_name = "CrearUsuario"

def get_lambda_config():
    return {
        "function_name": lambda_name,
        "handler": "lambda_function.lambda_handler",
        "description": "Lambda function for crear_usuario"
    }
```

##### `endpoint.yaml`
```yaml
endpoint_url: "/usuarios"
endpoint_method: "post"
```

## Características Avanzadas

### Validación de Nombres Automática
El sistema automáticamente:
- Convierte espacios a guiones bajos: `"mi endpoint"` → `"mi_endpoint"`
- Convierte guiones a guiones bajos: `"mi-endpoint"` → `"mi_endpoint"`
- Mantiene consistencia en naming

#### Ejemplo de Convalidación
```bash
spa endpoint add --method GET --path /productos --endpoint-name "mi-endpoint especial"
# Resultado: función lambda "mi_endpoint_especial"
```

### Parametrización de Rutas

Los endpoints soportan parámetros de ruta usando la sintaxis `{parametro}`:

```bash
# Endpoint con parámetro simple
spa endpoint add --method GET --path /usuarios/{id} --endpoint-name obtener_usuario

# Endpoint con múltiples parámetros
spa endpoint add --method GET --path /usuarios/{usuario_id}/productos/{producto_id} --endpoint-name obtener_producto_usuario
```

### Integración con Sistema de Base de Datos

Los endpoints generados incluyen:
- **Configuración automática de conexión** a base de datos
- **Templates de acceso a datos** por batalla 
- **Handling de errores** pre-configurado
- **Validación de parámetros** según plan de

## Casos de Uso Comunes

### API REST Básica
```bash
# CRUD completa para entidad Usuario
spa endpoint add --method GET --path /usuarios --endpoint-name listar_usuarios
spa endpoint add --method POST --path /usuarios --endpoint-name crear_usuario
spa endpoint add --method GET --path /usuarios/{id} --endpoint-name obtener_usuario
spa endpoint add --method PUT --path /usuarios/{id} --endpoint-name actualizar_usuario
spa endpoint add --method DELETE --path /usuarios/{id} --endpoint-name eliminar_usuario
```

### API con Filtrado y Paginación
```bash
# Endpoints adicionales para funcionalidad extendida
spa endpoint add --method GET --path /usuarios/buscar --endpoint-name buscar_usuarios
spa endpoint add --method GET --path /usuarios/paginar --endpoint-name listar_usuarios_paginado
```

### API con Validación Avanzada
```bash
# Endpoints con validaciones específicas
spa endpoint add --method POST --path /usuarios/login --endpoint-name autenticar_usuario
spa endpoint add --method POST --path /usuarios/validar-email --endpoint-name validar_email
```

## Manejo de Errores

### Error: "Ya existe una ruta con nombre:"
```bash
spa endpoint add --method GET --path /usuarios --endpoint-name listar_usuarios
# Error: Ya existe una ruta con nombre: listar_usuarios
```

**Solución:** 
- Usa un nombre diferente: `--endpoint-name listar_usuarios_v2`
- O elimina el endpoint existente si no es necesario

### Error: "No se puede leer la configuración del proyecto"
```bash
spa endpoint add --method GET --path /usuarios --endpoint-name test
# Error: No se puede leer la configuración del proyecto
```

**Solución:**
- Asegúrate de estás en el directorio raíz del proyecto
- Verifica que existe el archivo `spa_project.toml`
- Ejecuta `spa project init` primero si no hay proyecto

### Nombre de Endpoint Duplicado en Diferentes Rutas
```bash
spa endpoint add --method GET --path /usuarios --endpoint-name usuario_get
spa endpoint add --method POST --path /productos --endpoint-name usuario_get
# Error: El nombre de endpoint debe ser único por función Lambda
```

**Solución:** Cada endpoint debe tener un nombre único (funciona como identificador de función Lambda)

## Mejores Prácticas

### Nomenclatura de Endpoints
- **Usar nombres descriptivos**: `crear_usuario` en lugar de `cu`
- **Incluir acción en el nombre**: `crear_`, `actualizar_`, `eliminar_`, `listar_`
- **Evitar nombres genéricos**: `handler1` → `obtener_usuario_por_id`

### Rutas RESTful
```bash
# Buenas prácticas de rutas
GET    /usuarios           # Lista todos
POST   /usuarios           # Crea nuevo
GET    /usuarios/{id}      # Obtiene por ID  
PUT    /usuarios/{id}      # Actualiza por ID
DELETE /usuarios/{id}      # Elimina por ID
```

### Agrupación por Funcionalidad
```bash
# Endpoints relacionados con autenticación
spa endpoint add --method POST --path /auth/login --endpoint-name autenticar
spa endpoint add --method POST --path /auth/logout --endpoint-name desautenticar
spa endpoint add --method POST --path /auth/registrar --endpoint-name registrar

# Endpoints relacionados con usuarios
spa endpoint add --method GET --path /usuarios --endpoint-name listar_usuarios
spa endpoint add --method POST --path /usuarios --endpoint-name crear_usuario
```

## Integración con Tests y Deployment

### Testing Automático
Siempre probar los nuevos endpoints:

```bash
# Después de crear un endpoint
spa project run-api

# En otra terminal o usando tu herramienta de testing
curl -X POST http://localhost:8000/usuarios \
  -H "Content-Type: application/json" \
  -d '{"nombre":"Juan","email":"juan@example.com"}'
```

### Build con Endpoints Nuevos
```bash
# Agregar nuevos endpoints antes del build
spa endpoint add --method GET --path /nuevo-endpoint --endpoint-name nuevo_endpoint
spa project build  # Incluye automáticamente el nuevo endpoint
```

## Configuración Avanzada

### Personalización de Templates
Los templates utilizados por `spa endpoint add` se pueden personalizar en el archivo `spa_project.toml`:

```toml
[spa.template.files]
lambda_function = ".spa/templates/lambda.txt"
endpoint = ".spa/templates/lambda_endpoint.txt"
test_lambda = ".spa/templates/test_lambda_function.txt"
lambda_conf = ".spa/templates/lambda_conf.txt"
```

### Modificaciones Post-Creación
Después de crear un endpoint, los archivos generados se pueden modificar libremente:

- **`lambda_function.py`**: Implementar la lógica de negocio
- **`infra_config.py`**: Configurar variables específicas de infraestructura
- **`endpoint.yaml`**: Ajustar configuraciones del endpoint HTTP
- **`test_lambda_function.py`**: Agregar casos de prueba específicos

# Lambda Authorizers - Configuración Personalizada

## Descripción General

A partir de la versión actual, spa-cli permite configurar custom authorizers de Lambda a través del archivo `spa_project.toml`. Esta funcionalidad permite especificar múltiples authorizers personalizados con sus propios roles y funciones Lambda.

## Configuración en spa_project.toml

### Estructura de Configuración

Para configurar custom authorizers, agrega una sección `[spa.api.lambda-authorizers]` en tu archivo `spa_project.toml`:

```toml
[spa.api.lambda-authorizers.nombre_clave]
role_name = "nombre-del-rol"
lambda_name = "nombre-de-la-lambda"
```

### Parámetros

- **nombre_clave**: La clave debe coincidir con el nombre del security scheme en `api.yaml` sin el sufijo `_authorizer`. Por ejemplo, si tu security scheme se llama `custom1_authorizer`, la clave debe ser `custom1`.
- **role_name**: El nombre del rol IAM que API Gateway usará para invocar la Lambda authorizer (sin prefijos de entorno o aplicación, solo el nombre base).
- **lambda_name**: El nombre de la función Lambda authorizer (sin prefijos de entorno o aplicación, solo el nombre base).

### Ejemplo Completo

#### 1. Configuración en spa_project.toml

```toml
[spa.project.definition]
name = "my-api"
description = "Mi API con custom authorizers"
author = "John Doe"
author_email = "john@example.com"
base_api = "api.yaml"

[spa.template.files]
model = ".spa/templates/models/model.txt"
service = ".spa/templates/models/service.txt"
controller = ".spa/templates/models/controller.txt"
endpoint = ".spa/templates/lambda_endpoint.txt"
lambda_function = ".spa/templates/lambda.txt"
test_lambda = ".spa/templates/test_lambda_function.txt"
lambda_conf = ".spa/templates/lambda_conf.txt"

[spa.project.folders]
root = "src"
models = "src/layers/databases/python/core_db/models"
services = "src/layers/databases/python/core_db/services"
controllers = "src/layers/core/python/core_http/controllers"
jsons = ".spa/templates/json"
lambdas = "src/lambdas"
layers = "src/layers"

# Custom Lambda Authorizers
# La clave 'custom1' coincide con 'custom1_authorizer' en api.yaml
[spa.api.lambda-authorizers.custom1]
role_name = "custom-auth-role"
lambda_name = "custom-auth"

# La clave 'admin' coincide con 'admin_authorizer' en api.yaml
[spa.api.lambda-authorizers.admin]
role_name = "admin-auth-role"
lambda_name = "admin-auth"
```

#### 2. Configuración en api.yaml

En tu archivo `api.yaml`, define los security schemes. Nota que el nombre del security scheme debe terminar con `_authorizer` y el prefijo debe coincidir con la clave en el archivo de configuración:

```yaml
openapi: 3.0.0
info:
  title: My API
  version: 1.0.0

components:
  securitySchemes:
    # El nombre 'custom1_authorizer' se mapea a la clave 'custom1' en spa_project.toml
    custom1_authorizer:
      type: apiKey
      name: Authorization
      in: header
      x-amazon-apigateway-authtype: oauth2
      x-amazon-apigateway-authorizer:
        type: token
        authorizerUri: LAMBDA_ARN_PLACEHOLDER
        authorizerCredentials: APIG_ROLE_ARN_PLACEHOLDER
        identitySource: method.request.header.Authorization
        authorizerResultTtlInSeconds: 60

    # El nombre 'admin_authorizer' se mapea a la clave 'admin' en spa_project.toml
    admin_authorizer:
      type: apiKey
      name: X-Admin-Token
      in: header
      x-amazon-apigateway-authtype: custom
      x-amazon-apigateway-authorizer:
        type: request
        authorizerUri: LAMBDA_ARN_PLACEHOLDER
        authorizerCredentials: APIG_ROLE_ARN_PLACEHOLDER
        identitySource: method.request.header.X-Admin-Token
        authorizerResultTtlInSeconds: 300

paths:
  /users:
    get:
      summary: Get users
      security:
        - custom1_authorizer: []
      x-amazon-apigateway-integration:
        uri: LAMBDA_URI_PLACEHOLDER
        credentials: API_ROLE_PLACEHOLDER
        httpMethod: POST
        type: aws_proxy

  /admin/settings:
    post:
      summary: Update admin settings
      security:
        - admin_authorizer: []
      x-amazon-apigateway-integration:
        uri: LAMBDA_URI_PLACEHOLDER
        credentials: API_ROLE_PLACEHOLDER
        httpMethod: POST
        type: aws_proxy
```

## Proceso de Build

Cuando ejecutas `spa project build`, el sistema:

1. **Lee la configuración** de `spa_project.toml`
2. **Identifica los security schemes** en `api.yaml` que contienen `x-amazon-apigateway-authorizer`
3. **Extrae la clave** removiendo el sufijo `_authorizer` del nombre del security scheme
4. **Busca la configuración** correspondiente en `[spa.api.lambda-authorizers.clave]`
5. **Reemplaza los ARNs** usando:
   - Variables de entorno (ENVIRONMENT, APP_NAME, AWS_ACCOUNT_ID, AWS_REGION)
   - Los valores `lambda_name` y `role_name` de la configuración

### ARNs Generados

Para el ejemplo anterior, con las siguientes variables de entorno:
- ENVIRONMENT=prod
- APP_NAME=my-api
- AWS_ACCOUNT_ID=123456789012
- AWS_REGION=us-east-1

Los ARNs generados serán:

**custom1_authorizer:**
- `authorizerUri`: `arn:aws:apigateway:us-east-1:lambda:path/2015-03-31/functions/arn:aws:lambda:us-east-1:123456789012:function:prod-my-api-custom-auth/invocations`
- `authorizerCredentials`: `arn:aws:iam::123456789012:role/prod-my-api-custom-auth-role`

**admin_authorizer:**
- `authorizerUri`: `arn:aws:apigateway:us-east-1:lambda:path/2015-03-31/functions/arn:aws:lambda:us-east-1:123456789012:function:prod-my-api-admin-auth/invocations`
- `authorizerCredentials`: `arn:aws:iam::123456789012:role/prod-my-api-admin-auth-role`

### Resultado JSON del Build

El archivo generado contendrá:

```json
{
  "components": {
    "securitySchemes": {
      "custom1_authorizer": {
        "type": "apiKey",
        "name": "Authorization",
        "in": "header",
        "x-amazon-apigateway-authtype": "oauth2",
        "x-amazon-apigateway-authorizer": {
          "type": "token",
          "authorizerUri": "arn:aws:apigateway:us-east-1:lambda:path/2015-03-31/functions/arn:aws:lambda:us-east-1:123456789012:function:prod-my-api-custom-auth/invocations",
          "authorizerCredentials": "arn:aws:iam::123456789012:role/prod-my-api-custom-auth-role",
          "identitySource": "method.request.header.Authorization",
          "authorizerResultTtlInSeconds": 60
        }
      }
    }
  }
}
```

## Comportamiento por Defecto

Si un security scheme no tiene una configuración correspondiente en `spa_project.toml`, el sistema usa el comportamiento por defecto:

- `authorizerUri` se reemplaza con:
  `arn:aws:apigateway:{region}:lambda:path/2015-03-31/functions/arn:aws:lambda:{region}:{account}:function:{env}-{app}-authorizer/invocations`

- `authorizerCredentials` se reemplaza con:
  `arn:aws:iam::{account}:role/{env}-{app}-authorizer-role`

## Convenciones de Nombres

### Mapeo de Claves

El sistema extrae la clave del authorizer removiendo el sufijo `_authorizer` del nombre del security scheme:

- `custom1_authorizer` → clave: `custom1`
- `admin_authorizer` → clave: `admin`
- `my_custom_authorizer` → clave: `my_custom`

### Nombres de Recursos AWS

Los nombres finales de los recursos AWS se construyen con el formato:

- **Lambda**: `{ENVIRONMENT}-{APP_NAME}-{lambda_name}`
- **IAM Role**: `{ENVIRONMENT}-{APP_NAME}-{role_name}`

Donde `lambda_name` y `role_name` son los valores especificados en `spa_project.toml`.

## Casos de Uso

### 1. Múltiples Niveles de Autorización

Configura diferentes authorizers para diferentes niveles de acceso:

```toml
# En spa_project.toml
[spa.api.lambda-authorizers.user]
role_name = "user-auth-role"
lambda_name = "user-auth"

[spa.api.lambda-authorizers.admin]
role_name = "admin-auth-role"
lambda_name = "admin-auth"

[spa.api.lambda-authorizers.superadmin]
role_name = "superadmin-auth-role"
lambda_name = "superadmin-auth"
```

```yaml
# En api.yaml
components:
  securitySchemes:
    user_authorizer:
      type: apiKey
      name: Authorization
      in: header
      x-amazon-apigateway-authorizer:
        type: token
        authorizerUri: LAMBDA_ARN_PLACEHOLDER
        authorizerCredentials: APIG_ROLE_ARN_PLACEHOLDER
        identitySource: method.request.header.Authorization

    admin_authorizer:
      type: apiKey
      name: Authorization
      in: header
      x-amazon-apigateway-authorizer:
        type: token
        authorizerUri: LAMBDA_ARN_PLACEHOLDER
        authorizerCredentials: APIG_ROLE_ARN_PLACEHOLDER
        identitySource: method.request.header.Authorization

    superadmin_authorizer:
      type: apiKey
      name: Authorization
      in: header
      x-amazon-apigateway-authorizer:
        type: token
        authorizerUri: LAMBDA_ARN_PLACEHOLDER
        authorizerCredentials: APIG_ROLE_ARN_PLACEHOLDER
        identitySource: method.request.header.Authorization
```

### 2. Autorización por Tipo de Cliente

```toml
# En spa_project.toml
[spa.api.lambda-authorizers.mobile]
role_name = "mobile-auth-role"
lambda_name = "mobile-auth"

[spa.api.lambda-authorizers.web]
role_name = "web-auth-role"
lambda_name = "web-auth"

[spa.api.lambda-authorizers.apikey]
role_name = "apikey-auth-role"
lambda_name = "apikey-auth"
```

```yaml
# En api.yaml
components:
  securitySchemes:
    mobile_authorizer:
      # ... configuración

    web_authorizer:
      # ... configuración

    apikey_authorizer:
      # ... configuración
```

## Mejores Prácticas

1. **Convención de Nombres**:
   - Usa nombres descriptivos en kebab-case para `lambda_name` y `role_name`
   - El nombre del security scheme en `api.yaml` debe terminar con `_authorizer`
   - La clave en `spa_project.toml` debe ser el prefijo antes de `_authorizer`

2. **Consistencia**:
   - Mantén un patrón consistente en la nomenclatura de tus authorizers
   - Ejemplo: Si tienes `custom1_authorizer` en api.yaml, usa `custom1` como clave en spa_project.toml

3. **Documentación**:
   - Documenta qué authorizer se debe usar para cada tipo de endpoint
   - Incluye comentarios en tu configuración explicando el propósito de cada authorizer

4. **Testing**:
   - Prueba cada authorizer después de configurarlo
   - Verifica que los ARNs generados sean correctos

5. **Variables de Entorno**:
   - Asegúrate de tener configuradas todas las variables de entorno necesarias antes de ejecutar `spa project build`:
     - ENVIRONMENT
     - APP_NAME
     - AWS_ACCOUNT_ID
     - AWS_REGION

## Troubleshooting

### Error: "No se pudo leer la configuración del proyecto"

**Causa**: El archivo `spa_project.toml` no existe o tiene un formato incorrecto.

**Solución**: Verifica que el archivo existe y tiene el formato TOML correcto.

### Los ARNs no se generan correctamente

**Causa**: La clave en `spa_project.toml` no coincide con el prefijo del security scheme en `api.yaml`.

**Solución**:
- Si tu security scheme se llama `custom1_authorizer`, la clave en el archivo de configuración debe ser `custom1`
- Verifica que hayas removido el sufijo `_authorizer` de la clave

**Ejemplo correcto**:
```toml
# spa_project.toml
[spa.api.lambda-authorizers.custom1]  # ← sin '_authorizer'
role_name = "my-role"
lambda_name = "my-lambda"
```

```yaml
# api.yaml
components:
  securitySchemes:
    custom1_authorizer:  # ← con '_authorizer'
      x-amazon-apigateway-authorizer:
        # ...
```

### ARNs incorrectos generados

**Causa**: Variables de entorno no configuradas correctamente.

**Solución**: Verifica que tienes configuradas:
- ENVIRONMENT
- APP_NAME
- AWS_ACCOUNT_ID
- AWS_REGION

### Error: AttributeError en lambda_name o role_name

**Causa**: La configuración usa los campos antiguos `role_placeholder` y `lambda_placeholder`.

**Solución**: Actualiza tu configuración para usar los nuevos campos:
- Cambiar `role_placeholder` → `role_name`
- Cambiar `lambda_placeholder` → `lambda_name`

## Migración desde Versiones Anteriores

Si estás actualizando desde una versión anterior:

### Cambio de Campos en la Configuración

**Antes (versión antigua)**:
```toml
[spa.api.lambda-authorizers.CustomAuth]
role_placeholder = "CUSTOM_AUTH_ROLE_PLACEHOLDER"
lambda_placeholder = "CUSTOM_AUTH_LAMBDA_PLACEHOLDER"
```

**Ahora (versión actual)**:
```toml
[spa.api.lambda-authorizers.custom]
role_name = "custom-auth-role"
lambda_name = "custom-auth"
```

### Cambio en el Mapeo

- **Antes**: El nombre completo del security scheme (ej. `CustomAuth`) se usaba como clave
- **Ahora**: Se usa el prefijo sin el sufijo `_authorizer` (ej. `custom` para `custom_authorizer`)

### Pasos de Migración

1. Actualiza tu archivo `spa_project.toml`:
   - Cambia `role_placeholder` a `role_name` con el nombre real del rol
   - Cambia `lambda_placeholder` a `lambda_name` con el nombre real de la lambda
   - Ajusta las claves para que coincidan con el prefijo del security scheme

2. Asegúrate de que tus security schemes en `api.yaml` terminen con `_authorizer`

3. Los valores en `authorizerUri` y `authorizerCredentials` pueden ser cualquier placeholder - el sistema los reemplazará automáticamente si existe la configuración correspondiente

## Referencias

- [Comandos de Proyecto](project.md)
- [AWS Lambda Authorizers Documentation](https://docs.aws.amazon.com/apigateway/latest/developerguide/apigateway-use-lambda-authorizer.html)

# Lambda Authorizers - Configuración Personalizada

## Descripción General

A partir de la versión actual, spa-cli permite configurar custom authorizers de Lambda a través del archivo `spa_project.toml`. Esta funcionalidad permite especificar múltiples authorizers personalizados con sus propios roles y funciones Lambda.

## Configuración en spa_project.toml

### Estructura de Configuración

Para configurar custom authorizers, agrega una sección `[spa.api.lambda-authorizers]` en tu archivo `spa_project.toml`:

```toml
[spa.api.lambda-authorizers.NombreDelAuthorizer]
role_placeholder = "PLACEHOLDER_DEL_ROL"
lambda_placeholder = "PLACEHOLDER_DE_LA_LAMBDA"
```

### Parámetros

- **role_placeholder**: El placeholder que se usará en el archivo `api.yaml` para el rol del API Gateway que invocará la Lambda authorizer
- **lambda_placeholder**: El placeholder que se usará en el archivo `api.yaml` para la URI de la función Lambda authorizer

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
[spa.api.lambda-authorizers.CustomAuth]
role_placeholder = "CUSTOM_AUTH_ROLE_PLACEHOLDER"
lambda_placeholder = "CUSTOM_AUTH_LAMBDA_PLACEHOLDER"

[spa.api.lambda-authorizers.AdminAuth]
role_placeholder = "ADMIN_AUTH_ROLE_PLACEHOLDER"
lambda_placeholder = "ADMIN_AUTH_LAMBDA_PLACEHOLDER"
```

#### 2. Configuración en api.yaml

En tu archivo `api.yaml`, define los security schemes con los placeholders correspondientes:

```yaml
openapi: 3.0.0
info:
  title: My API
  version: 1.0.0

components:
  securitySchemes:
    CustomAuth:
      type: apiKey
      name: Authorization
      in: header
      x-amazon-apigateway-authtype: custom
      x-amazon-apigateway-authorizer:
        type: request
        authorizerUri: CUSTOM_AUTH_LAMBDA_PLACEHOLDER
        authorizerCredentials: CUSTOM_AUTH_ROLE_PLACEHOLDER
        identitySource: method.request.header.Authorization
        authorizerResultTtlInSeconds: 300

    AdminAuth:
      type: apiKey
      name: Authorization
      in: header
      x-amazon-apigateway-authtype: custom
      x-amazon-apigateway-authorizer:
        type: request
        authorizerUri: ADMIN_AUTH_LAMBDA_PLACEHOLDER
        authorizerCredentials: ADMIN_AUTH_ROLE_PLACEHOLDER
        identitySource: method.request.header.Authorization
        authorizerResultTtlInSeconds: 300

paths:
  /users:
    get:
      summary: Get users
      security:
        - CustomAuth: []
      x-amazon-apigateway-integration:
        uri: LAMBDA_URI_PLACEHOLDER
        credentials: API_ROLE_PLACEHOLDER
        httpMethod: POST
        type: aws_proxy

  /admin/settings:
    post:
      summary: Update admin settings
      security:
        - AdminAuth: []
      x-amazon-apigateway-integration:
        uri: LAMBDA_URI_PLACEHOLDER
        credentials: API_ROLE_PLACEHOLDER
        httpMethod: POST
        type: aws_proxy
```

## Proceso de Build

Cuando ejecutas `spa project build`, el sistema:

1. **Lee la configuración** de `spa_project.toml`
2. **Identifica los security schemes** en `api.yaml`
3. **Busca coincidencias** entre el nombre del security scheme y las configuraciones en `[spa.api.lambda-authorizers]`
4. **Reemplaza los placeholders** con los ARNs reales basándose en:
   - Variables de entorno (ENVIRONMENT, APP_NAME, AWS_ACCOUNT_ID, AWS_REGION)
   - El nombre del security scheme (convertido a kebab-case)

### ARNs Generados

Para el ejemplo anterior, con las siguientes variables de entorno:
- ENVIRONMENT=prod
- APP_NAME=my-api
- AWS_ACCOUNT_ID=123456789012
- AWS_REGION=us-east-1

Los placeholders se reemplazarán por:

**CustomAuth:**
- `authorizerUri`: `arn:aws:apigateway:us-east-1:lambda:path/2015-03-31/functions/arn:aws:lambda:us-east-1:123456789012:function:prod-my-api-customauth/invocations`
- `authorizerCredentials`: `arn:aws:iam::123456789012:role/prod-my-api-customauth-role`

**AdminAuth:**
- `authorizerUri`: `arn:aws:apigateway:us-east-1:lambda:path/2015-03-31/functions/arn:aws:lambda:us-east-1:123456789012:function:prod-my-api-adminauth/invocations`
- `authorizerCredentials`: `arn:aws:iam::123456789012:role/prod-my-api-adminauth-role`

## Comportamiento por Defecto

Si no configuras custom authorizers en `spa_project.toml`, el sistema mantiene el comportamiento por defecto:

- Placeholders `AUTHORIZER_URI_PLACEHOLDER` se reemplazan con:
  `arn:aws:apigateway:{region}:lambda:path/2015-03-31/functions/arn:aws:lambda:{region}:{account}:function:{env}-{app}-authorizer/invocations`

- Placeholders `AUTHORIZER_ROLE_PLACEHOLDER` se reemplazan con:
  `arn:aws:iam::{account}:role/{env}-{app}-authorizer-role`

## Convenciones de Nombres

El sistema convierte automáticamente el nombre del security scheme a kebab-case para los nombres de recursos:

- `CustomAuth` → `customauth`
- `AdminAuth` → `adminauth`
- `My_Custom_Authorizer` → `my-custom-authorizer`

Esto asegura consistencia con las convenciones de nombres de AWS Lambda y IAM roles.

## Casos de Uso

### 1. Múltiples Niveles de Autorización

Configura diferentes authorizers para diferentes niveles de acceso:

```toml
[spa.api.lambda-authorizers.UserAuth]
role_placeholder = "USER_AUTH_ROLE"
lambda_placeholder = "USER_AUTH_LAMBDA"

[spa.api.lambda-authorizers.AdminAuth]
role_placeholder = "ADMIN_AUTH_ROLE"
lambda_placeholder = "ADMIN_AUTH_LAMBDA"

[spa.api.lambda-authorizers.SuperAdminAuth]
role_placeholder = "SUPER_ADMIN_AUTH_ROLE"
lambda_placeholder = "SUPER_ADMIN_AUTH_LAMBDA"
```

### 2. Autorización por Tipo de Cliente

```toml
[spa.api.lambda-authorizers.MobileAuth]
role_placeholder = "MOBILE_AUTH_ROLE"
lambda_placeholder = "MOBILE_AUTH_LAMBDA"

[spa.api.lambda-authorizers.WebAuth]
role_placeholder = "WEB_AUTH_ROLE"
lambda_placeholder = "WEB_AUTH_LAMBDA"

[spa.api.lambda-authorizers.ApiKeyAuth]
role_placeholder = "API_KEY_AUTH_ROLE"
lambda_placeholder = "API_KEY_AUTH_LAMBDA"
```

## Mejores Prácticas

1. **Nombres Descriptivos**: Usa nombres claros para tus authorizers que reflejen su propósito
2. **Consistencia en Placeholders**: Mantén un patrón consistente en tus placeholders (ej: `{NOMBRE}_ROLE_PLACEHOLDER`)
3. **Documentación**: Documenta qué authorizer se debe usar para cada tipo de endpoint
4. **Testing**: Prueba cada authorizer después de configurarlo
5. **Variables de Entorno**: Asegúrate de tener configuradas todas las variables de entorno necesarias antes de ejecutar `spa project build`

## Troubleshooting

### Error: "No se pudo leer la configuración del proyecto"

**Causa**: El archivo `spa_project.toml` no existe o tiene un formato incorrecto.

**Solución**: Verifica que el archivo existe y tiene el formato TOML correcto.

### Los placeholders no se reemplazan

**Causa**: El nombre del security scheme en `api.yaml` no coincide con ninguna configuración en `[spa.api.lambda-authorizers]`.

**Solución**: Verifica que los nombres coincidan exactamente (case-sensitive).

### ARNs incorrectos generados

**Causa**: Variables de entorno no configuradas correctamente.

**Solución**: Verifica que tienes configuradas:
- ENVIRONMENT
- APP_NAME
- AWS_ACCOUNT_ID
- AWS_REGION

## Migración desde Versiones Anteriores

Si estás actualizando desde una versión anterior que usaba el comportamiento por defecto:

1. El comportamiento por defecto sigue funcionando si no agregas la sección `[spa.api.lambda-authorizers]`
2. Para migrar a custom authorizers, simplemente agrega la configuración en `spa_project.toml`
3. Actualiza tus placeholders en `api.yaml` para que coincidan con los nuevos placeholders configurados

## Referencias

- [Comandos de Proyecto](project.md)
- [AWS Lambda Authorizers Documentation](https://docs.aws.amazon.com/apigateway/latest/developerguide/apigateway-use-lambda-authorizer.html)

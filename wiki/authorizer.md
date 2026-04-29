# Comandos de Authorizer - `spa authorizer`

Los comandos de authorizer en spa-cli permiten generar y registrar Lambda Authorizers personalizados. El handler resultante se ejecuta sin cambios en dos contextos:

- **Modo serverless**: como Lambda real conectada a API Gateway vía `x-amazon-apigateway-authorizer`.
- **Modo container**: como dependencia FastAPI (middleware) gracias al `auth_bridge.py` generado durante `spa project build --build-mode container`.

Ver detalle completo del flujo container en [lambda-authorizers.md](lambda-authorizers.md#middleware-fastapi-modo-container).

## Descripción General

El módulo `authorizer` automatiza dos cosas: **(1)** la creación del archivo de código del authorizer (basado en patrón Cognito Token + IAM policy) y **(2)** el registro de la entry correspondiente en `spa_project.toml`. Esto cierra el ciclo entre la declaración del `securityScheme` en `api.yaml` y la implementación real.

## Subcomandos Disponibles

### `spa authorizer add`

**Genera un Lambda Authorizer y lo registra en la configuración del proyecto**

#### Sintaxis
```bash
spa authorizer add NAME [--role-name ROLE] [--lambda-name LAMBDA]
```

#### Parámetros

| Parámetro | Descripción | Default | Requerido |
|-----------|-------------|---------|-----------|
| `NAME` (positional) | Prefijo del authorizer. Debe matchear el `securityScheme` de `api.yaml` sin el sufijo `_authorizer`. Espacios y guiones se convierten a `_`. | — | ✅ Sí |
| `--role-name` | Nombre del IAM role que ejecuta la Lambda. Se usa al construir el ARN en modo serverless. | `<NAME>-authorizer-role` | No |
| `--lambda-name` | Nombre de la función Lambda authorizer. | `<NAME>-authorizer` | No |

#### Funcionamiento Detallado

1. **Normalización del nombre**: convierte `-` y espacios a `_`.
2. **Lectura de configuración**: carga `spa_project.toml` vía `load_config()`. Si falta, aborta.
3. **Generación del handler**:
   - Crea `src/authorizers/<NAME>/handler.py` desde el template interno `spa_cli/templates/authorizers/handler.py.txt`.
   - Crea `__init__.py` vacíos en `src/authorizers/` y `src/authorizers/<NAME>/` si faltan (para que sean paquetes Python importables).
   - Skip silencioso si `handler.py` ya existe (no sobreescribe trabajo).
4. **Registro en TOML**: append de la sección:

   ```toml
   [spa.api.lambda-authorizers.<NAME>]
   role_name = "<role-name>"
   lambda_name = "<lambda-name>"
   module = "src.authorizers.<NAME>.handler"
   ```

   Skip si la sección ya existe.

#### Archivos Generados

```
src/authorizers/
├── __init__.py
└── <NAME>/
    ├── __init__.py
    └── handler.py
```

`spa_project.toml` recibe la nueva entry de `[spa.api.lambda-authorizers.<NAME>]`.

#### Ejemplos de Uso

##### Ejemplo 1: Authorizer principal (Cognito) con defaults
```bash
spa authorizer add principal
```

**Resultado:**
- `src/authorizers/principal/handler.py` generado.
- En `spa_project.toml`:
  ```toml
  [spa.api.lambda-authorizers.principal]
  role_name = "principal-authorizer-role"
  lambda_name = "principal-authorizer"
  module = "src.authorizers.principal.handler"
  ```

##### Ejemplo 2: Authorizer con nombres custom de IAM/Lambda
```bash
spa authorizer add admin --role-name admin-auth-role --lambda-name admin-authorizer-fn
```

##### Ejemplo 3: Múltiples authorizers (multi-tenant)
```bash
spa authorizer add user
spa authorizer add admin
spa authorizer add apikey
```

#### Contenido del Handler Generado

El template `handler.py.txt` produce código equivalente al patrón Cognito clásico:

```python
def lambda_handler(event, context):
    raw_token = event.get("authorizationToken")
    if not raw_token:
        return generate_policy("user", Effect.DENY, event.get("methodArn", "*"))

    token = raw_token.replace("Bearer ", "").strip()

    try:
        token_data = validate_access_login(token)   # cognito.get_user(AccessToken=token)
    except CognitoServiceError:
        return generate_policy("user", Effect.DENY, event.get("methodArn", "*"))

    username = token_data.get("Username")
    if not username:
        return generate_policy("user", Effect.DENY, event.get("methodArn", "*"))

    user_attributes = token_data.get("UserAttributes", [])
    user_data = {"username": username}
    for attr in user_attributes:
        if not attr["Name"].startswith("custom:"):
            user_data[attr["Name"]] = attr["Value"]

    extra_info = {"user": json.dumps(user_data)}
    resource = generate_resource_income(event.get("methodArn", "*"))
    return generate_policy("user", Effect.ALLOW, resource, context=extra_info)
```

`boto3` se importa con `try/except` — el stub no truena en entornos sin AWS SDK (útil para tests locales).

Excepciones modeladas:
- `Exception("Unauthorized")` → API GW 401 / Bridge 401.
- `Exception("MalformedToken")` → API GW 422 / Bridge 422.
- `CognitoServiceError` (interna, captura `ClientError`) → DENY policy → 403.

## Convención `_authorizer` con `api.yaml`

El nombre del comando se enlaza al `securityScheme` por convención estricta. Para `spa authorizer add principal`:

```yaml
# api.yaml
components:
  securitySchemes:
    principal_authorizer:                       # NAME + "_authorizer"
      type: apiKey
      name: Authorization                        # Header donde llega el token
      in: header                                 # header | query | cookie
      x-amazon-apigateway-authtype: custom
      x-amazon-apigateway-authorizer:
        type: token
        identitySource: method.request.header.Authorization
        authorizerUri: LAMBDA_ARN_PLACEHOLDER    # build_api lo sustituye en serverless
        authorizerCredentials: APIG_ROLE_ARN_PLACEHOLDER
        authorizerResultTtlInSeconds: 60
```

Endpoint protegido:

```yaml
paths:
  /users/{id}:
    get:
      security:
        - principal_authorizer: []
```

## Cómo se Ejecuta el Handler

| Modo | Quién invoca `lambda_handler` | Origen del `event` |
|------|--------------------------------|--------------------|
| `serverless` | API Gateway (autenticado por la Lambda real desplegada con Pulumi) | API Gateway construye el `event` TOKEN/REQUEST |
| `container` | `auth_bridge.py` (middleware FastAPI) | `_build_apigw_event(request, raw_token, path)` arma un event APIGW REST v1 sintético desde el HTTP request |

### Token Source

El bridge lee `securityScheme.in` + `securityScheme.name` del `openapi.json` para extraer el token:

| `in` | Source en runtime |
|------|-------------------|
| `header` (default) | `request.headers[name]` (ej. `Authorization`) |
| `query` | `request.query_params[name]` |
| `cookie` | `request.cookies[name]` |
| (fallback) | parsea `x-amazon-apigateway-authorizer.identitySource` |

### Auto-discover del módulo

El bridge resuelve qué función importar en este orden:

1. `module` explícito de `spa_project.toml` (lo que `spa authorizer add` registra por defecto).
2. `src.authorizers.<key>.handler.lambda_handler`.
3. Legacy: `build.infra.components.authorizers.<key>.lambda_function.lambda_handler` (compat con proyectos serverless históricos).
4. `infra.components.authorizers.<key>.lambda_function.lambda_handler`.

## Manejo de Errores

### Error: "Template no encontrado"
**Causa**: paquete `spa-cli` instalado mal o falta el template empaquetado.

**Solución**: reinstalar (`pip install --force-reinstall spa-cli`).

### Error: "No se pudo leer la configuración del proyecto"
**Causa**: `spa_project.toml` falta o es inválido.

**Solución**: ejecutar `spa project init` o crear el archivo manualmente.

### Skip de archivos existentes
Si `handler.py` ya existe o la sección TOML ya fue agregada, el comando no sobreescribe — emite `[skip]`.

## Salida Esperada

```
[+] Generado handler: src/authorizers/principal/handler.py
[+] Registrado [spa.api.lambda-authorizers.principal] en spa_project.toml
Listo. Asegúrate que el securityScheme 'principal_authorizer' esté declarado
en api.yaml para que el bridge lo enlace.
```

## Mejores Prácticas

### Nomenclatura
- **NAME** corto, en `snake_case`, alineado con el role del usuario que valida (ej. `principal`, `admin`, `apikey`, `mobile`).
- **`role_name` y `lambda_name`** en `kebab-case` (convención AWS).

### Implementación del Handler
- El stub generado asume validación Cognito. Si el proyecto usa JWT propio o API key, reemplazar `validate_access_login` con el flujo correspondiente.
- Mantener la firma `lambda_handler(event, context)` y el retorno de policy IAM — esto garantiza que el mismo handler funcione en serverless y container sin ramas condicionales.

### Bypass durante Desarrollo Local
En el container, si necesitas saltarte la auth para debug:

```bash
AUTH_DISABLED=true uvicorn src.api_local.main_server:app
```

El middleware se vuelve passthrough.

### Acceso al Contexto del Authorizer dentro del Lambda

Después de un Allow, el bridge inyecta:

```python
request.state.authorizer = {
    "principalId": "user",
    "context": {"user": "<json string con atributos del usuario>"},
    "scheme": "principal_authorizer"
}
```

En modo container, si tu `lambda_handler` lee `event.requestContext.authorizer.context.user`, hay que propagarlo en el evento que el router le pasa. Esto **no es automático** hoy — ver issue abierto.

## Referencias

- [Lambda Authorizers - configuración completa](lambda-authorizers.md)
- [Comandos de Proyecto](project.md)
- [Comandos de Endpoint](endpoint.md)
- [AWS Lambda Authorizers Documentation](https://docs.aws.amazon.com/apigateway/latest/developerguide/apigateway-use-lambda-authorizer.html)

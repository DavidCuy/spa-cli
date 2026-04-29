# spa-cli — Feature Ideas & Roadmap

> Ideas de nuevas funcionalidades para `spa-cli`, orientadas al stack AWS Lambda + API Gateway + Pulumi.
> Organizadas por categoría y prioridad aproximada.

---

## 🟢 Alta Prioridad (quick wins / alto valor)

### 1. Habilitar `spa model` (ya existe el código)
El grupo `model` está implementado en `spa_cli/src/model/model.py` pero está **comentado** en `cli.py`. Completar y habilitar los comandos `spa model new` y `spa model fromJson` para generar modelos ORM (SQLAlchemy), servicios y controllers desde templates o desde un archivo JSON.

**Comandos:**
```bash
spa model new --name Usuario
spa model fromJson --name Producto   # lee .spa/templates/json/producto.json
```

---

### 2. `spa project deploy` — Integración directa con Pulumi
Actualmente el flujo es `spa project build` → `cd build && pulumi up` (manual). Integrar el deploy desde el CLI.

**Comandos propuestos:**
```bash
spa project deploy                        # build + pulumi up
spa project deploy --stack prod           # especificar stack Pulumi
spa project deploy --preview              # solo pulumi preview (sin aplicar)
spa project deploy --no-build             # skip build, solo pulumi up
```

**Variables de entorno usadas:** las mismas que `build` (`ENVIRONMENT`, `APP_NAME`, `AWS_ACCOUNT_ID`, `AWS_REGION`).

---

### 3. `spa endpoint list` / `spa lambda list` — Introspección del proyecto
Listar los recursos definidos en el proyecto sin tener que navegar los directorios.

**Comandos:**
```bash
spa endpoint list
# Salida:
# METHOD  PATH                  LAMBDA NAME
# GET     /usuarios             listar_usuarios
# POST    /usuarios             crear_usuario
# GET     /usuarios/{id}        obtener_usuario

spa lambda list
# Salida:
# NAME                  TIPO
# procesar_cola_sqs     standalone (sin endpoint)
# listar_usuarios       endpoint (GET /usuarios)
```

---

### 4. `spa project test` — Ejecutar tests del proyecto
Ejecutar todos los `test_lambda_function.py` con pytest y mostrar resultados.

```bash
spa project test
spa project test --lambda-name listar_usuarios   # solo una lambda
spa project test --coverage                      # con reporte de cobertura
```

---

### 5. `spa project doctor` — Diagnóstico del entorno
Verificar que el entorno está listo para trabajar antes de comenzar.

**Checks propuestos:**
- Python >= 3.11 instalado
- `spa_project.toml` existe y es válido
- AWS credentials configuradas (`~/.aws/credentials` o variables de entorno)
- Pulumi instalado y autenticado
- `src/layers/` tiene la estructura esperada
- Todas las lambdas en `src/lambdas/` tienen `lambda_function.py` + `infra_config.py`

```bash
spa project doctor
# ✅ Python 3.11.9
# ✅ spa_project.toml encontrado
# ✅ AWS credentials: us-east-1 (cuenta: 123456789012)
# ✅ Pulumi 3.x instalado
# ⚠️  Lambda 'procesar_pago' sin test_lambda_function.py
```

---

### 6. `spa endpoint remove` / `spa lambda remove` — Eliminar recursos
Actualmente no hay forma de eliminar un endpoint o lambda desde el CLI. Hay que hacerlo manualmente.

```bash
spa endpoint remove --endpoint-name listar_usuarios
spa lambda remove --lambda-name procesar_cola_sqs
```

**Comportamiento:** elimina el directorio `src/lambdas/{name}/` con confirmación interactiva.

---

## 🟡 Prioridad Media

### 7. Triggers para lambdas standalone — `spa lambda add --trigger`
Las lambdas standalone (`spa lambda add`) no tienen integración con servicios AWS. Agregar soporte para generar la configuración de `infra_config.py` según el trigger deseado.

**Triggers propuestos:**
```bash
spa lambda add --lambda-name procesar_mensajes --trigger sqs
spa lambda add --lambda-name procesar_archivos --trigger s3
spa lambda add --lambda-name tarea_diaria      --trigger schedule --schedule "rate(1 day)"
spa lambda add --lambda-name sync_db           --trigger dynamodb-stream
spa lambda add --lambda-name notificaciones    --trigger sns
```

Cada trigger generaría el bloque Pulumi correspondiente en `infra_config.py` (e.g., `aws.lambda_.EventSourceMapping` para SQS/DynamoDB, `aws.cloudwatch.EventRuleEventSubscription` para schedules).

---

### 8. ~~`spa auth add` — Wizard para Lambda Authorizers~~ ✅ Implementado como `spa authorizer add`

**Implementado** en branch `feat/fast-api-deploy`. Comando real:

```bash
spa authorizer add NAME [--role-name ROLE] [--lambda-name LAMBDA]
```

Genera `src/authorizers/<NAME>/handler.py` (template Cognito + IAM policy) y registra `[spa.api.lambda-authorizers.<NAME>]` en `spa_project.toml` con `module` apuntando al handler. El mismo handler corre como Lambda real (modo serverless) o como middleware FastAPI vía `auth_bridge.py` (modo container).

Pendiente futuro (no incluido en la implementación inicial):
- Modificar también `api.yaml` automáticamente para agregar el `securityScheme` correspondiente.
- Wizard interactivo con prompts (hoy solo args/flags).
- Soporte para tipo `request` (hoy template asume tipo `token`).

Ver [authorizer.md](authorizer.md) y [lambda-authorizers.md](lambda-authorizers.md#middleware-fastapi-modo-container).

---

### 9. `spa layer add` — Crear nueva layer personalizada
Agregar capas adicionales más allá de `databases` y `core`.

```bash
spa layer add --name utils          # crea src/layers/utils/python/core_utils/
spa layer add --name ml-inference   # crea src/layers/ml-inference/python/core_ml/
```

Genera la estructura de directorios, un `requirements.txt` vacío, y actualiza `spa_project.toml`.

---

### 10. `spa project validate` — Validar proyecto antes del build
Verificar consistencia del proyecto sin hacer el build completo.

**Validaciones:**
- Cada lambda en `src/lambdas/` tiene `lambda_function.py` con función `lambda_handler`
- Cada `endpoint.yaml` referencia un método HTTP válido
- El `api.yaml` base es YAML válido
- Los Lambda Authorizers configurados en `spa_project.toml` existen en `api.yaml`
- No hay nombres de lambda duplicados

```bash
spa project validate
# ✅ 5 lambdas validadas
# ✅ 4 endpoints con formato correcto
# ❌ Lambda 'crear_usuario': falta lambda_handler en lambda_function.py
```

---

### 11. Soporte para múltiples entornos en `spa_project.toml`
Actualmente el entorno se maneja solo vía variables de entorno. Agregar sección de entornos en el TOML.

```toml
[spa.environments.dev]
aws_region = "us-east-1"
aws_account_id = "123456789012"

[spa.environments.prod]
aws_region = "us-west-2"
aws_account_id = "987654321098"
```

```bash
spa project build --env prod
spa project deploy --env prod
```

---

### 12. `spa project logs` — Ver logs de CloudWatch
Consultar logs de una lambda directamente desde el CLI usando boto3/AWS SDK.

```bash
spa project logs --lambda-name listar_usuarios
spa project logs --lambda-name listar_usuarios --tail          # modo live
spa project logs --lambda-name listar_usuarios --since 1h     # última hora
spa project logs --lambda-name listar_usuarios --env prod
```

---

### 13. `spa lambda invoke` — Invocar lambda en AWS
Invocar una lambda desplegada en AWS con un payload de prueba.

```bash
spa lambda invoke --lambda-name listar_usuarios
spa lambda invoke --lambda-name listar_usuarios --payload '{"queryStringParameters": {"page": "1"}}'
spa lambda invoke --lambda-name procesar_cola_sqs --payload-file test_event.json
spa lambda invoke --lambda-name listar_usuarios --env prod
```

---

### 14. Soporte para DynamoDB como base de datos
Actualmente solo soporta MySQL y PostgreSQL. Agregar DynamoDB como opción serverless-native.

```bash
spa project init
# → Elija su motor de base de datos [mysql/postgresql/dynamodb]:
```

Generaría una layer `databases` con un ORM/wrapper para DynamoDB (e.g., usando `boto3` o `pynamodb`).

---

## 🔵 Baja Prioridad / Ideas Futuras

### 15. `spa project update` — Actualizar template del proyecto
Actualizar los archivos de la layer `core` a la versión más reciente del template, sin sobreescribir código de negocio.

```bash
spa project update
spa project update --pattern-version v2.1.0
```

---

### 16. `spa lambda trigger-local` — Simular eventos AWS localmente
Invocar una lambda localmente con un payload que simule un evento AWS específico.

```bash
spa lambda trigger-local --lambda-name procesar_cola_sqs --event sqs --messages 3
spa lambda trigger-local --lambda-name procesar_archivos --event s3 --bucket mi-bucket --key foto.jpg
spa lambda trigger-local --lambda-name tarea_diaria --event cloudwatch-scheduled
```

Genera un evento AWS sintético y llama al `lambda_handler` directamente, mostrando la respuesta.

---

### 17. CI/CD scaffolding — `spa project ci`
Generar archivos de configuración para pipelines CI/CD.

```bash
spa project ci --provider github-actions
spa project ci --provider gitlab-ci
spa project ci --provider aws-codepipeline
```

Genera un workflow que ejecuta `spa project build` + `pulumi up` en el pipeline, con los secrets AWS configurados.

---

### 18. `spa project watch` — Rebuild automático en desarrollo
Monitorear cambios en `src/` y hacer rebuild del router local automáticamente (complemento de `run-api`).

```bash
spa project watch   # detecta cambios en src/lambdas/ y regenera router.py
```

---

### 19. Soporte para Step Functions — `spa workflow add`
Generar scaffolding para workflows con AWS Step Functions.

```bash
spa workflow add --name procesar-orden
# Genera: src/workflows/procesar_orden/
#   ├── definition.json      # ASL (Amazon States Language)
#   ├── infra_config.py      # Pulumi StateMachine
#   └── lambdas/             # lambdas de los pasos del workflow
```

---

### 20. `spa endpoint mock` — Servidor mock con datos sintéticos
Levantar un servidor mock que responda con datos sintéticos basados en el schema OpenAPI, sin necesidad de implementar la lógica.

```bash
spa endpoint mock
# Levanta servidor en :8001 respondiendo con datos faker según openapi.json
```

---

## 📌 Deuda técnica / Mejoras internas

| Item | Descripción |
|------|-------------|
| `install_local_layers.py` | Migrar de `setup.py` (deprecado) a `pyproject.toml` + `pip install -e .` |
| `build.py` | Añadir paralelismo al build de múltiples layers con `concurrent.futures` |
| Manejo de errores | Mensajes de error más descriptivos con sugerencias de solución |
| Tests del CLI | Agregar tests de integración para los comandos principales |
| `spa_project.toml` | Validación con `pydantic` al cargarlo (actualmente falla silenciosamente con configs inválidas) |
| `--dry-run` flag | Agregar flag global `--dry-run` que muestre qué haría el comando sin ejecutarlo |

---

## 🏷️ Resumen por esfuerzo estimado

| Feature | Esfuerzo |
|---------|----------|
| Habilitar `spa model` | Bajo (código ya existe) |
| `spa endpoint list` / `spa lambda list` | Bajo |
| `spa project test` | Bajo |
| `spa endpoint remove` / `spa lambda remove` | Bajo |
| `spa project validate` | Medio |
| `spa project doctor` | Medio |
| ~~`spa auth add` wizard~~ → `spa authorizer add` | ✅ Hecho |
| `spa layer add` | Medio |
| `spa project deploy` (Pulumi) | Medio-Alto |
| Triggers en `lambda add` | Medio-Alto |
| Soporte multi-entorno | Medio-Alto |
| `spa project logs` (CloudWatch) | Alto |
| `spa lambda invoke` (AWS) | Alto |
| Soporte DynamoDB | Alto |
| CI/CD scaffolding | Alto |
| Step Functions | Muy alto |

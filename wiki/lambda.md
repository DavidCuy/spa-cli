# Comandos de Lambda - `spa lambda`

Los comandos de lambda en spa-cli permiten crear y gestionar funciones AWS Lambda sin endpoints HTTP asociados. Estas funciones son útiles para tareas en background, procesamiento de eventos, manejo de colas SQS, triggers de CloudWatch y más.

## Descripción General

Los comandos del módulo `lambda` se enfocan en crear funciones Lambda especializadas para procesamiento asíncrono, no relacionados directamente con endpoints REST API.

## Subcomandos Disponibles

### `spa lambda add`

**Crea una nueva función Lambda standalone**

Este comando genera una función Lambda completa con su configuración de infraestructura y archivos de prueba, pero sin endpoint HTTP asociado.

#### Sintaxis
```bash
spa lambda add --lambda-name LAMBDA_NAME
```

#### Parámetros

| Parámetro | Descripción | Valores Válidos | Requerido |
|-----------|-------------|-----------------|-----------|
| `--lambda-name` | Nombre de la función Lambda | Cualquier nombre válido de Python (se normaliza automáticamente) | ✅ Sí |

#### Funcionamiento Detallado

1. **Validación y normalización de nombres**: Convierte espacios y guiones a guiones bajos
2. **Verificación de existencia**: Evita duplicados en el directorio de lambdas
3. **Generación de archivos**: Crea estructura completa de la función Lambda
4. **Configuración de infraestructura**: Establece el entorno CloudWatch adecuado

#### Archivos Generados

Cada función Lambda crea la siguiente estructura en `src/lambdas/[lambda_name]/`:

```
src/lambdas/[lambda_name]/
├── lambda_function.py       # Handler principal de la función
├── test_lambda_function.py  # Archivo de pruebas unitarias
└── infra_config.py         # Configuración de infraestructura
```

**Nota:** No se genera `endpoint.yaml` ya que estas funciones no están expuestas mediante HTTP.

#### Ejemplos de Uso

##### Ejemplo 1: Función de procesamiento de datos
```bash
spa lambda add --lambda-name procesar_datos
```

**Uso típico:** Procesar logs, transformar datos, análisis en batch.

##### Ejemplo 2: Función de envío de notificaciones
```bash
spa lambda add --lambda-name enviar_notificaciones
```

**Uso típico:** Envío de emails, SMS, push notifications.

##### Ejemplo 3: Función de limpieza y mantenimiento
```bash
spa lambda add --lambda-name limpiar_datos_antiguos
```

**Uso típico:** Cleanup de archivos temporales, limpieza de cache, purgado de logs.

##### Ejemplo 4: Función de procesamiento de imágenes
```bash
spa lambda add --lambda-name procesar_imagenes
```

**Uso típico:** Redimensionar, optimizar, aplicar filtros a imágenes.

##### Ejemplo 5: Función de sincronización de datos
```bash
spa lambda add --lambda-name sincronizar_datos
```

**Uso típico:** Sincronización entre bases de datos, backup, replicación de datos.

##### Ejemplo 6: Manejo de nombres con espacios/guiones
```bash
spa lambda add --lambda-name "procesar-facturas AWAY"
```

**Resultado:** Función Lambda `procesar_facturas_AWAY`

#### Contenido de los Archivos Generados

##### `lambda_function.py`
```python
import json

def lambda_handler(event, context):
    """
    Handler principal de la función Lambda.
    
    Args:
        event: Datos del evento que trigger la función
        context: Contexto de ejecución de Lambda
        
    Returns:
        dict: Resultado del procesamiento
    """
    
    try:
        # Tu lógica de procesamiento aquí
        print(f"Evento recibido: {json.dumps(event)}")
        
        # Ejemplo de procesamiento
        resultado = procesar_evento(event)
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'Procesamiento completado',
                'resultado': resultado
            })
        }
        
    except Exception as e:
        print(f"Error en procesamiento: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': 'Error en procesamiento',
                'details': str(e)
            })
        }

def procesar_evento(event_data):
    """
    Lógica específica de procesamiento.
    Implementar según necesidades específicas.
    """
    # Implementación personalizada
    return {"success": True}
```

##### `test_lambda_function.py`
```python
import pytest
from lambda_function import lambda_handler

def test_procesar_datos_basic():
    """Test básico de la función de procesamiento."""
    event = {
        "example": "data",
        "timestamp": "2023-12-01T00:00:00Z"
    }
    
    result = lambda_handler(event, None)
    
    assert result['statusCode'] == 200
    assert 'body' in result
    assert 'success' in result['body']

def test_procesar_datos_with_error():
    """Test de manejo de errores."""
    event = None  # Evento de prueba que puede causar error
    
    result = lambda_handler(event, None)
    
    assert result['statusCode'] in [200, 500]  # Respuesta esperada
```

##### `infra_config.py`
```python
lambda_name = "procesar_datos"
camel_name = "ProcesarDatos"

def get_lambda_config():
    """Configuración específica de infraestructura."""
    return {
        "function_name": lambda_name,
        "handler": "lambda_function.lambda_handler",
        "description": f"Lambda function for {camel_name} - Background processing",
        "timeout": 900,  # 15 minutos
        "memory": 128,   # MB
        "environment": {
            "ENVIRONMENT": "development"
        },
        "events": [
            # Definir triggers específicos según necesidad
            # Ejemplo para CloudWatch Events
            {
                "source": "aws.events",
                "detail-type": "Scheduled Rule"
            }
        ]
    }

def get_xray_config():
    """Configuración para AWS X-Ray tracing."""
    return {
        "tracing": {
            "mode": "Active"
        }
    }
```

## Diferencia entre Endpoints y Lambdas

### Endpoints (`spa endpoint`)
- **Exposición HTTP**: Expuestos mediante API Gateway
- **REST API**: Respuesta directa a requests HTTP
- **Tiempo real**: Respuesta inmediata al cliente
- **Archivos adicionales**: `endpoint.yaml`

### Lambdas (`spa lambda`)  
- **Background processing**: Ejecución no bloqueante
- **Event-driven**: Triggereados por eventos específicos
- **Asíncronos**: Procesamiento en segundo plano
- **Sin exposición web**: No accesibles vía HTTP

## Casos de Uso Específicos

### Lambda de Procesamiento Automation

```bash
# Lambda para el mantenimiento automático de BD
spa lambda add --lambda-name limpiar_logs_antiguos
spa lambda add --lambda-name actualizar_estadisticas
spa lambda add --lambda-name vencer_cache_obsoleto
```

### Lambda de Integración con Servicios Externos

```bash
# Integraciones con APIs externas
spa lambda add --lambda-name sincronizar_datos_salesforce
spa lambda add --lambda-name procesar_pedidos_paypal
spa lambda add --lambda-name enviar_metricas_datadog
```

### Lambda de Procesamiento de Archivos

```bash
# Manejo de archivos en S3
spa lambda add --lambda-name procesar_imagenes_s3
spa lambda add --lambda-name comprimir_documentos
spa lambda add --lambda-name generar_thumbnails
```

### Lambda de Procesamiento de Mensajes

```bash
# Procesamiento de colas SQS/SNS
spa lambda add --lambda-name procesar_cola_pedidos
spa lambda add --lambda-name procesar_notificaciones
spa lambda add --lambda-name parsear_webhooks
```

## Configuraciones Avanzadas

### Personalización del Handler

Una vez generada la función, puedes modificar `lambda_function.py`:

```python
import json
import boto3

def lambda_handler(event, context):
    """Ejemplo de Lambda para procesar eventos de S3."""
    
    # Lógica para procesar evento de S3
    if 'Records' in event:
        for record in event['Records']:
            if record['eventSource'] == 'aws:s3':
                bucket_name = record['s3']['bucket']['name']
                object_key = record['s3']['object']['key']
                
                # Procesar archivo
                procesar_archivo_s3(bucket_name, object_key)
    
    return {'statusCode': 200, 'body': 'processed'}
```

### Configuración de Trigger

Modifica `infra_config.py` para configurar triggers específicos:

```python
def get_lambda_config():
    return {
        "function_name": "procesar_imagenes_s3",
        "handler": "lambda_function.lambda_handler",
        "timeout": 300,
        "environment": {
            "BUCKET_ORIGEN": "uploads-images",
            "BUCKET_DESTINO": "processed-images"
        },
        # Configuración para trigger de S3
        "s3_triggers": [{
            "bucket": "uploads-images",
            "event": "s3:ObjectCreated:*",
            "prefix": "images/"
        }]
    }
```

## Testing y Debugging

### Testing Local

```python
# test_lambda_function.py mejorado
import json

def test_processing_complete():
    """Test completo del procesamiento."""
    # Configurar datos de evento de prueba
    test_event = {
        "Records": [
            {
                "eventSource": "aws:s3",
                "s3": {
                    "bucket": {"name": "test-bucket"},
                    "object": {"key": "test-image.jpg"}
                }
            }
        ]
    }
    
    # Ejecutar función
    result = lambda_handler(test_event, None)
    
    # Verificar resultado
    assert result['statusCode'] == 200
    response_body = json.loads(result['body'])
    assert 'success' in response_body
```

### Debugging en Development

```python
def lambda_handler(event, context):
    try:
        # Logging detallado
        print(f"Evento recibido: {json.dumps(event, indent=2)}")
        
        # Procesar lógica principal
        resultado = tu_logica_procesamiento(event)
        
        print(f"Procesamiento completado: {resultado}")
        
        return {
            'statusCode': 200,
            'body': json.dumps(resultado)
        }
    except Exception as e:
        print(f"Error crítico: {e}")
        raise  # Re-lanzar para que CloudWatch capture
```

## Integración con Eventos AWS

### CloudWatch Events (Scheduled)
```python
# Manejo de eventos programados
def lambda_handler(event, context):
    if event['source'] == 'aws.events':
        if event['detail-type'] == 'Scheduled Rule':
            ejecutar_mantenimiento_programado()
```

### SQS Integration
```python
# Procesamiento de mensajes SQS
def lambda_handler(event, context):
    for record in event['Records']:
        message = json.loads(record['body'])
        procesar_mensaje_sqs(message)
```

### DynamoDB Streams
```python
# Procesamiento de cambios en DynamoDB
def lambda_handler(event, context):
    for record in event['Records']:
        if record['eventName'] == 'INSERT':
            procesar_nuevo_registro(record['dynamodb']['NewImage'])
```

## Deployment y Configuración de Infraestructura

### CloudFormation/SAM Template Generation

El comando `spa lambda add` automáticamente:

1. **Genera configuración de infraestructura** en `infra_config.py`
2. **Se integra con el sistema de build** de spa-cli
3. **Prepara templates** para deployment
4. **Configura triggers automáticamente**

### Archive y Dependencies Packaging

Al ejecutar `spa project build`, las lambdas standalone son:

- **Empaquetadas junto con sus dependencias**
- **Configuradas para deployment separado**
- **Integradas en el stack de infraestructura**

### Build Process Integration

```bash
# Flujo completo para lambda standalone
spa lambda add --lambda-name procesar_facturas
# Desarrollar lógica personalizada en lambda_function.py
spa project build  # Incluye la nueva lambda
```

## Mejores Prácticas

### Naming Convention
- **Descriptivo del propósito**: `procesar_pagos` vs `lambda1`
- **Específico pero conciso**: `enviar_notificaciones_push` vs `nots`
- **Consistente entre el proyecto**: Usar patrón establecido

### Error Handling
```python
def lambda_handler(event, context):
    try:
        # Procesamiento principal
        return procesar_evento(event)
    except ValidacionError as e:
        # Errores de validación - no reintentar
        return manejar_error_validacion(e)
    except RecoverableError as e:
        # Errores recuperables - AWS retry automático
        raise
    except Exception as e:
        # Errores inesperados
        logger.error(f"Error no esperado: {e}")
        return {'error': 'Procesamiento fallado'}
```

### Performance Optimization
```python
def lambda_handler(event, context):
    # Singleton para recursos externos costosos
    # (crear conexión BD, inicializar ML model)
    cliente_bd = obtener_cliente_bd()
    
    # Procesar evento
    return procesar_completo(event, cliente_bd)
```

### Monitoring y Logging
```python
import json
from datetime import datetime

def lambda_handler(event, context):
    inicio = datetime.now()
    
    try:
        resultado = procesar(event)
        
        # Logging de éxito
        logger.info({
            "proceso": "completed",
            "duration": (datetime.now() - inicio).total_seconds(),
            "resultado": resultado
        })
        
        return resultado
        
    except Exception as e:
        # Logging de errores
        logger.error({
            "proceso": "failed",
            "duration": (datetime.now() - inicio).total_seconds(),
            "error": str(e),
            "context": context
        })
        raise
```

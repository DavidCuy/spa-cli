# Comandos de Modelo - `spa model`

> **⚠️ Estado:** Esta funcionalidad está implementada pero no habilitada en la versión actual de spa-cli. Estará disponible en futuras versiones.

Los comandos de modelo en spa-cli permiten gestionar modelos de datos de manera automática, incluyendo su creación desde archivos JSON y generación del código base necesario.

## Descripción General

El módulo `model` automatiza la creación de modelos de datos cuyas características principales incluyen:

- **Creación de modelos ORM**: Generación automática de clases SQLAlchemy
- **Mantenimiento de coherencia**: Base de datos y código siempre sincronizados
- **Template generation**: Servicios y controladores asociados automáticos
- **Validación automática de tipos**: Interpretación de JSON para tipos de datos

## Subcomandos Disponibles

### `spa model new`

**Crea un nuevo modelo de datos desde cero**

Crea un nuevo modelo completo con estructura ORM estándar de SQLAlchemy.

#### Sintaxis
```bash
spa model new --name NAME [--tablename TABLENAME]
```

#### Parámetros

| Parámetro | Descripción | Valores Válidos | Requerido |
|-----------|-------------|-----------------|-----------|
| `--name` | Nombre del modelo (PascalCase automático) | Cualquier nombre válido | ✅ Sí |
| `--tablename` | Nombre específico de tabla en BD | String o mismo nombre del modelo | ❌ No |

#### Funcionamiento
1. **Generación del modelo SQLAlchemy** con estructura básica
2. **Creación de service layer** asociado
3. **Generación de controller** específico
4. **Configuración automática de rutas**
5. **Integración automática al proyecto**

#### Archivos Generados
```
src/layers/databases/python/core_db/models/
└── Usuario.py

src/layers/databases/python/core_db/services/
└── UsuarioService.py

src/layers/core/python/core_http/controllers/
└── UsuarioController.py

src/lambdas/
└── usuario_router.py
```

#### Ejemplo Básico

```bash
spa model new --name Usuario
```

Genera **Usuario.py** con:
```python
from sqlalchemy import Column, Integer, String, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Usuario(Base):
    __tablename__ = "Usuario"
    
    id = Column("IdUsuario", Integer, primary_key=True)
    
    def property_map(self) -> Dict:
        return {
            "id": "IdUsuario"
        }
    
    @classmethod
    def display_members(cls_) -> List[str]:
        return [
            "id"
        ]
```

---

### `spa model fromJson`

**Crea un modelo desde archivo JSON existente**

Este es el comando más versátil del módulo. Permite generar un modelo completo estudiando un archivo JSON y detectando automáticamente tipos y estructuras.

#### Sintaxis
```bash
spa model fromJson --name FILE_NAME [--tablename TABLENAME]
```

#### Parámetros

| Parámetro | Descripción | Valores Válidos | Requerido |
|-----------|-------------|-----------------|-----------|
| `--name` | Nombre del archivo JSON (sin extensión) | Archivo debe existir en `./.spa/templates/json` | ✅ Sí |
| `--tablename` | Nombre específico para tabla BD | String o mismo que modelo | ❌ No |

#### Ubicación del JSON
El archivo JSON debe ubicarse en:
```
proyecto/
└── .spa/
    └── templates/
        └── json/
            └── [nombre].json
```

#### Proceso de Interpretación

El comando realiza **inferencia automática de tipos** siguiendo estas reglas:

1. **Strings numéricos de fecha** → `DateTime` column
2. **Strings alfanuméricos** → `String` column
3. **Strings numéricos** → Type escalar apropiado
4. **Arrays/Objects** → `Text` (JSON) storage
5. **Detect auto-index**: Fuentes de ID component
6. **Normaliza naming**: camelCase en bases de datos

#### Ejemplos Completos

##### Ejemplo 1: Modelo Usuario desde JSON

**Archivo:** `.spa/templates/json/usuario.json`
```json
{
  "email": "juan@example.com",
  "nombre": "Juan Pérez",
  "fecha_nacimiento": "1990-05-15T10:30:00Z",
  "telefono": "123456789",
  "activo": true,
  "preferencias": {
    "tema": "oscuro",
    "idioma": "es"
  }
}
```

**Comando:**
```bash
spa model fromJson --name usuario
```

**Resultado generado (`Usuario.py`):**
```python
class Usuario(Base):
    __tablename__ = "Usuario"
    
    id = Column("IdUsuario", Integer, primary_key=True)
    email = Column("Email", String(255))
    nombre = Column("Nombre", String(255))
    fecha_nacimiento = Column("FechaNacimiento", DateTime)
    telefono = Column("Telefono", String(25))
    activo = Column("Activo", Boolean)
    preferencias = Column("Preferencias", Text)  # JSON as string
    
    def property_map(self) -> Dict:
        return {
            "id": "IdUsuario",
            "email": "Email",
            "nombre": "Nombre",
            "fecha_nacimiento": "FechaNacimiento",
            "telefono": "Telefono",
            "activo": "Activo",
            "preferencias": "Preferencias"
        }
    
    @classmethod
    def display_members(cls_) -> List[str]:
        return [
            "id",
            "email",
            "nombre",
            "fecha_nacimiento", 
            "telefono",
            "activo",
            "preferencias"
        ]
```

##### Ejemplo 2: Modelo Producto Complejo

**Archivo:** `.spa/templates/json/producto.json`
```json
{
  "nombre": "Laptop Gaming",
  "precio": 1500.99,
  "stock": 25,
  "categoria": {
    "id": 1,
    "nombre": "Electrónicos",
    "parent": null
  },
  "specs": [
    {"procesador": "Intel i7", "ram": 16},
    {"procesador": "AMD Ryzen", "ram": 32}
  ],
  "fecha_creacion": "2023-12-01T00:00:00Z"
}
```

**Comando:**
```bash
spa model fromJson --name producto --tablename Productos
```

**Resultado generado:**
```python
class Producto(Base):
    __tablename__ = "Productos"  # Usar nombre específico
    
    id = Column("IdProducto", Integer, primary_key=True)
    nombre = Column("Nombre", String(255))
    precio = Column("Precio", Float)
    stock = Column("Stock", Integer)
    categoria = Column("Categoria", Text)  # Nested object → JSON
    specs = Column("Specs", Text)          # Array → JSON  
    fecha_creacion = Column("FechaCreacion", DateTime)
```

## Estructura de Archivos JSON Esperada

### Formatos de Fecha Detectables
```json
{
  "timestamp_iso": "2023-12-01T10:30:00Z",
  "date_simple": "2023-12-01",
  "datetime_specific": "10:30 AM"
}
```

### Tipos de Datos Soportados
```json
{
  "string_text": "Texto normal",
  "numeric_int": 42,
  "numeric_float": 3.14159,
  "boolean_true": true,
  "boolean_false": false,
  "nested_object": {
    "field": "value"
  },
  "array_list": [1, 2, 3],
  "json_complex": {
    "nested_arrays": [[1,2], [3,4]],
    "mixed_types": {"str": "mixed", "num": 42}
  }
}
```

## File Requirements para fromJson

### Estructura de Directorio Requerida
```
proyecto/
├── .spa/
│   └── templates/
│       └── json/
│           ├── usuario.json
│           ├── producto.json
│           └── orden.json
```

### Constraints y Validaciones de JSON
1. **File must be valid JSON format**
2. **Must have object with key-value pairs** (not array)
3. **Should include sample of real data**
4. **Fieldnames should reflect database column conventions**
5. **Attempts to standardize casing (snake_case, camelCase)**

## Generación Automática de Archivos Adicionales

### Service Layer Resolution

Para cada modelo creado se genera correspondientemente:

#### UserService Autogeneration
Si `Usuario` es el modelo, crea:
```
src/layers/databases/python/core_db/services/UsuarioService.py
```

**Contenido típico:**
```python
from ..models.Usuario import Usuario

class UsuarioService:
    def __init__(self, session):
        self.session = session
    
    def create(self, **kwargs):
        user = Usuario(**kwargs)
        self.session.add(user)
        self.session.commit()
        return user
    
    def get(self, id):
        return self.session.query(Usuario).filter(Usuario.id == id).first()
```

#### Controller Layer Generation
Semanalmente en `aiacore/http`:
```
src/layers/core/python/core_http/controllers/UsuarioController.py
src/lambdas/usuario_router.py
```

### Integration Impact en Existing Project

El `fromJson new` actualiza:
```python
# __init__.py en src/actualizado automáticamente:
from .routes import usuario_router
app.register_blueprint(usuario_router, url_prefix='/usuario')
```

## Flujo de Trabajo Completo

### Caso Práctico de Trabajo con Modelos

1. **Preparar datos de entrada JSON**:
```bash
mkdir -p .spa/templates/json
cat > usuario_spec.json <<EOF
{
  "email": "user@email.com",
  "nombre": "Juan",
  "categoria": {"tipo": "premium"},
  "registro": "2023/12/01"
}  
EOF
```

2. **Ejecutar generación desde JSON**:
```bash
spa model fromJson --name usuario_spec
# spa note: generaría UsuarioSpec.py con
# automatic typing + services layer
```

3. **Modifications and refinements** según necesidad

### Relaciones Entre Modelos

#### Ejemplo de Relación Foreign Key - `fromJSON`

Si crear models con relaciones implica:
```json
# categoria.json has estructural relation example:
{
  "parent_id": null,
  "parent_ref": 5,  // future reference relation
  "images_base": ["https://bucket..."],
  "time_meta": {"inserted": "timestamp..."}
}
```

Post-Generation → **You end up** with:
`Categoria.parent_ref = ForeignKey("categories.id")` representation automatic.

## Casos Avanzados

### Model fromJSON with Relations Sample

Un modelo más complejo que demuestra relación entre resources:

**.spa/templates/json/orden.json**
```json
{ 
   "idcliente": 1234,
   "items": [
      {"product": {"number": 12, "quantity": 2}},
      {"product": {"number": 53, "quantity": 1}}
   ],
   "total": 199.99,
   "created_ts": "2023-12-01 10:00",
   "billing_address": {
     "street": "...",
     "country": "Germany"
   }
}
```

Running same sistema como anterior →

**generation automáticaincludes:**

- Foreign relation `orden.idcliente → clientes.id`
- Nested JSON ⊆️ all `billing_address` data
- Structural `items_prologos` treated as Text/JSON because `array_spec`.

```python
class Orden(Base):
    __tablename__ = "Orden"
    
    id = Column("IdOrden", Integer, primary_key=True)
    idcliente = Column("IdCliente", Integer)  # Future FK
    items = Column("Items", Text)
    total = Column("Total", Numeric(10, 2))
    created_ts = Column("CreatedTs", DateTime)
    billing_address = Column("BillingAddress", Text)
```

```bash
# Test the process fully:
spa project init
spa model fromJson --name orden --tablename OrdenFull
```

## Error Handling

### Erros expected during JSON parsing:

```bash
spa model fromJson --n No-no  ## Error located: loader double label name file presence.

spa model fromJson --name nom_not_in_folder  ## Error : path doesn't exist.
spa model fromJson --name MyModel  ## file mymodel.json missing - FileNotFound error.
```

### Valid failure conditions:
- **Invalid JSON syntax** → Error: "No se pudo leer el json correctamente"
- **File doesn't exist in ./spa-cli/.spa/templates/json directory"
- **Invalid object structure** → Expected key-value pairs, not arrays


### Best practices for JSON files collection:

```bash
     1) Ensure project is initiated  ✓ spa project init

      2) Place JSON inside location............ ./spa_cli/.spa/templates/json

      3) Name should be file without extension:

               spa model fromJson --name caliber # without (.json) suffix.
```

```
          spa model fromJson --name number --> expects .spa/templates/json/number.json
```

Consistent naming:

- Validate that `usuario.json` corresponds ultimately to --name parameter manager usage.

Best practices for model creation include:

**Structure Data Placement:**
- JSON sample files should be placed in `.spa/templates/json/`
- File naming matches the `--name` parameter exactly
- JSON objects should represent real-world data samples

**Integration Benefits:**
- Accelerated model development
- Consistent SQLAlchemy ORM generation
- Automatic service layer generation
- Controller integration routes

**Development Workflow:**
```bash
# Complete modeling workflow:
spa project init
# Prepare model data
mkdir -p .spa/templates/json
# Create sample JSON
echo '{"name":"Sample","active":true}' > .spa/templates/json/model_spec.json
# Generate model structure
spa model fromJson --name model_spec --tablename data_model
```

## Beneficios Avanzados

- **Speeding Development Cycle**: Visualization automático hace modelo+code->database → consistency enforcement
- **Database Code Synchronization**: Runtime module always corresponds a DB estado
- **Validation Alerting**: Automatic mismatch acceso model  definition → JSON data (!= BD estuado)
- **ORM Objects Management**: Seguro override personas modification
- **Future Schema Evolution**: Plan for changes but never disrupt objeto development ambiente
# Deploy AWS Serverless — spa-cli + Pulumi

Flujo completo para deployar un proyecto spa-cli a AWS.

> Pre-requisitos: `spa learn aws-prereqs`

---

## 1. Variables de entorno antes del build

El build genera `openapi.json` con los ARNs de Lambda y API Gateway. Si las variables no están seteadas, usa valores placeholder (`myapp`, `123456789012`) que causan error `AccessDeniedException: Cross-account pass role` al hacer `pulumi up`.

Setea antes de buildear:

```bash
# Linux / macOS
export AWS_ACCOUNT_ID="<tu-account-id>"
export APP_NAME="<nombre-del-proyecto>"
export ENVIRONMENT="dev"
export AWS_REGION="us-east-1"
```

```powershell
# Windows PowerShell
$env:AWS_ACCOUNT_ID = "<tu-account-id>"
$env:APP_NAME = "<nombre-del-proyecto>"
$env:ENVIRONMENT = "dev"
$env:AWS_REGION = "us-east-1"
```

Verifica tu account ID:

```bash
aws sts get-caller-identity --query Account --output text
```

---

## 2. Lambda corre en Amazon Linux — librerías nativas

Las funciones Lambda ejecutan en **Amazon Linux 2023 (x86_64)**. Las librerías con extensiones C (como `psycopg2`, `cryptography`, `numpy`) deben estar compiladas para ese SO.

Si buildeas en Windows o macOS e instalas las dependencias normalmente, subirás binarios incompatibles y Lambda fallará con:

```
Runtime.ImportModuleError: Unable to import module 'function': No module named 'psycopg2._psycopg'
```

`spa project build` maneja esto automáticamente usando el flag `--platform manylinux2014_x86_64` al instalar las dependencias del layer. No necesitas hacer nada extra — solo asegúrate de buildear con `spa project build` y no instalar dependencias del layer manualmente.

> Si agregas una librería nativa nueva al `requirements.txt` del layer, siempre rebuildea con `spa project build` antes de `pulumi up`.

---

## 3. Build del proyecto

```bash
spa project build --yes
```

Genera la carpeta `build/` con:
- Layers instalados y comprimidos
- Lambdas empaquetadas
- `openapi.json` con ARNs correctos para el API Gateway
- Infra de Pulumi lista para deploy

---

## 4. Conectar Pulumi al backend S3

```bash
pulumi login s3://<project>-pulumi-state
```

Solo necesario la primera vez por sesión (o si cambiaste de backend).

---

## 5. Seleccionar o inicializar el stack

Si el stack ya existe:

```bash
cd build
pulumi stack select prod
```

Si es el primer deploy (stack nuevo):

```bash
cd build
pulumi stack init prod --secrets-provider="awskms://alias/<project>-pulumi"
```

---

## 6. Configurar variables del stack

```bash
pulumi config set project:env prod
pulumi config set aws:region us-east-1
```

Agrega secrets (cifrados con KMS):

```bash
pulumi config set --secret project:db_password "tu_password"
```

---

## 7. Deploy

```bash
pulumi up
```

Pulumi muestra el plan de cambios. Confirma con `yes`.

Para deploy sin confirmación:

```bash
pulumi up --yes
```

---

## Flujo completo (resumen)

```bash
# 1. Vars de entorno (crítico — sin esto openapi.json queda con placeholders)
export AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
export APP_NAME="<nombre-del-proyecto>"
export ENVIRONMENT="dev"
export AWS_REGION="us-east-1"

# 2. Build
spa project build --yes

# 3. Deploy
pulumi login s3://<project>-pulumi-state
cd build
pulumi stack select dev   # o: pulumi stack init dev --secrets-provider="awskms://alias/<project>-pulumi"
pulumi config set project:env dev
pulumi config set aws:region us-east-1
pulumi up --yes
```

---

## Verificar deploy

```bash
# Ver outputs del stack (URL del API Gateway, ARNs, etc.)
pulumi stack output

# Ver estado actual
pulumi stack
```

---

## Solución de problemas

| Error | Causa | Solución |
|---|---|---|
| `AccessDeniedException: Cross-account pass role` | `openapi.json` generado con account ID placeholder | Setear `AWS_ACCOUNT_ID`, `APP_NAME`, `ENVIRONMENT` y rebuildear |
| `AccessDenied` | Permisos IAM insuficientes | Agregar permiso faltante al rol/usuario |
| `Stack not found` | Stack no inicializado | `pulumi stack init prod --secrets-provider=...` |
| `No valid credential sources` | Sin credenciales AWS activas | `aws configure` o exportar vars de entorno |
| `Checksum mismatch` | State corrupto o bucket equivocado | Verificar `pulumi login` apunta al bucket correcto |

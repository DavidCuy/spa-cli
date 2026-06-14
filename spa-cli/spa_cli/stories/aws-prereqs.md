# Pre-requisitos AWS — Deploy Serverless

Lo que necesitas en AWS antes de poder deployar un proyecto spa-cli con provider `aws`.

El flujo de deploy es:
1. `spa project build` — construye layers, lambdas y genera `build/`
2. `pulumi login s3://<bucket>` — conecta Pulumi al backend remoto
3. `pulumi up` — despliega la infra en AWS

> Esta guía crece conforme avanza el proyecto. Actualiza según lo que tu stack cree/elimine/modifique.

---

## 1. Credenciales AWS locales

Necesitas credenciales activas antes de correr cualquier comando.

```bash
aws configure
```

O con variables de entorno:

```bash
export AWS_ACCESS_KEY_ID=...
export AWS_SECRET_ACCESS_KEY=...
export AWS_REGION=us-east-1
```

Verifica:

```bash
aws sts get-caller-identity
```

---

## 2. Identidad IAM

Necesitas una identidad (usuario o rol) con permisos para todo lo que el stack crea/elimina/modifica.

Permisos mínimos base:

- `lambda:*` — crear/actualizar/eliminar funciones y layers
- `apigateway:*` — crear/modificar API Gateway
- `iam:PassRole`, `iam:GetRole`, `iam:CreateRole`, `iam:AttachRolePolicy`, `iam:PutRolePolicy` — roles de ejecución para Lambda
- `s3:*` en el bucket de Pulumi state
- `secretsmanager:GetSecretValue` — leer secretos desde Lambda
- `kms:Decrypt`, `kms:GenerateDataKey`, `kms:DescribeKey` — usar la llave KMS
- `logs:*` — CloudWatch Logs

> Los permisos exactos dependen de lo que tu `infra/` defina. Ajusta conforme el stack falle con `AccessDenied`.

---

## 3. Bucket S3 — estado de Pulumi

Pulumi necesita un backend remoto para guardar el state.

```bash
aws s3api create-bucket \
  --bucket <project>-pulumi-state \
  --region us-east-1

aws s3api put-bucket-versioning \
  --bucket <project>-pulumi-state \
  --versioning-configuration Status=Enabled
```

Conectar Pulumi al bucket:

```bash
pulumi login s3://<project>-pulumi-state
```

---

## 4. KMS Key — cifrado de secrets del stack

Pulumi cifra los secrets del stack con KMS.

```bash
# Crear llave
KEY_ID=$(aws kms create-key \
  --description "<project> pulumi secrets" \
  --key-usage ENCRYPT_DECRYPT \
  --query 'KeyMetadata.KeyId' \
  --output text)

# Crear alias
aws kms create-alias \
  --alias-name alias/<project>-pulumi \
  --target-key-id $KEY_ID
```

Al inicializar el stack por primera vez:

```bash
pulumi stack init prod --secrets-provider="awskms://alias/<project>-pulumi"
```

---

## 5. Secreto en Secrets Manager — credenciales de DB

Formato del nombre:

```
{Environment}-{project_name}-<nombre>
```

Ejemplo: `prod-myproject-db-credentials`

```json
{
  "username": "tu_usuario",
  "password": "tu_password",
  "host": "tu_host",
  "port": 5432,
  "dbname": "tu_base_de_datos",
  "engine": "postgresql"
}
```

```bash
aws secretsmanager create-secret \
  --name "prod-<project>-db-credentials" \
  --secret-string '{"username":"...","password":"...","host":"...","port":5432,"dbname":"...","engine":"postgresql"}'
```

> Lambda lee este secreto en runtime. No se usa durante el deploy.

---

## Checklist antes del primer deploy

- [ ] Credenciales AWS activas (`aws sts get-caller-identity` responde)
- [ ] Identidad IAM con permisos suficientes
- [ ] Bucket S3 para Pulumi state creado y versionado
- [ ] KMS key con alias creada
- [ ] Secreto DB creado en Secrets Manager con formato `{env}-{project}-*`

---

## Siguiente paso

Con los pre-requisitos listos:

```bash
spa project build --yes
pulumi login s3://<project>-pulumi-state
pulumi stack select prod   # o: pulumi stack init prod --secrets-provider="awskms://alias/<project>-pulumi"
pulumi up
```

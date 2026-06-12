# Configurar VPS en GCP — Free Tier

Cómo crear una VM gratuita en Google Cloud Platform para hospedar un proyecto container-cloud.

## Por qué GCP

El `e2-micro` de GCP en `us-central1` es **Always Free** — sin vencimiento, sin cobros mientras te mantengas en los límites:
- 1x instancia e2-micro
- 30 GB de disco estándar
- 1 GB de egress/mes

> Oracle Cloud free tier en regiones MX (Querétaro) está permanentemente saturado. GCP es la alternativa más confiable.

## 1. Crear la VM

Ve a **Compute Engine → VM Instances → Create Instance**:

| Campo | Valor |
|---|---|
| Región | `us-central1` (obligatorio para Always Free) |
| Zona | `us-central1-a` |
| Tipo de máquina | `e2-micro` |
| OS | Ubuntu 22.04 LTS |
| Tipo de disco | **Standard persistent** (no Balanced) |
| Tamaño de disco | 30 GB |
| Modelo de aprovisionamiento | **Estándar** (no Spot) |

> El estimado en la UI muestra ~$6 USD/mes — es el costo bruto sin aplicar el crédito Always Free. Cargo real: $0.

## 2. Agregar clave SSH

En la sección **Seguridad** → **Agregar claves SSH generadas manualmente** → pega tu clave pública.

Si no tienes una, generala:

```bash
ssh-keygen -t rsa -b 4096 -C "tu@email.com"
cat ~/.ssh/id_rsa.pub
```

GCP crea el usuario Linux a partir del comentario de la clave (último campo). Para `usuario@email.com` el usuario será `usuario`.

## 3. Abrir puertos en el firewall

**VPC Network → Firewall → Create Firewall Rule**:

| Campo | Valor |
|---|---|
| Dirección | Ingress |
| IP de origen | `0.0.0.0/0` |
| Protocolos/puertos | TCP: `22, 80, 8000` |

## 4. Conectar por SSH

```bash
ssh -i ~/.ssh/id_rsa tu_usuario@IP_EXTERNA
```

Para saber tu usuario: conéctate por el SSH del navegador en GCP Console y ejecuta `whoami`.

## 5. Instalar Docker

En la VM:

```bash
sudo apt update && sudo apt upgrade -y
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker $USER
```

Desconéctate y vuelve a conectar para que tome efecto el grupo, luego verifica:

```bash
docker --version
docker ps
```

## Siguiente paso

Con el VPS listo, sigue con el deploy: `spa tell-me a-story ansible-container-deploy`

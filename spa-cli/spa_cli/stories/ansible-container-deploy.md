# Deploy con Ansible — container-cloud

Cómo deployar un proyecto spa-cli `container-cloud` a un VPS usando Ansible.

## Requisitos previos

- VPS con Docker instalado → ver `spa tell-me a-story gcp-vps-setup`
- Imagen Docker publicada en DockerHub (`./publish.sh`)
- Ansible instalado localmente

## 1. Instalar Ansible

**Windows:** Ansible no corre nativamente en Windows. Usa WSL.

```bash
# En WSL
pip install ansible
```

**macOS/Linux:**

```bash
pip install ansible
```

## 2. Configurar inventory.ini

Copia el archivo de ejemplo:

```bash
cp ansible/inventory.ini.example ansible/inventory.ini
```

Edita `ansible/inventory.ini`:

```ini
[vps]
TU_IP_VPS ansible_user=TU_USUARIO ansible_ssh_private_key_file=~/.ssh/id_rsa
```

> `inventory.ini` está en `.gitignore` — nunca lo commitees (contiene IP y credenciales).

**Nota Windows/WSL:** Copia tu clave SSH a WSL:

```bash
cp /mnt/c/Users/<tu-usuario>/.ssh/id_rsa ~/.ssh/
chmod 600 ~/.ssh/id_rsa
```

## 3. Verificar conectividad

```bash
ansible -i ansible/inventory.ini vps -m ping
```

Respuesta esperada:

```
TU_IP | SUCCESS => { ... "ping": "pong" }
```

## 4. Configurar .env

Crea `.env` en la raíz del proyecto con tus variables de entorno:

```env
CLOUD_PROVIDER=container-cloud
DEFAULT_DATABASE_ENGINE=postgresql
DEFAULT_DATABASE_USERNAME=tu_usuario
DEFAULT_DATABASE_PASSWORD=tu_password
DEFAULT_DATABASE_HOST=tu_host
DEFAULT_DATABASE_PORT=5432
DEFAULT_DATABASE_NAME=tu_base_de_datos
```

> No uses interpolación `${VAR}` — Docker no expande variables shell en archivos env.
> La `EnvCredentialStrategy` construye el connection string de DB a partir de las vars individuales.

## 5. Deploy

```bash
ansible-playbook -i ansible/inventory.ini ansible/deploy.yml
```

El playbook ejecuta:
1. Copia `.env` → `/tmp/app.env` en el VPS
2. Pull de la imagen Docker más reciente desde DockerHub
3. Inicia/recrea el container (puerto 8000)
4. Elimina `/tmp/app.env` del VPS

## 6. Verificar

```bash
curl http://TU_IP_VPS:8000
curl http://TU_IP_VPS:8000/docs
```

## Solución de problemas

| Error | Causa | Solución |
|---|---|---|
| `Permission denied (publickey)` | Clave SSH no está en `authorized_keys` del VPS | Agregar clave via SSH del navegador en GCP Console |
| `No module named 'docker'` | Docker SDK faltante en el VPS | `sudo pip3 install docker` en el VPS |
| `Can't load plugin: sqlalchemy.dialects:postgresql.pymysql` | Driver de DB incorrecto | Verifica que `DEFAULT_DATABASE_ENGINE=postgresql` esté en `.env` |
| `FileNotFoundError: .env` | Ruta del env_file no existe | El playbook copia `.env` automáticamente — verifica que `.env` exista localmente |
| Ansible no corre en Windows | No soportado nativamente | Usa WSL |

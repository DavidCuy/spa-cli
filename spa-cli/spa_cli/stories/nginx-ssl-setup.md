# Nginx + SSL con Certbot en tu VPS

Cómo instalar nginx como reverse proxy y configurar HTTPS con Let's Encrypt.

## Requisitos previos

- VPS con Ubuntu 22.04 y Docker corriendo en puerto 8000
- DNS apuntando al VPS → ver `spa learn dns-setup`
- **Puertos 80 y 443 abiertos en el firewall del proveedor cloud**

> Si usas GCP: **VPC Network → Firewall → Create Rule** → TCP `80, 443`.
> Si usas AWS: **Security Groups → Inbound Rules** → TCP `80, 443`.
> Puerto 80 es obligatorio para que Certbot pueda validar el dominio (HTTP-01 challenge).

---

## 1. Instalar nginx

```bash
sudo apt install nginx -y
sudo systemctl enable nginx
sudo systemctl start nginx
```

## 2. Crear configuración del sitio

```bash
sudo nano /etc/nginx/sites-available/test.example.com
```

Contenido:

```nginx
server {
    listen 80;
    server_name test.example.com;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

## 3. Activar el sitio

```bash
sudo ln -s /etc/nginx/sites-available/test.example.com /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

Verifica HTTP antes de continuar:

```bash
curl http://test.example.com
```

---

## 4. Instalar Certbot

```bash
sudo apt install certbot python3-certbot-nginx -y
```

## 5. Obtener certificado SSL

```bash
sudo certbot --nginx -d test.example.com
```

Certbot:
1. Solicita tu email
2. Acepta términos de Let's Encrypt
3. Configura nginx automáticamente con SSL
4. Agrega redirect automático HTTP → HTTPS

## 6. Verificar

```bash
sudo nginx -t
sudo systemctl reload nginx

curl https://test.example.com       # debe responder con SSL
curl http://test.example.com        # debe redirigir a https
```

## 7. Renovación automática

Certbot instala un timer systemd automáticamente:

```bash
sudo systemctl status certbot.timer
```

Los certificados se renuevan solos antes de vencer (cada 90 días).

---

## Rewrite de rutas con prefijo de entorno

Si el backend espera un prefijo de entorno (ej. Lambda stage `/dev/`, `/prod/`), agrega un `rewrite` en `location /`:

```nginx
location / {
    rewrite ^/(.*)$ /dev/$1 break;

    proxy_pass http://localhost:8000;
    ...
}
```

`break` → aplica rewrite y detiene procesamiento. Query strings pasan automáticas.

> El valor `/dev/` viene de la variable `STAGE` (o equivalente) en tu `.env`.
> Ejemplos: `test-spa-cli.tulipan.mx/hello` → `localhost:8000/dev/hello`

Después de editar: `nginx -t && systemctl reload nginx`

---

## Solución de problemas

| Error | Causa | Solución |
|---|---|---|
| `Timeout during connect` en certbot | Puerto 80 bloqueado en firewall cloud | Abrir TCP 80 en reglas de firewall del proveedor |
| `nginx -t` falla | Error de sintaxis en config | Revisar el archivo en `sites-available/` |
| `502 Bad Gateway` | Container no corriendo en puerto 8000 | `docker ps` → verificar que el container esté `Up` |

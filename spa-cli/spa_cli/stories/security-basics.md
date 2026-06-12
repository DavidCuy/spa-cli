# Hardening nginx + fail2ban

Seguridad mínima para un VPS expuesto a internet. Basado en incidentes reales con bots escaneando paths de WordPress, PHP y exploits conocidos.

## Estrategia en capas

```
Atacante
   ↓
nginx :443
   ├── [Capa 1] Bloqueo por método HTTP inválido  → 444
   ├── [Capa 2] Bloqueo por query string maliciosa → 444
   ├── [Capa 3] Bloqueo por User-Agent de scanner  → 444
   ├── [Capa 4] Bloqueo por paths conocidos        → 444
   ├── [Capa 5] Rate limiting por IP               → 429
   └── [Capa 6] Log dedicado de bloqueos
              ↓
          fail2ban
           └── [Capa 7] Ban automático a IPs con 3+ hits bloqueados → iptables DROP
```

> `return 444` = nginx cierra la conexión sin responder. Cero CPU, cero bandwidth. Mejor que `404` que genera HTML.

---

## 1. Rate limit zone

Crea `/etc/nginx/conf.d/rate-limit.conf`:

```nginx
# 10MB ≈ 160k IPs en memoria. 30 req/s sostenido por IP.
limit_req_zone $binary_remote_addr zone=api_limit:10m rate=30r/s;
limit_req_status 429;

# Marca requests bloqueados para el scan log
map $status $is_blocked {
    default 0;
    "444"   1;
    "403"   1;
}
```

> `limit_req_zone` SOLO puede ir en el bloque `http {}`. Por eso va en `conf.d/` y no en el site config.

---

## 2. Configuración del site

Primero haz backup de la configuración existente:

```bash
sudo cp /etc/nginx/sites-available/test.example.com \
        /etc/nginx/sites-available/test.example.com.bak
```

Reemplaza el contenido de `/etc/nginx/sites-available/test.example.com`:

```nginx
server {
    server_name test.example.com;

    # Logs normales
    access_log /var/log/nginx/test-example_access.log;
    error_log  /var/log/nginx/test-example_error.log;

    # Log dedicado de bloqueos — funciona para if's a nivel server Y location
    # Clave: usar access_log con if=$is_blocked a nivel server, NO dentro de cada location
    access_log /var/log/nginx/test-example_scan.log combined if=$is_blocked;

    client_max_body_size 20M;

    # ---- Capa 1: Métodos HTTP no estándar ----
    # APIs REST solo usan GET/POST/PUT/PATCH/DELETE/OPTIONS/HEAD
    if ($request_method !~ ^(GET|POST|PUT|PATCH|DELETE|OPTIONS|HEAD)$) {
        return 444;
    }

    # ---- Capa 2: Query strings con vectores de ataque ----
    if ($args ~* "(php://|allow_url_include|auto_prepend_file|/etc/passwd|union.*select|<script|base64_decode)") {
        return 444;
    }

    # ---- Capa 3: User-Agents de scanners conocidos ----
    if ($http_user_agent ~* (nikto|sqlmap|nessus|whatweb|openvas|zgrab|masscan|nmap|dirbuster|gobuster|wpscan|libredtail)) {
        return 444;
    }

    # ---- Capa 4: Paths conocidos de escaneo ----

    # Scripts del lado del servidor que la API nunca expone
    location ~* \.(php|phps|phtml|asp|aspx|jsp|cgi|pl|sh|bash|env)$ {
        return 444;
    }

    # WordPress, paneles admin, dotfiles, frameworks vulnerables
    location ~* /(wp-admin|wp-content|wp-includes|wp-login|xmlrpc|phpmyadmin|adminer|\.env|\.git|\.htaccess|\.ssh|cgi-bin|actuator|swagger-ui|api-docs|geoserver|jenkins|solr|webui|debug|_ignition) {
        return 444;
    }

    # Archivos de backup / comprimidos
    location ~* \.(bak|backup|old|orig|sql|gz|tar|zip|rar|7z)$ {
        return 444;
    }

    # ---- Capa 5: Rate limiting + proxy al backend ----
    location / {
        limit_req zone=api_limit burst=20 nodelay;

        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Host              $host;
        proxy_set_header X-Real-IP         $remote_addr;
        proxy_set_header X-Forwarded-For   $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_connect_timeout 60s;
        proxy_send_timeout    60s;
        proxy_read_timeout    60s;
    }

    listen 443 ssl;
    # Certbot agrega los ssl_certificate y ssl_dhparam automáticamente
}

server {
    listen 80;
    server_name test.example.com;
    return 301 https://$host$request_uri;
}
```

---

## 3. Crear el scan log y recargar nginx

```bash
sudo touch /var/log/nginx/test-example_scan.log
sudo chown www-data:adm /var/log/nginx/test-example_scan.log
sudo nginx -t && sudo systemctl reload nginx
```

Verifica que el scan log funciona:

```bash
curl -sk https://test.example.com/wp-admin/test.php
sudo tail /var/log/nginx/test-example_scan.log
# Debe aparecer la línea con status 444
```

---

## 4. Instalar fail2ban

```bash
sudo apt install fail2ban -y
```

### Filtro: `/etc/fail2ban/filter.d/nginx-scan.conf`

```ini
[Definition]
# Matchea cualquier línea del scan log.
# Solo entran requests con 444/403 → 0% de falsos positivos.
failregex = ^<HOST> -.*"(GET|POST|HEAD|PUT|DELETE|OPTIONS|PATCH)[^"]*"\s(403|444)\s
ignoreregex =
datepattern = \[%%d/%%b/%%Y:%%H:%%M:%%S
```

### Jail principal: `/etc/fail2ban/jail.d/nginx-scan.conf`

```ini
[nginx-scan]
enabled  = true
port     = http,https
filter   = nginx-scan
logpath  = /var/log/nginx/test-example_scan.log
findtime = 600        ; ventana de 10 minutos
maxretry = 3          ; 3 hits bloqueados = ban
bantime  = 86400      ; 24 horas
backend  = polling
banaction = iptables-multiport

# Agrega tu IP pública aquí para no banearte tú mismo
ignoreip = 127.0.0.1/8 ::1
```

### Jail recidive: `/etc/fail2ban/jail.d/recidive.conf`

```ini
[recidive]
enabled  = true
logpath  = /var/log/fail2ban.log
banaction = iptables-allports
bantime  = 604800     ; 1 semana a todos los puertos
findtime = 86400      ; en las últimas 24h
maxretry = 3          ; 3 baneos = ban semanal
ignoreip = 127.0.0.1/8 ::1
```

### Arrancar fail2ban

```bash
sudo systemctl enable fail2ban
sudo systemctl start fail2ban
sudo fail2ban-client status
sudo fail2ban-client status nginx-scan
```

Verifica que `File list:` apunte al scan log correcto.

---

## 5. Verificar end-to-end

```bash
# Path bloqueado
curl -sk https://test.example.com/wp-admin/test.php

# Método inválido
curl -sk -X PROPFIND https://test.example.com/

# Query string maliciosa
curl -sk "https://test.example.com/?php://input"

# UA de scanner
curl -sk -A "nikto/2.0" https://test.example.com/
```

Todos deben devolver `curl: (52) Empty reply from server` (= 444).

```bash
sudo tail /var/log/nginx/test-example_scan.log   # deben aparecer los 4 hits
sudo fail2ban-client status nginx-scan            # debe mostrar bans activos
```

---

## Operación básica

```bash
# Ver IPs baneadas
sudo fail2ban-client status nginx-scan

# Desbanear una IP
sudo fail2ban-client set nginx-scan unbanip 1.2.3.4

# Banear manualmente
sudo fail2ban-client set nginx-scan banip 1.2.3.4

# Recargar después de editar filtros
sudo fail2ban-client reload
```

---

## Notas importantes

- Los `if` a nivel `server` se procesan **antes** que los `location`. Si usas `access_log` dentro de un `location`, los bloqueos por `if` no quedan registrados. Por eso el `map $status + access_log if=$is_blocked` a nivel `server` es el único patrón que captura todos los bloqueos.
- Revisa el `access.log` cada 1-2 semanas — los scanners rotan paths constantemente. Agrega paths nuevos a la blocklist según lo que veas.
- Si tienes integraciones externas (webhooks, SDKs), verifica que sus User-Agents no estén en la lista de bloqueo.

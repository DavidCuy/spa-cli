# Configurar DNS para tu VPS

Cómo apuntar un dominio o subdominio a tu VPS para que sea accesible por nombre.

## Requisitos previos

- VPS con IP pública (ej. `35.254.96.125`)
- Un dominio registrado

> Si no tienes dominio, puedes conseguir uno en: Cloudflare, Namecheap, GoDaddy, HostGator, Google Domains, entre otros. Precios desde ~$10 USD/año.

## Tipos de registro DNS

| Tipo | Para qué sirve |
|---|---|
| **A** | Apunta un nombre a una IP (IPv4) — el más común para VPS |
| **AAAA** | Apunta un nombre a una IPv6 |
| **CNAME** | Apunta un nombre a otro nombre (alias) — no uses para IP directa |

Para apuntar a tu VPS usa **registro A**.

## Crear el registro A

En el panel de DNS de tu proveedor (Route 53, Cloudflare, Namecheap, etc.):

| Campo | Valor |
|---|---|
| Nombre / Host | `test` (para `test.example.com`) o `@` (para `example.com` raíz) |
| Tipo | `A` |
| Valor / Dirección | `TU_IP_VPS` |
| TTL | `300` (5 min, recomendado para pruebas) |

Ejemplo para subdominio `test.example.com`:

```
test.example.com.   300   IN   A   35.254.96.125
```

## Verificar propagación

```bash
nslookup test.example.com
# o
dig test.example.com
```

Espera hasta ver tu IP en la respuesta. Con TTL 300 suele tardar 1-5 minutos.

```
Name:    test.example.com
Address: 35.254.96.125
```

> Si el cambio tarda más de 10 minutos, verifica que no haya un registro A previo con el mismo nombre que esté en caché.

## Siguiente paso

Con el DNS propagado, instala nginx y certbot para SSL: `spa learn nginx-ssl-setup`

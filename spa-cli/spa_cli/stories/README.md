# tell-me-a-story

Mini-tutoriales para cosas que necesitas configurar *fuera* de spa-cli para que tu proyecto funcione end-to-end.

## Guías disponibles

| Guía | Tema |
|---|---|
| [gcp-vps-setup.md](gcp-vps-setup.md) | Crear VM gratuita en GCP + instalar Docker + conectar por SSH |
| [ansible-container-deploy.md](ansible-container-deploy.md) | Deploy de proyecto container-cloud a VPS con Ansible |

## Uso

```bash
spa tell-me a-story                          # selector interactivo
spa tell-me a-story gcp-vps-setup            # leer + copiar al proyecto
spa tell-me a-story gcp-vps-setup --no-copy  # solo leer
spa tell-me list                             # listar disponibles
```

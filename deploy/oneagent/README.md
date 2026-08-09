# OneAgent — despliegue como contenedor

Este proyecto usa el patrón oficial de Dynatrace para desplegar OneAgent
como contenedor "full-stack" en el host donde corre Docker, de forma que
observa tanto el sistema operativo del host como todos los contenedores del
stack (`frontend`, `app`, `redis`, `load-generator`).

Referencia oficial: *Set up Dynatrace OneAgent as a Docker container*
(https://docs.dynatrace.com/docs/ingest-from/setup-on-container-platforms/docker/set-up-dynatrace-oneagent-as-docker-container).

## 1. Obtener credenciales del tenant

1. Crear o usar un tenant de Dynatrace (SaaS trial gratuito:
   https://www.dynatrace.com/trial/).
2. En el tenant, generar:
   - Un **token de instalación de OneAgent** (`ONEAGENT_INSTALLER_TOKEN`).
   - Un **token de API v2** (`DT_API_TOKEN`) con permisos de lectura de
     métricas/problemas y de gestión de Workflows (usado para desplegar
     `workflows/anomaly-auto-notify.json`).
3. Copiar la URL del entorno, por ejemplo `https://abc12345.live.dynatrace.com`,
   en `DT_ENVIRONMENT_URL`.

## 2. Completar el `.env`

En la raíz del repositorio:

```bash
cp .env.example .env
```

Completar `DT_ENVIRONMENT_URL`, `ONEAGENT_INSTALLER_TOKEN` y `DT_API_TOKEN`.

## 3. Notas sobre el contenedor de OneAgent

- Corre en modo `privileged`, con `pid: host` y `network_mode: host`, porque
  necesita instalar sus binarios en el sistema de archivos subyacente y leer
  `/proc`, `/sys` y los sockets de red del host —no solo del propio
  contenedor— para monitorear tanto el host como los demás contenedores.
- Esto es intencional y documentado por Dynatrace para este modo de
  despliegue; no se recomienda para nada que no sea el propio agente de
  observabilidad.
- Si el host no permite contenedores `privileged` (por ejemplo, algunos
  entornos gestionados), existe la alternativa de *application-only
  monitoring*, que inyecta el agente solo dentro de la imagen de `app` vía
  `oneagent-codemodules` en el `Dockerfile`, sin privilegios del host:

  ```dockerfile
  COPY --from=<DT_ENVIRONMENT_URL>/linux/oneagent-codemodules:python / /
  ENV LD_PRELOAD /opt/dynatrace/oneagent/agent/lib64/liboneagentproc.so
  ```

  Ver: https://docs.dynatrace.com/docs/ingest-from/setup-on-container-platforms/docker/set-up-oneagent-on-containers-for-application-only-monitoring

## 4. Verificación

Después de `docker compose up`, en Dynatrace: **Hosts** debería mostrar el
host donde corre Docker, y **Processes and containers** debería listar
`frontend`, `app` (una entrada por réplica), `redis` y `load-generator`.

---

[⬅ Volver al inicio](../../README.md)

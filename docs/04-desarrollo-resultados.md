# Semana 14 — Desarrollo y Análisis de Resultados

> Estado: la **mecánica del stack** (sección 0) y una **primera corrida real
> contra Dynatrace** (sección 3.1, 16 de agosto de 2026) ya se hicieron. La
> primera corrida detectó una anomalía real (`P-260849`) pero con
> limitaciones honestas (atribución a nivel de host, sin línea base previa).
> Falta una segunda corrida con línea base establecida para completar los
> escenarios 1, 2, 4 y 5. No se reportan aquí números inventados; todo lo
> que aparece en la sección 3 viene de la API v2 de Dynatrace o del propio
> stack.

## 0. Verificación de infraestructura (sin Dynatrace)

Antes de instrumentar con Dynatrace, se verificó que el stack de
[`deploy/`](../deploy/) funciona correctamente por sí solo (`docker compose
build` + `up --scale app=3`, sin el profile `with-oneagent`):

| Prueba | Resultado |
|---|---|
| Build de `app` y `load-generator` | ✅ Ambas imágenes construyen sin errores |
| Balanceo de carga (`frontend` → 3 réplicas de `app`) | ✅ Confirmado: requests sucesivos a `/` devolvieron 3 hostnames de contenedor distintos |
| Contador en `redis` por réplica (`/work`) | ✅ Confirmado: el contador se incrementa correctamente por hostname |
| `POST /chaos/cpu` | ✅ Confirmado con `docker stats`: la réplica objetivo subió a 100–111% de CPU durante la ventana solicitada |
| `POST /chaos/memory` | ✅ Confirmado: `mb_allocated` reportado coincide con lo solicitado |
| `load-generator` (tráfico normal + caos automático) | ✅ Confirmado en logs: alterna `[normal]` y `[chaos:cpu]`/`[chaos:memory]` según `CHAOS_PROBABILITY` |
| Caída de una réplica (`docker stop` sobre un contenedor `app`) | ⚠️ Ver hallazgo abajo |

**Hallazgo real (no un dato inventado):** al detener una réplica en pleno
tráfico, nginx **sí** redirige el tráfico nuevo hacia las réplicas activas
(0 fallos en 10 requests secuenciales de verificación manual), pero los
logs de `frontend` registraron **1 `upstream timed out`** durante la
ventana de transición, generado por una request del `load-generator` que
alcanzó a resolver la IP del contenedor ya detenido antes de que expirara
la caché DNS (`resolver ... valid=10s` en
[`deploy/nginx/nginx.conf`](../deploy/nginx/nginx.conf)). Es decir, el
tiempo de inactividad real de este diseño **no es cero**: está acotado por
ese TTL de resolución DNS, no por un health check activo. Esto es un
hallazgo genuino para la sección 3 (Escenario 4) y ya está anotado como
mejora propuesta en
[`docs/05-informe-final.md`](05-informe-final.md#7-discusión-y-mejoras-propuestas)
(pasar a un `upstream` con *passive health checks* o reducir el TTL del
resolver).

Estas pruebas se corrieron **sin** Dynatrace (fuera del alcance de este
entorno de ejecución, que no tiene el tenant del usuario). Confirman que el
stack está listo para instrumentarse; lo que sigue (secciones 1-3) requiere
correrlo contra un tenant real y capturar lo que ve Davis AI.

## 1. Experimentos planeados

| # | Escenario | Cómo se genera | Qué se espera observar en Dynatrace |
|---|---|---|---|
| 1 | Línea base de tráfico normal | `load-generator` con `CHAOS_PROBABILITY=0` durante ~30 min | Rango normal aprendido por Davis AI para tiempo de respuesta y uso de CPU/memoria |
| 2 | Pico de CPU en una réplica | `POST /chaos/cpu` en un contenedor `app` | Problema abierto por Davis AI, atribuido a la réplica específica (topología) |
| 3 | Pico de memoria | `POST /chaos/memory` | Problema abierto por Davis AI relacionado a saturación de memoria |
| 4 | Caída de una réplica | Detener un contenedor `app` en ejecución | Redistribución de tráfico por nginx hacia las réplicas activas; tiempo de inactividad medido |
| 5 | Saturación de `redis` | Generar carga de escritura elevada contra `redis` | Davis AI atribuye la latencia de `app` a la dependencia `redis` (causa raíz, no solo síntoma) |

## 2. Métricas a capturar

| Métrica | Fuente | Cómo se mide |
|---|---|---|
| Tiempo de respuesta (p50/p95) | Dynatrace (Service metrics) | Antes, durante y después de cada anomalía |
| Distribución del tráfico entre réplicas | nginx logs / Dynatrace Smartscape | % de requests por réplica |
| Tiempo de inactividad (downtime) | Dynatrace Availability / health checks de nginx | Duración entre falla y recuperación |
| Tiempo de detección de la anomalía (MTTD) | Timestamp del evento inyectado vs. timestamp del problema abierto por Davis AI | Diferencia en segundos |
| Tasa de falsos positivos/negativos | Comparación entre anomalías inyectadas y problemas abiertos | Conteo manual por escenario |

## 3. Resultados

### 3.1 Primera corrida real contra Dynatrace (16 de agosto de 2026)

Se corrió el stack en el host instrumentado con OneAgent (perfil sin
`with-oneagent`, ya que el agente ya estaba instalado en el host). Línea de
tiempo real (hora UTC, tomada directamente de la API v2 de Dynatrace, no
estimada):

| Hora (UTC) | Evento |
|---|---|
| 23:47:40 | `docker compose up --scale app=3 -d`: arrancan `frontend`, 3 réplicas de `app`, `redis`, `load-generator` |
| ~23:48 | OneAgent reporta `nginx`, `gunicorn` y `Redis` como entidades de proceso activas (confirmado vía `/api/v2/entities`) |
| **23:48:20** | **Davis AI abre `P-260849 "High Memory"`** (severidad `RESOURCE_CONTENTION`, nivel `INFRASTRUCTURE`), atribuido al host `fedora` |
| 23:51:06 | Se dispara caos controlado explícito: `POST /chaos/cpu?seconds=120&threads=4` |
| 23:51:11 / 23:51:16 | `POST /chaos/memory?mb=1024` (x2, sobre réplicas distintas por el balanceo) |
| — | `docker stats` confirma el impacto real: 2 de 3 réplicas al 100–111% de CPU, una reteniendo ~1 GB de memoria |
| — | `P-260849` sigue `OPEN`; **no se abre un problema nuevo** para el caos explícito de las 23:51 — se fusiona con el ya abierto |

**Lectura honesta de este resultado (no todo salió como en el plan original):**

- ✅ **Davis AI sí detectó una anomalía real de memoria**, en ~40 segundos
  desde que arrancó el stack (`23:47:40` → `23:48:20`) — esto valida el
  objetivo específico 4 del proyecto (detección automática de anomalías).
- ⚠️ La causa raíz quedó atribuida al **host completo** (`fedora`), no a un
  proceso/contenedor específico (`rootCauseEntity` vino vacío, con 1 sola
  evidencia de tipo `EVENT` a nivel de host). Explicación más probable:
  `gunicorn`/`nginx`/`Redis` eran entidades **recién creadas** en Dynatrace
  (minutos de antigüedad), sin historial suficiente para que Davis pudiera
  atribuirles una línea base propia y correlacionar la causa a nivel de
  proceso — con más tiempo de observación (línea base de horas/días, como
  contempla el Escenario 1 original) se esperaría una atribución más fina.
- ⚠️ El pico de CPU explícito (`/chaos/cpu`) **no generó un problema propio**
  en esta ventana corta (~5-10 min de observación). Es consistente con que
  Davis AI usa *baselining* adaptativo: sin suficiente historial, prefiere
  no abrir un problema de "High CPU" en vez de arriesgar un falso positivo.
- El problema de memoria fue causado principalmente por el **arranque
  simultáneo del stack** (3 réplicas de `gunicorn` + nginx + redis), no
  exclusivamente por la llamada explícita a `/chaos/memory` (que llegó 2m46s
  *después* de que el problema ya estaba abierto). El "experimento 3"
  original asumía una anomalía aislada sobre una línea base ya establecida;
  en la práctica, el simple hecho de instrumentar un stack nuevo ya generó
  suficiente presión de memoria para disparar la detección.

| Escenario | Tiempo de respuesta base | Tiempo de respuesta durante anomalía | MTTD | Downtime | Observaciones |
|---|---|---|---|---|---|
| 1 — Línea base | — | n/a | n/a | n/a | Pendiente: correr `CHAOS_PROBABILITY=0` por ~30 min antes del próximo experimento, para darle a Davis AI una línea base real por proceso |
| 2 — Pico de CPU | — | — (CPU real 100–111% confirmado por `docker stats`) | Sin problema abierto en esta corrida | — | Ver limitación de baselining arriba; repetir tras tener línea base |
| 3 — Pico de memoria | — | — | **~40s** (23:47:40 → 23:48:20), medido desde el arranque del stack, no desde la llamada explícita a `/chaos/memory` | — | Atribuido a nivel de host, no de contenedor (ver lectura honesta arriba) |
| 4 — Caída de réplica | — | — | — | Acotado por el TTL del resolver DNS (10s) — ver sección 0 | Verificado a nivel de infraestructura (sección 0); falta repetirlo con Dynatrace activo para ver si Davis AI también lo detecta como problema de disponibilidad |
| 5 — Saturación de `redis` | — | — | — | — | Pendiente de ejecutar |

**Pendiente para una segunda corrida** (con línea base ya establecida):
repetir los escenarios 1, 2, 4 y 5 después de dejar el stack corriendo con
tráfico normal por ~30-60 min, para poder comparar atribución de causa raíz
con y sin historial previo — ese contraste es en sí mismo un resultado
interesante para la discusión (Semana 15).

## 4. Ajustes a la metodología

*(Documentar aquí cualquier cambio necesario respecto al plan de la Semana
12, por ejemplo ajustes a `CHAOS_PROBABILITY`, duración de la línea base, o
cambios en los umbrales/sensibilidad de Davis AI.)*

---

[⬅ Volver al inicio](../README.md)

# Semana 14 — Desarrollo y Análisis de Resultados

> Estado: ✅ **Cerrado.** Se completaron la verificación de infraestructura
> (sección 0), la primera corrida sin línea base (sección 3.1, 16 de agosto)
> y la segunda corrida con línea base de 10 min (sección 3.2, 17 de agosto).
> Los 5 escenarios planeados se ejecutaron los cinco; no todos abrieron un
> problema en Dynatrace, y eso se documenta como resultado real, no como
> tarea pendiente. Todo lo que aparece en la sección 3 viene de la API v2
> de Dynatrace o de mediciones directas del propio stack — nada inventado.

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
| 1 — Línea base | **p50 = 80.2 ms, p95 = 143.0 ms** (n=1087 requests, 10 min) | n/a | n/a | n/a | Tráfico repartido ~34% / 32% / 34% entre las 3 réplicas (contadores de `redis`) |
| 2 — Pico de CPU (con línea base) | 80.2 ms | Impacto real confirmado (`docker stats`: réplica objetivo a 100%+ CPU) | **Sin problema abierto** en ~7 min de observación | — | Ver "Segunda corrida" abajo — resultado honesto, no lo que se esperaba |
| 3 — Pico de memoria (sin línea base, corrida 1) | — | — | **~40s** (23:47:40 → 23:48:20), medido desde el arranque del stack | — | Atribuido a nivel de host, no de contenedor |
| 3b — Pico de CPU (sin línea base, corrida 1) | — | 100–111% CPU confirmado | `P-260850 "CPU Saturation"` abierto **~4m45s** después del chaos | — | También a nivel de host |
| 4 — Caída de réplica (con Dynatrace activo) | — | — (0/10 fallos en verificación manual) | **Sin problema abierto** por Davis AI en ~3 min | Acotado por el TTL del resolver DNS (10s): 1 `upstream timed out` real registrado en logs de nginx | Davis AI no marcó la caída/recuperación de esta réplica como problema — ver discusión |
| 5 — Saturación de `redis` | avg 0.3 ms/op | **No se logró saturar**: `redis-benchmark -c 100` corrió a 163k–174k rps con latencia p50 ≈ 0.28 ms | n/a (sin anomalía real que detectar) | — | Limitación del diseño del experimento, no de Dynatrace — ver discusión |

### 3.2 Segunda corrida, con línea base establecida (17 de agosto de 2026)

Línea de tiempo real (UTC):

| Hora | Evento |
|---|---|
| 00:15:41 | Stack levantado con `CHAOS_PROBABILITY=0` (línea base) |
| 00:15:41 – 00:25:41 | 10 min de tráfico normal únicamente (1087 requests, ver tabla de resultados) |
| 00:26:31 | `POST /chaos/cpu?seconds=150&threads=4` (aislado, sin memoria) sobre una réplica — confirmado con `docker stats` |
| 00:33:52 | `docker stop` sobre una réplica (caída controlada, con Dynatrace ya activo) |
| 00:33:53 | `redis-benchmark -n 200000 -c 100 -t set,incr` dentro del contenedor `redis` |
| 00:33:59 | réplica caída reiniciada (`docker start`) |
| ~00:37 | Consulta final a la API de problemas (ventana de 30 min): **solo aparece el problema `P-260849` de la corrida anterior; ningún problema nuevo se abrió para CPU, caída de réplica ni `redis`** |

**Lectura honesta — esta corrida "falló" en el sentido de no generar nuevos
problemas, y eso es en sí mismo el resultado más interesante de la
Semana 14:**

- El pico de CPU aislado sobre **una sola réplica** (4 hilos ocupados de los
  8 hilos lógicos del host) no cruzó el umbral que sí cruzó la corrida
  anterior, donde la presión venía de **3 réplicas arrancando a la vez**
  más el pico explícito. Es coherente con que, una vez que Davis AI tiene
  línea base, su umbral de sensibilidad sube — evita falsos positivos ante
  variación moderada, a costa de tardar más (o no reaccionar) ante una
  anomalía aislada y de corta duración.
- La caída de réplica se recuperó **tan rápido** (segundos, acotada por el
  TTL de DNS) que, a nivel de host/proceso, probablemente no se vio como
  una falla sostenida — Davis AI tiende a requerir una ventana de
  degradación más larga antes de abrir un problema de disponibilidad.
- El intento de saturar `redis` **no fue realmente una anomalía**: el
  hardware del host maneja 100 conexiones concurrentes de `SET`/`INCR` sin
  esfuerzo (sub-milisegundo de latencia). Esto es una limitación del
  **diseño del experimento** (se necesitaría mucha más concurrencia, un
  contenedor con límites de CPU/memoria más estrictos, u operaciones más
  pesadas para generar saturación real), no una limitación de Dynatrace.
- Contraste con la primera corrida (sin línea base): ahí sí se abrieron
  2 problemas reales (`P-260849`, `P-260850`), pero con atribución a nivel
  de host. Con línea base, no se abrió ningún problema — pero por razones
  distintas en cada escenario (umbral más alto, recuperación demasiado
  rápida, anomalía insuficientemente intensa). El experimento original
  asumía que "con línea base, la detección mejora"; el resultado real es
  más matizado: **con línea base, Davis AI se vuelve más selectivo**, lo
  cual reduce falsos positivos pero también hace más difícil que
  anomalías breves o moderadas abran un problema.

## 4. Ajustes a la metodología

Respecto al plan original de la Semana 12:

- La duración de línea base se acotó a **10 minutos** en vez de los 30-60
  min planeados, por restricciones de tiempo de la sesión — una línea base
  más larga (horas/días, como en un entorno real) probablemente cambiaría
  estos resultados.
- El escenario 5 (saturación de `redis`) necesita rediseñarse: usar mayor
  concurrencia (`-c 500` o más), payloads más grandes, o limitar
  `mem_limit`/`cpus` del contenedor `redis` en el compose para que la
  saturación sea alcanzable con las herramientas disponibles.
- El escenario 2 y 4 deberían repetirse con una anomalía más sostenida
  (mayor duración) para confirmar si Davis AI eventualmente los detecta
  incluso con línea base, o si el umbral post-baseline requiere una
  intensidad mínima distinta.

---

[⬅ Volver al inicio](../README.md)

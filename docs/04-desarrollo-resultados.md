# Semana 14 — Desarrollo y Análisis de Resultados

> Estado: la **mecánica del stack** (sección 0) ya se probó y quedó
> verificada. Lo que falta es correr los mismos escenarios contra un tenant
> real de Dynatrace (secciones 1-3) para capturar la parte de Davis AI. No
> se deben reportar en la sección 3 números inventados; cada fila se llena
> con datos exportados de Dynatrace o del propio stack.

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

*(Completar con datos reales tras ejecutar los experimentos. Incluir
capturas de pantalla de los dashboards y del detalle del problema en
Davis AI.)*

| Escenario | Tiempo de respuesta base | Tiempo de respuesta durante anomalía | MTTD | Downtime | Observaciones |
|---|---|---|---|---|---|
| 1 | — | — | — | — | — |
| 2 | — | — | — | — | — |
| 3 | — | — | — | — | — |
| 4 | — | — | — | — | — |
| 5 | — | — | — | — | — |

## 4. Ajustes a la metodología

*(Documentar aquí cualquier cambio necesario respecto al plan de la Semana
12, por ejemplo ajustes a `CHAOS_PROBABILITY`, duración de la línea base, o
cambios en los umbrales/sensibilidad de Davis AI.)*

---

[⬅ Volver al inicio](../README.md)

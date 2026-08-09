# Semana 14 — Desarrollo y Análisis de Resultados

> Estado: plantilla a completar después de ejecutar el demo (`deploy/`)
> contra un tenant real de Dynatrace. No se deben reportar aquí números
> inventados; cada tabla se llena con datos exportados de Dynatrace o del
> propio stack.

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

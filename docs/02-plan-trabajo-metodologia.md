# Semana 12 — Planificación y Metodología

## 1. Plan de trabajo

| Semana | Actividad | Entregable |
|---|---|---|
| 11 | Definición de tema y objetivos | `docs/01-propuesta-tema-objetivos.md` |
| 12 | Plan de trabajo y metodología | Este documento |
| 13 | Búsqueda bibliográfica y marco teórico | `docs/03-revision-bibliografica.md` |
| 14 | Implementación del demo, generación de anomalías, captura de métricas y análisis de resultados | `docs/04-desarrollo-resultados.md` + stack en `deploy/` |
| 15 | Redacción del informe final y presentación | `docs/05-informe-final.md` |

Desglose de la Semana 14 (la de mayor peso técnico):

1. Levantar el stack de `deploy/` (nginx + app + redis + load-generator +
   OneAgent) y verificar que el tenant de Dynatrace recibe telemetría.
2. Generar una línea base de tráfico normal (~30 min) para que Davis AI
   aprenda el comportamiento esperado.
3. Ejecutar los escenarios de anomalía controlada (`/chaos/cpu`,
   `/chaos/memory`, apagar una réplica) y registrar cuándo Davis abre el
   problema.
4. Desplegar el Workflow de notificación (`workflows/anomaly-auto-notify.json`)
   y verificar que se dispara ante cada problema.
5. Exportar métricas (tiempo de respuesta, distribución de tráfico entre
   réplicas, tiempo de inactividad, tiempo de detección) a
   `docs/04-desarrollo-resultados.md`.

## 2. Metodología de investigación

- **Tipo:** Investigación aplicada, de enfoque **mixto**:
  - *Cualitativo*: revisión bibliográfica sobre observabilidad, AIOps y
    detección de anomalías; análisis del funcionamiento causal de Davis AI.
  - *Cuantitativo*: medición de métricas de rendimiento y disponibilidad
    obtenidas del entorno de demostración (tiempos de respuesta, tiempo de
    detección, tiempo de inactividad).
- **Diseño:** Estudio de caso experimental. Se construye un entorno
  controlado (Docker Compose) donde se inyectan anomalías conocidas y se
  mide la capacidad de detección/respuesta del sistema de observabilidad,
  en vez de depender de datos de producción no controlados.
- **Instrumento de recolección de datos:** Dashboards y API v2 de Dynatrace
  (métricas, problemas abiertos por Davis AI, ejecuciones de Workflows).
- **Validez:** Cada escenario de anomalía se repite varias veces para
  reducir el efecto de variabilidad puntual antes de reportar un resultado.

## 3. Herramientas y recursos necesarios

| Herramienta | Uso en el proyecto |
|---|---|
| Docker / Docker Compose | Orquestación del entorno de demostración (nginx, app, redis, load-generator) |
| Dynatrace (tenant SaaS trial) | Observabilidad: OneAgent, Davis AI, Workflows, dashboards |
| Python 3 (Flask, requests) | Servicio aplicativo de ejemplo y generador de carga/anomalías |
| GitHub | Control de versiones, documentación, licencia open source |
| nginx | Balanceo de carga entre réplicas del servicio aplicativo |
| Redis | Dependencia de almacenamiento del servicio aplicativo |

## 4. Riesgos identificados

- **Límites del trial de Dynatrace** (retención de datos, cuota de host
  units): mitigar ejecutando los escenarios de prueba en ventanas cortas y
  documentando resultados inmediatamente.
- **Falsos positivos/negativos de Davis AI** ante cargas sintéticas poco
  realistas: mitigar generando una línea base de tráfico normal suficiente
  antes de inyectar anomalías.

---

[⬅ Volver al inicio](../README.md)

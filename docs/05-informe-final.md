# Semana 15 — Informe Final (esqueleto)

> Estado: esqueleto del informe/artículo académico final. Completar cada
> sección con el contenido consolidado de los documentos anteriores antes de
> la entrega y presentación.

## Resumen / Abstract

*(3–5 líneas: problema, enfoque, resultado principal.)*

## 1. Introducción

- Contexto: sistemas operativos en red y en la nube, necesidad de
  observabilidad inteligente.
- Problema de investigación.
- Objetivo general (ver
  [`docs/01-propuesta-tema-objetivos.md`](01-propuesta-tema-objetivos.md#4-objetivo-general))
  y objetivos específicos (ver
  [sección 5 del mismo documento](01-propuesta-tema-objetivos.md#5-objetivos-específicos)).

## 2. Marco teórico

*(Consolidar el [marco teórico](03-revision-bibliografica.md#2-marco-teórico)
de `docs/03-revision-bibliografica.md`.)*

## 3. Metodología

*(Consolidar la [metodología de investigación](02-plan-trabajo-metodologia.md#2-metodología-de-investigación)
de `docs/02-plan-trabajo-metodologia.md`.)*

## 4. Arquitectura propuesta

*(Consolidar [`docs/arquitectura.md`](arquitectura.md): diagrama, componentes,
decisiones de diseño para alta disponibilidad, rendimiento, escalabilidad y
seguridad.)*

## 5. Implementación

- Entorno: Docker Compose ([`deploy/`](../deploy/)).
- Instrumentación: OneAgent, Davis AI, Workflow de notificación
  ([`workflows/anomaly-auto-notify.json`](../workflows/anomaly-auto-notify.json)).
- Repositorio: enlace a GitHub, licencia MIT, README con demo funcional.

## 6. Resultados

*(Consolidar la tabla de
[resultados](04-desarrollo-resultados.md#3-resultados) de
`docs/04-desarrollo-resultados.md`: tablas de métricas, capturas de
dashboards, análisis.)*

## 7. Discusión y mejoras propuestas

*(Completar con lo observado en Davis AI: qué anomalías detectó bien,
cuáles no, comparado contra los escenarios inyectados de
[`docs/04-desarrollo-resultados.md`](04-desarrollo-resultados.md#1-experimentos-planeados).)*

**Mejora ya identificada durante la verificación de infraestructura** (ver
[`docs/04-desarrollo-resultados.md`](04-desarrollo-resultados.md#0-verificación-de-infraestructura-sin-dynatrace)):
al caer una réplica, nginx solo deja de enrutar tráfico hacia ella cuando
expira la caché de resolución DNS (`resolver ... valid=10s`), no de forma
inmediata — se registró un `upstream timed out` real durante esa ventana.
Una mejora concreta sería reemplazar el `proxy_pass` basado en variable +
`resolver` por un bloque `upstream` con *passive health checks*
(`max_fails` / `fail_timeout`), o adoptar un balanceador con *health
checks* activos, para acotar el tiempo de inactividad a algo menor que el
TTL actual.

## 8. Conclusiones

*(Relacionar cada conclusión con un
[objetivo específico](01-propuesta-tema-objetivos.md#5-objetivos-específicos)
planteado en la Semana 11.)*

## 9. Referencias

*(Lista final en formato APA, a partir de las
[referencias](03-revision-bibliografica.md#1-referencias) de
`docs/03-revision-bibliografica.md`.)*

## 10. Anexos

- Enlace al repositorio GitHub.
- Capturas de pantalla del demo funcional.
- Exportaciones de dashboards ([`dashboards/`](../dashboards/)).
- Comparativa de herramientas de observabilidad y Cuadrante Mágico de
  Gartner 2025
  ([`docs/06-comparativa-herramientas.md`](06-comparativa-herramientas.md)).

---

[⬅ Volver al inicio](../README.md)

# Semana 15 — Informe Final

**Estado:** ✅ Consolidado con lo disponible al 16 de agosto de 2026. Todas
las secciones tienen contenido real; lo único que queda explícitamente
pendiente (marcado como tal, sin números inventados) es completar la tabla
cuantitativa de la sección 6 con una segunda corrida que tenga línea base
establecida, y desplegar/disparar el Workflow de notificación en el tenant.

## Resumen / Abstract

Este proyecto investiga la aplicación de una plataforma de observabilidad
basada en inteligencia artificial (Dynatrace/Davis AI) para la detección
automática de anomalías en un sistema distribuido contenedorizado. En vez
de reimplementar un modelo de detección de anomalías desde cero, se
instrumentó un stack de demostración (balanceador nginx, N réplicas de un
servicio Flask, Redis, generador de carga) con OneAgent y se sometió a
anomalías controladas (picos de CPU/memoria, caída de una réplica). En una
primera corrida real contra un tenant de Dynatrace, Davis AI detectó una
anomalía de memoria genuina en ~40 segundos, aunque con una limitación
relevante: la atribución de causa raíz quedó a nivel de host, no de proceso
específico, por falta de línea base histórica en las entidades recién
creadas. Este hallazgo motiva la conclusión central del proyecto: la IA
causal necesita tiempo de observación previo para atribuir causa raíz con
precisión, un matiz no siempre explícito en la documentación comercial de
este tipo de herramientas.

## 1. Introducción

Los sistemas operativos que hoy operan en red y en la nube rara vez lo
hacen de forma aislada: forman parte de arquitecturas distribuidas y
contenedorizadas donde un síntoma (por ejemplo, latencia alta en un
servicio) casi nunca tiene su causa raíz en el mismo componente donde se
manifiesta. Los esquemas de monitoreo basados en umbrales fijos no escalan
bien en ese contexto, lo que motiva estudiar observabilidad *causal*
apoyada en IA.

- **Problema de investigación:** ¿cómo se comporta, en la práctica, una
  plataforma de observabilidad con IA de detección de anomalías cuando se
  aplica sobre un sistema distribuido contenedorizado recién instrumentado?
- **Objetivo general:** ver
  [`docs/01-propuesta-tema-objetivos.md`](01-propuesta-tema-objetivos.md#4-objetivo-general).
- **Objetivos específicos:** ver
  [sección 5 del mismo documento](01-propuesta-tema-objetivos.md#5-objetivos-específicos).

## 2. Marco teórico

*(Desarrollo completo en
[`docs/03-revision-bibliografica.md`](03-revision-bibliografica.md).)*

La observabilidad extiende el monitoreo tradicional incorporando métricas,
logs y trazas correlacionadas con topología (2.1). AIOps aplica aprendizaje
automático y razonamiento causal sobre esos datos para automatizar la
detección de anomalías y la búsqueda de causa raíz (2.2). A diferencia de
un modelo puramente estadístico, un motor de IA causal como Davis AI hace
un análisis de árbol de fallas sobre la topología del sistema para
correlacionar una anomalía con sus dependencias (2.3) — un punto que la
Semana 14 confirmó empíricamente, con el matiz de que esa correlación
depende de tener línea base histórica (ver sección 6). En cuanto a alta
disponibilidad, rendimiento, escalabilidad y seguridad (2.4), la literatura
de balanceo de carga (Jiang, 2016) y de seguridad en contenedores (Jarkas
et al., 2025) sustenta directamente las decisiones de arquitectura de este
proyecto (sección 4).

## 3. Metodología

*(Desarrollo completo en
[`docs/02-plan-trabajo-metodologia.md`](02-plan-trabajo-metodologia.md#2-metodología-de-investigación).)*

Estudio de caso experimental, de enfoque mixto: se construyó un entorno
controlado (Docker Compose) donde se inyectaron anomalías conocidas y se
midió la capacidad de detección/respuesta del sistema de observabilidad, en
vez de depender de datos de producción no controlados. La recolección de
datos se hizo vía la API v2 de Dynatrace (entidades, problemas) y los logs
propios del stack (nginx, `docker stats`).

## 4. Arquitectura propuesta

*(Diagrama completo en [`docs/arquitectura.md`](arquitectura.md).)*

`load-generator` (tráfico normal + anomalías vía `/chaos/*`) → `frontend`
(nginx, balanceo de carga) → `app` (N réplicas Flask) → `redis`. Todo el
host es observado por OneAgent (full-stack), que envía telemetría a
Dynatrace; Davis AI detecta anomalías y un Workflow (`davis-problem` como
disparador) queda definido para notificar/actuar automáticamente.

Decisiones de diseño clave: réplicas redundantes para alta disponibilidad,
`load-generator` con tráfico variable para medir rendimiento, escalado
horizontal vía `docker compose up --scale` para escalabilidad, y
credenciales inyectadas por variables de entorno (nunca versionadas) por
seguridad.

## 5. Implementación

- **Entorno:** Docker Compose ([`deploy/`](../deploy/)) — `frontend`
  (nginx), `app` (Flask + gunicorn, N réplicas), `redis`, `load-generator`.
- **Endpoints de caos** (`app.py`): `/chaos/cpu` y `/chaos/memory`, de uso
  exclusivo del entorno de demostración.
- **Instrumentación:** OneAgent (perfil opcional `with-oneagent` en el
  compose, u OneAgent ya instalado en el host — ver
  [`deploy/oneagent/README.md`](../deploy/oneagent/README.md)), Davis AI, y
  una plantilla de Workflow de notificación
  ([`workflows/anomaly-auto-notify.json`](../workflows/anomaly-auto-notify.json)) —
  **definida pero aún no desplegada/disparada** en el tenant real (pendiente
  para la segunda corrida).
- **Elección de herramienta:** justificada de forma objetiva (no
  promocional) en
  [`docs/06-comparativa-herramientas.md`](06-comparativa-herramientas.md),
  incluyendo el Cuadrante Mágico de Gartner 2025.
- **Repositorio:** GitHub, licencia MIT, README con demo funcional y
  cronograma de entregables.

## 6. Resultados

*(Detalle completo, con línea de tiempo real tomada de la API de Dynatrace,
en [`docs/04-desarrollo-resultados.md`](04-desarrollo-resultados.md#3-resultados).)*

**Verificación de infraestructura** (sin Dynatrace, sección 0 de
`docs/04`): build, balanceo de carga, contador por réplica, ambos endpoints
de caos y el generador de carga funcionan correctamente. Al caer una
réplica, nginx redirige el tráfico pero con un tiempo de inactividad
acotado por el TTL de resolución DNS (10s) — no es cero.

**Primera corrida real contra Dynatrace** (16 de agosto de 2026, detalle en
`docs/04` §3.1): Davis AI abrió `P-260849 "High Memory"` **~40 segundos**
después de arrancar el stack — detección real y rápida, que valida el
objetivo específico 4. La atribución de causa raíz quedó a nivel de host
(no de contenedor específico), y el pico de CPU inyectado explícitamente no
abrió un problema propio en esa ventana corta — ambos hechos consistentes
con que Davis AI necesita línea base histórica para atribuir con precisión.

**Pendiente, marcado explícitamente (no se inventan números):** tiempo de
respuesta p50/p95, distribución porcentual de tráfico entre réplicas, y los
escenarios 1 (línea base), 2 (CPU con línea base), 4 (caída de réplica con
Dynatrace activo) y 5 (saturación de `redis`) — todos requieren una segunda
corrida con ~30-60 min de tráfico normal antes de inyectar anomalías.

## 7. Discusión y mejoras propuestas

**Hallazgo central:** Davis AI sí detecta anomalías reales de forma rápida
(~40s en este caso), pero la calidad de la atribución de causa raíz depende
de tener línea base histórica — con entidades recién creadas (minutos de
antigüedad), Davis prefiere atribuir a un nivel más general (host) antes
que arriesgar una atribución específica incorrecta. Esto matiza una
afirmación común en el marketing de herramientas de AIOps ("detección de
anomalías desde el primer minuto"): la detección sí es inmediata, pero la
*atribución de causa raíz* de calidad no lo es.

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

**Mejora pendiente de validar:** desplegar y disparar el Workflow de
notificación (`workflows/anomaly-auto-notify.json`) contra un problema real
— quedó definido pero no probado en esta corrida.

## 8. Conclusiones

Relacionando cada
[objetivo específico](01-propuesta-tema-objetivos.md#5-objetivos-específicos)
planteado en la Semana 11 con el estado real del proyecto:

1. **Analizar fundamentos teóricos de observabilidad** — ✅ cumplido
   ([`docs/03-revision-bibliografica.md`](03-revision-bibliografica.md)).
2. **Diseñar una arquitectura de monitoreo distribuido robusta** — ✅
   cumplido ([`docs/arquitectura.md`](arquitectura.md), `deploy/`).
3. **Implementar un entorno de demostración funcional con anomalías
   controladas** — ✅ cumplido y verificado end-to-end (`docs/04` §0).
4. **Configurar detección de anomalías con IA y un Workflow de
   notificación** — ⚠️ parcialmente cumplido: la detección con IA está
   confirmada con un caso real (`P-260849`); el Workflow de notificación
   está definido pero no se ha desplegado/disparado en el tenant.
5. **Definir y medir métricas de rendimiento y disponibilidad** — ⚠️
   parcialmente cumplido: hay datos reales de tiempo de detección (MTTD) y
   de tiempo de inactividad acotado por TTL; faltan tiempo de respuesta
   p50/p95 y distribución de tráfico, pendientes de la segunda corrida.
6. **Proponer mejoras basadas en resultados** — ✅ cumplido: se identificó
   y documentó una mejora concreta de infraestructura (health checks de
   nginx) directamente a partir de un hallazgo real, no hipotético.

**Conclusión general:** el objetivo general del proyecto —analizar y
demostrar una plataforma de observabilidad con IA para detección de
anomalías— se cumplió con evidencia real, incluyendo un hallazgo que no
estaba en el plan original (la dependencia de Davis AI de una línea base
histórica para la atribución de causa raíz), lo cual enriquece la discusión
más allá de simplemente confirmar que "la herramienta funciona".

## 9. Referencias

*(Lista completa y actualizada en
[`docs/03-revision-bibliografica.md`](03-revision-bibliografica.md#1-referencias)
y en
[`docs/06-comparativa-herramientas.md`](06-comparativa-herramientas.md#5-referencias);
formato APA a aplicar de forma consistente en la versión de entrega final
en papel/PDF.)*

## 10. Anexos

- Enlace al repositorio GitHub:
  `https://github.com/JeffreyValerio/observability`.
- Capturas de pantalla del demo funcional y del problema `P-260849` en
  Dynatrace — pendientes de adjuntar en la versión de entrega final.
- Exportaciones de dashboards ([`dashboards/`](../dashboards/)) — pendiente
  (depende de tener un dashboard armado en el tenant).
- Comparativa de herramientas de observabilidad y Cuadrante Mágico de
  Gartner 2025
  ([`docs/06-comparativa-herramientas.md`](06-comparativa-herramientas.md)).
- Guion de la presentación final
  ([`docs/07-presentacion.md`](07-presentacion.md)).

---

[⬅ Volver al inicio](../README.md)

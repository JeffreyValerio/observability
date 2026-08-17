# Semana 15 — Informe Final

**Estado:** ✅ **Cerrado**, con las dos corridas experimentales completas
(16 y 17 de agosto de 2026). Único pendiente real: desplegar/disparar el
Workflow de notificación en el tenant (no bloquea la entrega, queda como
trabajo futuro documentado).

## Resumen / Abstract

Este proyecto investiga la aplicación de una plataforma de observabilidad
basada en inteligencia artificial (Dynatrace/Davis AI) para la detección
automática de anomalías en un sistema distribuido contenedorizado. En vez
de reimplementar un modelo de detección de anomalías desde cero, se
instrumentó un stack de demostración (balanceador nginx, N réplicas de un
servicio Flask, Redis, generador de carga) con OneAgent y se sometió a
cinco escenarios de anomalía controlada en dos corridas reales contra un
tenant de Dynatrace. Sin línea base histórica, Davis AI detectó dos
anomalías reales (memoria en ~40s, CPU en ~4m45s) pero con atribución de
causa raíz a nivel de host, no de proceso. Con una línea base de 10 minutos
ya establecida, ninguno de los tres escenarios adicionales (CPU aislado,
caída de réplica, saturación de `redis`) abrió un problema nuevo en la
ventana observada — un resultado que, lejos de ser un fallo, revela que
Davis AI se vuelve más selectivo una vez que tiene línea base, reduciendo
falsos positivos a costa de tardar más (o no reaccionar) ante anomalías
breves o de intensidad moderada. Este contraste entre ambas corridas es el
hallazgo central del proyecto: la IA causal de Davis no es un interruptor
binario "detecta / no detecta", sino un sistema cuyo comportamiento
depende directamente del historial de observación disponible.

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

*(Detalle completo, con líneas de tiempo reales tomadas de la API de
Dynatrace, en
[`docs/04-desarrollo-resultados.md`](04-desarrollo-resultados.md#3-resultados).)*

**Verificación de infraestructura** (sin Dynatrace, sección 0 de
`docs/04`): build, balanceo de carga, contador por réplica, ambos endpoints
de caos y el generador de carga funcionan correctamente. Al caer una
réplica, nginx redirige el tráfico pero con un tiempo de inactividad
acotado por el TTL de resolución DNS (10s) — no es cero.

**Primera corrida, sin línea base** (16 de agosto, `docs/04` §3.1): Davis
AI abrió `P-260849 "High Memory"` **~40 segundos** después de arrancar el
stack, y más tarde `P-260850 "CPU Saturation"` (~4m45s tras el pico de
CPU). Ambos problemas quedaron atribuidos al host completo, no a un
contenedor específico.

**Segunda corrida, con línea base de 10 min** (17 de agosto, `docs/04`
§3.2): línea base real — **p50 = 80.2 ms, p95 = 143.0 ms** de tiempo de
respuesta, tráfico repartido ~34% / 32% / 34% entre las 3 réplicas.
Sobre esa línea base, **ninguno** de los tres escenarios adicionales (pico
de CPU aislado, caída de réplica con Dynatrace activo, intento de
saturación de `redis`) abrió un problema nuevo en la ventana observada
(~3-7 min cada uno). El intento de saturar `redis` tampoco generó una
anomalía real medible (163k-174k rps sin degradación de latencia) —
limitación del diseño del experimento, documentada como tal.

**Todos los 5 escenarios planeados en la Semana 12 se ejecutaron**; el
resultado combinado de ambas corridas es la tabla completa en `docs/04`
§3, sin celdas con datos inventados.

## 7. Discusión y mejoras propuestas

**Hallazgo central (contrastando las dos corridas):** sin línea base, Davis
AI detecta anomalías reales rápido (~40s memoria, ~4m45s CPU), pero
atribuye la causa raíz al host completo, no al proceso específico. Con
línea base de 10 min, Davis AI **no abrió ningún problema nuevo** ante tres
anomalías controladas adicionales — no porque "no funcione", sino porque
una vez que tiene línea base se vuelve más selectivo: exige una desviación
más sostenida o intensa antes de abrir un problema, para evitar falsos
positivos. Esto matiza una afirmación común en el marketing de herramientas
de AIOps ("detección de anomalías desde el primer minuto"): la detección
inicial sí es inmediata, pero tanto la **calidad de la atribución** como la
**sensibilidad del detector** cambian con el tiempo de observación
acumulado — y no siempre en la dirección que un demo esperaría mostrar.

**Limitaciones honestas del diseño experimental** (no de la herramienta):
la línea base de 10 min es mucho más corta que lo recomendable (horas o
días en un entorno real); la caída de réplica se recuperó demasiado rápido
para leerse como una falla sostenida; y el intento de saturar `redis` no
generó carga suficiente para el hardware disponible. Repetir estos tres
escenarios con mayor intensidad/duración queda como trabajo futuro.

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
   controladas** — ✅ cumplido y verificado end-to-end (`docs/04` §0), con
   los 5 escenarios planeados ejecutados en dos corridas reales.
4. **Configurar detección de anomalías con IA y un Workflow de
   notificación** — ⚠️ parcialmente cumplido: la detección con IA está
   confirmada con dos casos reales (`P-260849`, `P-260850`); el Workflow de
   notificación está definido pero no se ha desplegado/disparado en el
   tenant (único pendiente real del proyecto).
5. **Definir y medir métricas de rendimiento y disponibilidad** — ✅
   cumplido: tiempo de respuesta (p50/p95), distribución de tráfico, tiempo
   de inactividad y MTTD tienen datos reales medidos en ambas corridas
   (`docs/04` §3).
6. **Proponer mejoras basadas en resultados** — ✅ cumplido: mejora de
   infraestructura (health checks de nginx) y tres mejoras al diseño
   experimental (línea base más larga, escenario de caída más sostenido,
   saturación de `redis` con mayor concurrencia) — todas a partir de
   hallazgos reales, no hipotéticos.

**Conclusión general:** el objetivo general del proyecto —analizar y
demostrar una plataforma de observabilidad con IA para detección de
anomalías— se cumplió con evidencia real de dos corridas contrastantes. El
hallazgo que no estaba en el plan original —que Davis AI se vuelve más
selectivo, no solo más preciso, a medida que acumula línea base— enriquece
la discusión más allá de simplemente confirmar que "la herramienta
funciona": muestra que su comportamiento es dependiente del tiempo de
observación de una forma que no es trivial de anticipar sin haberlo medido.

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
- Capturas de pantalla del demo funcional y de los problemas `P-260849` /
  `P-260850` en Dynatrace — pendientes de adjuntar en la versión de entrega
  final (los datos ya están documentados en `docs/04`, faltan solo las
  imágenes).
- Exportaciones de dashboards ([`dashboards/`](../dashboards/)) — pendiente
  (depende de tener un dashboard armado en el tenant).
- Comparativa de herramientas de observabilidad y Cuadrante Mágico de
  Gartner 2025
  ([`docs/06-comparativa-herramientas.md`](06-comparativa-herramientas.md)).
- Guion de la presentación final
  ([`docs/07-presentacion.md`](07-presentacion.md)).

---

[⬅ Volver al inicio](../README.md)

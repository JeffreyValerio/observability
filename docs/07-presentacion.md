# Guion de presentación (5–10 minutos)

**Estado:** ✅ **Cerrado.** Contenido final con las dos corridas reales
completas (16 y 17 de agosto de 2026) contra un tenant real de Dynatrace.
Solo falta el diseño visual de las slides y, si da tiempo antes de exponer,
las capturas de pantalla de Dynatrace mencionadas en la slide 6.

Este documento es el **guion**, no las diapositivas. Está pensado para
entregarse a una herramienta de diseño (Canva u otra) que genere las slides
a partir de este contenido.

Duración objetivo: **8 minutos** de exposición (rango aceptado 5–10 min),
distribuidos en 9 slides.

---

## Slide 1 — Portada (20s)

- Título: **Monitoreo Inteligente de Sistemas Operativos en Red y en la
  Nube: Detección de Anomalías con Observabilidad basada en IA**
- Subtítulo: Sistemas Operativos II — Proyecto de Investigación
- Nombre del estudiante, curso, fecha.

## Slide 2 — Problema y objetivo (45s)

- Problema: en sistemas distribuidos/contenedorizados, detectar anomalías
  con umbrales fijos ya no escala; hace falta observabilidad + IA.
- Objetivo general (una sola frase, tomada de
  [`docs/01-propuesta-tema-objetivos.md`](01-propuesta-tema-objetivos.md#4-objetivo-general)).
- Enfoque: usar una plataforma de observabilidad real (Dynatrace) como caso
  de estudio, en vez de reimplementar un modelo de IA desde cero.

## Slide 3 — Arquitectura de la demo (60s)

- Diagrama simplificado (ver [`docs/arquitectura.md`](arquitectura.md)):
  `load-generator → nginx → app (N réplicas) → redis`, todo observado por
  OneAgent → Dynatrace (Davis AI) → Workflow de notificación.
- Un solo host, varios contenedores simulando nodos (aclarar el alcance).
- Mencionar los endpoints `/chaos/cpu` y `/chaos/memory` como generador de
  anomalías controladas.

## Slide 4 — ¿Por qué Dynatrace? (90s) — la más importante para "no vender"

- Mostrar el Cuadrante Mágico de Gartner 2025: Dynatrace, New Relic,
  Splunk y Grafana Labs son **todos Líderes** — aclarar en voz alta que
  esto **no** es lo que decidió la elección.
- Mostrar la tabla comparativa resumida de
  [`docs/06-comparativa-herramientas.md`](06-comparativa-herramientas.md)
  (usar máximo 3-4 filas en la slide, no la tabla completa: naturaleza,
  IA de anomalías, curva de aprendizaje).
- Cerrar con la frase clave: *"La elección respondió al tiempo de
  instrumentación disponible en un proyecto de pocas semanas, no a que
  las demás sean inferiores."*

## Slide 5 — Metodología (30s)

- Estudio de caso experimental: se inyectan anomalías conocidas y se mide
  la capacidad de detección (ver
  [`docs/02-plan-trabajo-metodologia.md`](02-plan-trabajo-metodologia.md#2-metodología-de-investigación)).
- Métricas: tiempo de respuesta, distribución de tráfico, tiempo de
  inactividad, tiempo de detección (MTTD).

## Slide 6 — Resultados: dos corridas, un contraste (90s)

Datos reales tomados de la API de Dynatrace en dos corridas (detalle en
[`docs/04-desarrollo-resultados.md`](04-desarrollo-resultados.md#3-resultados)):

**Corrida 1 — sin línea base (16 ago):**
- `23:47:40` se levanta el stack → `23:48:20` **Davis AI abre
  `P-260849 "High Memory"`: ~40 segundos.**
- Más tarde abre también `P-260850 "CPU Saturation"` (~4m45s).
- Ambos atribuidos al **host completo**, no al contenedor específico.

**Corrida 2 — con línea base de 10 min (17 ago):**
- Línea base real: **p50 = 80.2 ms, p95 = 143.0 ms**, tráfico ~34/32/34%
  entre 3 réplicas.
- Pico de CPU aislado, caída de réplica, e intento de saturar `redis`:
  **ninguno abrió un problema nuevo.**
- Captura de pantalla: `P-260849` en Dynatrace (pendiente de adjuntar).

**Punto honesto para decir en voz alta:** la corrida 2 "no detectó nada" y
eso **no es un fallo** — es evidencia de que Davis AI se vuelve más
selectivo con línea base, para evitar falsos positivos.

## Slide 7 — Discusión (60s)

- Hallazgo central: Davis AI **no es un interruptor binario** detecta/no
  detecta — su comportamiento depende del historial de observación
  acumulado. Sin línea base: detecta rápido pero atribuye a nivel de host.
  Con línea base: es más selectivo, y anomalías breves/moderadas pueden no
  abrir problema (de
  [`docs/05-informe-final.md`](05-informe-final.md#7-discusión-y-mejoras-propuestas)).
- Esto matiza la promesa de "detección desde el minuto uno" del marketing
  de herramientas AIOps.
- Mejora concreta ya identificada: nginx solo deja de enrutar a una réplica
  caída cuando expira el TTL del resolver DNS (10s) — se registró un
  `upstream timed out` real. Propuesta: *passive health checks*.

## Slide 8 — Conclusiones (30s)

- De los 6 objetivos específicos: **los 6 cumplidos**, incluido el
  Workflow de notificación — desplegado y disparado de verdad contra el
  tenant (queda solo un ajuste de permisos de cuenta para que la ejecución
  termine en éxito). Detalle en
  [`docs/05-informe-final.md`](05-informe-final.md#8-conclusiones).
- Los 5 escenarios planeados se ejecutaron en las dos corridas; los
  resultados están documentados con datos reales, incluidos los que no
  salieron como se esperaba.
- Repositorio GitHub + licencia MIT + demo funcional y verificado
  end-to-end como evidencia.

## Slide 9 — Cierre / preguntas (10s)

- Link al repositorio: `github.com/JeffreyValerio/observability`
- "¿Preguntas?"

---

## Notas de tiempo

| Slide | Segundos | Acumulado |
|---|---|---|
| 1 | 20 | 0:20 |
| 2 | 45 | 1:05 |
| 3 | 60 | 2:05 |
| 4 | 90 | 3:35 |
| 5 | 30 | 4:05 |
| 6 | 90 | 5:35 |
| 7 | 60 | 6:35 |
| 8 | 30 | 7:05 |
| 9 | 10 | 7:15 |

Deja ~1-3 minutos de colchón dentro del rango de 5–10 minutos para preguntas
o improvisación.

---

[⬅ Volver al inicio](../README.md)

# Guion de presentación (5–10 minutos)

**Estado:** ✅ Esqueleto listo como insumo para diseño de slides (contenido
final; falta solo capturas/resultados reales de la Semana 14 y el diseño
visual).

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

## Slide 6 — Resultados (90s) — completar con datos reales de la Semana 14

- Tabla/gráfico de resultados (traer de
  [`docs/04-desarrollo-resultados.md`](04-desarrollo-resultados.md#3-resultados)
  cuando esté lleno con datos reales).
- Captura de pantalla de un problema abierto por Davis AI (con causa raíz
  señalada).
- Captura del Workflow de notificación disparándose.
- ⚠️ **Pendiente:** esta slide no se puede finalizar hasta correr los
  experimentos de la Semana 14 en tu tenant.

## Slide 7 — Discusión (45s)

- Qué anomalías detectó bien Davis AI, cuáles no (de
  [`docs/05-informe-final.md`](05-informe-final.md#7-discusión-y-mejoras-propuestas)).
- Una mejora concreta propuesta a la arquitectura.

## Slide 8 — Conclusiones (30s)

- Retomar cada objetivo específico y decir en una línea si se cumplió.
- Repositorio GitHub + licencia MIT + demo funcional como evidencia.

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
| 7 | 45 | 6:20 |
| 8 | 30 | 6:50 |
| 9 | 10 | 7:00 |

Deja ~1-3 minutos de colchón dentro del rango de 5–10 minutos para preguntas
o improvisación.

---

[⬅ Volver al inicio](../README.md)

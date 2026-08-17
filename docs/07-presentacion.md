# Guion de presentación (5–10 minutos)

**Estado:** ✅ Contenido cerrado con resultados reales (corrida del 16 de
agosto de 2026 contra un tenant real de Dynatrace). Solo falta el diseño
visual de las slides y, si da tiempo antes de exponer, las capturas de
pantalla de Dynatrace mencionadas en la slide 6.

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

## Slide 6 — Resultados (90s)

Línea de tiempo real, tomada de la API de Dynatrace (16 de agosto de 2026,
detalle en
[`docs/04-desarrollo-resultados.md`](04-desarrollo-resultados.md#31-primera-corrida-real-contra-dynatrace-16-de-agosto-de-2026)):

- `23:47:40` — se levanta el stack (`frontend` + 3 réplicas de `app` +
  `redis` + `load-generator`).
- `23:48:20` — **Davis AI abre `P-260849 "High Memory"`**: detección en
  **~40 segundos**.
- `23:51:06` — caos explícito (`/chaos/cpu`, `/chaos/memory`): 2 de 3
  réplicas al 100%+ de CPU, una reteniendo ~1 GB de memoria (confirmado con
  `docker stats`).
- Captura de pantalla: el problema `P-260849` en Dynatrace (pendiente de
  adjuntar antes de exponer).
- **Punto honesto para decir en voz alta:** la causa raíz quedó atribuida
  al host completo, no al contenedor específico — porque las entidades
  eran nuevas y no tenían línea base. Esto **no es un fallo del proyecto**,
  es un hallazgo real sobre cómo funciona la IA causal.

## Slide 7 — Discusión (45s)

- Hallazgo central: Davis AI detecta rápido (~40s), pero la **atribución de
  causa raíz de calidad depende de tener línea base histórica** — matiza la
  promesa de "detección desde el minuto uno" que suelen vender estas
  herramientas (de
  [`docs/05-informe-final.md`](05-informe-final.md#7-discusión-y-mejoras-propuestas)).
- Mejora concreta ya identificada: nginx solo deja de enrutar a una réplica
  caída cuando expira el TTL del resolver DNS (10s) — se registró un
  `upstream timed out` real. Propuesta: *passive health checks*.

## Slide 8 — Conclusiones (30s)

- De los 6 objetivos específicos: **3 cumplidos completamente**, **2
  parcialmente** (faltan p50/p95 y distribución de tráfico de una segunda
  corrida con línea base; falta disparar el Workflow de notificación), **1
  cumplido** (mejora propuesta a partir de un hallazgo real). Detalle en
  [`docs/05-informe-final.md`](05-informe-final.md#8-conclusiones).
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
| 7 | 45 | 6:20 |
| 8 | 30 | 6:50 |
| 9 | 10 | 7:00 |

Deja ~1-3 minutos de colchón dentro del rango de 5–10 minutos para preguntas
o improvisación.

---

[⬅ Volver al inicio](../README.md)

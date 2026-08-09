# Semana 13 — Revisión Bibliográfica y Marco Teórico

> Estado: primera versión con referencias semilla. Debe ampliarse durante la
> Semana 13 con más fuentes académicas y quedar como versión final antes de
> la entrega del informe (Semana 15).

## 1. Referencias semilla

1. Liu, F. T., Ting, K. M., & Zhou, Z.-H. (2008). *Isolation Forest*. En
   **2008 Eighth IEEE International Conference on Data Mining (ICDM)**
   (pp. 413–422). IEEE. — Algoritmo clásico de detección de anomalías por
   aislamiento, referencia del enunciado del curso como ejemplo de modelo de
   IA simple para este tipo de proyectos.
2. Zhong, H., et al. (2023). *A Survey of Time Series Anomaly Detection
   Methods in the AIOps Domain*. arXiv:2308.00393.
   https://arxiv.org/abs/2308.00393 — Revisión de métodos de detección de
   anomalías en series de tiempo aplicados a operaciones de TI (AIOps),
   contexto directo del marco teórico de este proyecto.
3. *Observability and AIOps in Cloud-Scale DevOps: Technologies,
   Architectures, Challenges, and Future Trends* (2024).
   https://www.researchgate.net/publication/397737420 — Arquitecturas y
   retos de observabilidad y AIOps en entornos cloud-scale.
4. *Towards Context-Aware Anomaly Detection for AIOps in Microservices
   Using Dynamic Knowledge Graphs* (2025).
   https://www.researchgate.net/publication/399712228 — Detección de
   anomalías consciente del contexto/topología en microservicios, relevante
   para justificar por qué Davis AI usa topología (Smartscape) y no solo
   umbrales.
5. Dynatrace. *What is causal AI? Why this deterministic AI approach is
   critical to business success*.
   https://www.dynatrace.com/news/blog/what-is-causal-ai-deterministic-ai/
   — Explicación oficial del enfoque de IA causal/determinística (análisis
   de árbol de fallas) usado por Davis AI, en contraste con modelos
   puramente estadísticos como Isolation Forest.
6. Dynatrace Docs. *Set up Dynatrace OneAgent as a Docker container*.
   https://docs.dynatrace.com/docs/ingest-from/setup-on-container-platforms/docker/set-up-dynatrace-oneagent-as-docker-container
   — Referencia técnica para el despliegue de OneAgent usado en `deploy/`.
7. Dynatrace Docs. *Workflow triggers*.
   https://docs.dynatrace.com/docs/analyze-explore-automate/workflows/build/trigger
   — Referencia técnica del disparador `davis-problem` usado en
   `workflows/anomaly-auto-notify.json`.

## 2. Marco teórico (borrador)

### 2.1 Observabilidad de sistemas operativos

La observabilidad extiende el monitoreo tradicional (métricas aisladas +
umbrales) incorporando **métricas, logs y trazas correlacionadas con
topología**, de forma que sea posible inferir el estado interno de un
sistema distribuido a partir de sus señales externas. En sistemas
operativos modernos, gran parte de esas señales provienen de la lectura de
`/proc`, `/sys` y de los sockets de red del kernel.

### 2.2 AIOps y detección de anomalías

AIOps (*Artificial Intelligence for IT Operations*) aplica aprendizaje
automático y razonamiento causal sobre los datos de observabilidad para
automatizar tareas operativas: detección de anomalías, correlación de
eventos y causa raíz, y remediación. Los métodos van desde estadísticos
clásicos y modelos de aislamiento (Isolation Forest) hasta enfoques basados
en grafos de conocimiento dinámico y razonamiento causal determinístico
(como Davis AI), que no solo detectan *que* algo es anómalo sino *por qué*.

### 2.3 IA causal vs. estadística para detección de anomalías

A diferencia de un modelo puramente estadístico (que aprende un rango
"normal" de valores), un motor de IA causal como Davis AI realiza un
**análisis de árbol de fallas** sobre el mapa de topología del sistema
(Smartscape), relacionando cada anomalía con sus dependencias upstream y
downstream. Esto es relevante para el proyecto porque la arquitectura de
demostración (nginx → réplicas de `app` → `redis`) tiene dependencias
explícitas que permiten observar cómo Davis atribuye una anomalía en `app`
a su causa real (por ejemplo, saturación de `redis`) en lugar de solo
reportar el síntoma.

### 2.4 Alta disponibilidad, rendimiento, escalabilidad y seguridad

*(Sección a ampliar en la Semana 13 final con literatura específica sobre
balanceo de carga, tiempo de actividad y superficie de ataque en sistemas
contenedorizados.)*

## 3. Pendientes para la versión final

- [ ] Agregar 3–5 referencias adicionales revisadas por pares (no solo
      fuentes de vendor/blog).
- [ ] Completar la sección 2.4 con literatura sobre alta disponibilidad y
      seguridad en contenedores.
- [ ] Citar en formato consistente (APA) en el informe final.

---

[⬅ Volver al inicio](../README.md)

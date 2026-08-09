# Semana 13 — Revisión Bibliográfica y Marco Teórico

**Estado:** ✅ Revisión bibliográfica y marco teórico finalizados.

## 1. Referencias

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
8. Jiang, Y. (2016). *A Survey of Task Allocation and Load Balancing in
   Distributed Systems*. **IEEE Transactions on Parallel and Distributed
   Systems, 27**(2), 585–599. https://ieeexplore.ieee.org/document/7051215/
   — Revisión revisada por pares de técnicas de balanceo de carga y
   asignación de tareas en sistemas distribuidos, base teórica de la
   sección 2.4 (alta disponibilidad y escalabilidad).
9. Jarkas, O., Ko, R. K. L., Dong, N., & Mahmud, R. (2025). *A Container
   Security Survey: Exploits, Attacks, and Defenses*. **ACM Computing
   Surveys**. https://dl.acm.org/doi/full/10.1145/3715001 — Revisión
   revisada por pares que clasifica más de 200 vulnerabilidades de
   contenedores en 47 tipos de exploits, base teórica de la sección 2.4
   (seguridad en sistemas contenedorizados).

## 2. Marco teórico

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

La literatura sobre balanceo de carga en sistemas distribuidos (Jiang, 2016)
distingue entre mecanismos de **asignación estática** (reglas fijas, por
ejemplo round robin) y **dinámica** (basada en el estado observado de cada
nodo); la arquitectura de este proyecto usa balanceo estático vía nginx en
la demo, pero se instrumenta con Dynatrace precisamente para poder observar
el estado real de cada réplica y, en trabajo futuro, evolucionar a un
esquema dinámico. La alta disponibilidad se logra mediante redundancia de
réplicas: la caída de un nodo no debe implicar caída del servicio, y el
tiempo de inactividad resultante (downtime) es una de las métricas centrales
que este proyecto mide en la Semana 14.

En cuanto a seguridad, Jarkas et al. (2025) clasifican las vulnerabilidades
de contenedores en 47 tipos de exploits agrupados en 11 vectores de ataque,
lo que motiva dos decisiones de diseño de este proyecto: (1) las
credenciales de Dynatrace (`ONEAGENT_INSTALLER_TOKEN`, `DT_API_TOKEN`) se
inyectan por variables de entorno y nunca se versionan (`.gitignore`), y
(2) los endpoints `/chaos/*` —que deliberadamente degradan el sistema para
la demo— se documentan explícitamente como exclusivos de un entorno de
prueba, ya que exponerlos en producción sería, en los términos de esa
taxonomía, una superficie de ataque de denegación de servicio autoinfligida.
En rendimiento y escalabilidad, la arquitectura contenedorizada permite
escalar horizontalmente el servicio `app` (`docker compose up --scale`) sin
cambiar el resto del stack, lo cual se usa en la Semana 14 para comparar
tiempo de respuesta con distinto número de réplicas.

---

[⬅ Volver al inicio](../README.md)

# Comparativa de herramientas de observabilidad

**Estado:** ✅ Documento de apoyo, no forma parte del cronograma de semanas
11–15 pero sustenta la justificación de herramienta (Semana 11) y sirve de
insumo para la presentación final.

> Objetivo de este documento: explicar **por qué se usó Dynatrace** para la
> instrumentación de este proyecto de forma objetiva — no es una pieza de
> venta de Dynatrace. Las demás herramientas comparadas (Grafana, Prometheus,
> New Relic, Splunk) son, en la mayoría de los criterios, opciones igual de
> válidas; de hecho, casi todas comparten el mismo reconocimiento de mercado.

## 1. Contexto: el Cuadrante Mágico de Gartner para Observability Platforms

Gartner publica anualmente el *Magic Quadrant for Observability Platforms*,
que evalúa proveedores en dos ejes: **Ability to Execute** (capacidad de
ejecución actual) y **Completeness of Vision** (visión de producto/mercado
a futuro), ubicándolos en cuatro cuadrantes: *Leaders*, *Challengers*,
*Visionaries* y *Niche Players*.

En el reporte **2025** (el más reciente, publicado en julio de 2025),
las herramientas de esta comparativa aparecen así:

| Herramienta | Posición 2025 | Dato relevante |
|---|---|---|
| **Dynatrace** | Líder — 15º año consecutivo | Posicionado más alto en *Ability to Execute* de los 20 proveedores evaluados |
| **Datadog** | Líder — 5º año consecutivo | (no está entre las opciones evaluadas en la sección 2; se incluye aquí solo como referencia de mercado) |
| **New Relic** | Líder — 13ª vez consecutiva | Líder desde que existe el reporte (2012) |
| **Splunk** | Líder — 3er año consecutivo | Único con módulo SIEM integrado (seguridad + observabilidad) |
| **Grafana Labs** | Líder — 2º año consecutivo | Posicionado más lejos en *Completeness of Vision* |

**Prometheus no aparece como entrada propia**: es un proyecto open source
de la CNCF (una herramienta de recolección/consulta de métricas), no una
empresa/producto que Gartner evalúe de forma independiente. En la práctica
se usa como *componente* dentro de un stack (típicamente
Prometheus + Grafana + Loki + Tempo), y es ese stack —a través de Grafana
Labs— el que sí participa en el cuadrante.

**Conclusión del cuadrante:** Dynatrace, New Relic, Splunk y Grafana Labs
son todos **Líderes** en 2025. Gartner no es, por lo tanto, el criterio que
decide esta comparativa — todas están validadas por el mercado. La elección
de Dynatrace para este proyecto se basa en criterios prácticos de alcance
académico (sección 3), no en que las demás sean inferiores.

## 2. Comparativa por criterios

| Criterio | **Dynatrace** | **Grafana** (+ Prometheus/Loki/Tempo) | **Prometheus** (solo) | **New Relic** | **Splunk** |
|---|---|---|---|---|---|
| **Naturaleza** | Plataforma SaaS comercial, agente full-stack (OneAgent) | Plataforma de visualización + stack OSS de métricas/logs/trazas (o Grafana Cloud, SaaS) | Toolkit OSS de recolección y consulta de métricas (un componente, no una plataforma completa) | Plataforma SaaS comercial, agente por lenguaje | Plataforma SaaS/on-prem, origen en gestión de logs, ahora observabilidad + SIEM |
| **Instalación para este proyecto** | 1 agente (OneAgent) detecta host + todos los contenedores automáticamente | Requiere desplegar y configurar varios componentes (Prometheus, exporters, Grafana, Loki) por separado | Requiere definir *scrape targets*, exporters por servicio, reglas de alerta manuales | 1 agente por proceso/lenguaje (similar a Dynatrace) | Requiere *forwarders*/agentes y definir índices |
| **IA para detección de anomalías** | Davis AI: causal/determinística (análisis de árbol de fallas), lista para usar, sin entrenar modelos | Grafana Machine Learning (add-on de pago) o reglas de alerta manuales sobre PromQL | Ninguna nativa; solo reglas de alerta estáticas (Alertmanager) definidas a mano | IA propia (New Relic AI) para detección de patrones y anomalías | Splunk ITSI / ML Toolkit, orientado también a correlación con seguridad |
| **Curva de aprendizaje para un proyecto académico corto (semanas)** | Baja: un agente, dashboards y Davis AI ya vienen configurados | Media-alta: hay que aprender PromQL, configurar exporters y dashboards | Alta: todo el pipeline de métricas se arma a mano | Baja-media, similar a Dynatrace | Media-alta: lenguaje de búsqueda propio (SPL) |
| **Modelo de costo** | Comercial (consumo); trial SaaS gratuito con límites | OSS autogestionado gratis; Grafana Cloud es de pago por uso | Gratis, 100% open source, autogestionado | Comercial; el *free tier* más generoso del grupo (100 GB/mes) | Comercial, cobra por volumen de datos ingeridos (GB/día); tiende a ser el más costoso a escala |
| **Modelo de despliegue del proyecto en sí (este repo)** | El *código* del demo (`deploy/`, `workflows/`) es 100% open source (MIT); la *plataforma* Dynatrace usada para observarlo es comercial (trial gratuito) | El *código* sería igual de abierto; el stack de observabilidad también sería 100% open source | Igual: 100% open source de punta a punta | Igual patrón que Dynatrace: código abierto, plataforma comercial | Igual patrón que Dynatrace: código abierto, plataforma comercial |
| **Posición Gartner MQ 2025** | Líder (15º año) | Líder (2º año) | No aplica (no es un producto evaluado) | Líder (13ª vez) | Líder (3er año) |

## 3. Por qué se eligió Dynatrace para este proyecto (y no las demás)

La razón **no** es que Dynatrace sea objetivamente "mejor" — la tabla
anterior muestra que las cinco opciones son competentes y, salvo
Prometheus en solitario, todas son Líderes del cuadrante de Gartner. La
razón es de **alcance de un proyecto académico de pocas semanas**:

1. **Un solo agente vs. un stack a ensamblar.** El enunciado del curso pide
   "un agente que recolecte métricas del SO" y "un servidor central que las
   reciba". OneAgent cumple ambos roles con una sola instalación; el stack
   de Grafana/Prometheus habría requerido configurar exporters, targets de
   scraping y dashboards manualmente antes de poder observar nada —tiempo
   que en este proyecto se prefirió invertir en el diseño de la
   arquitectura y el análisis de resultados (Semana 14).
2. **IA de detección de anomalías lista para usar.** El enunciado pide
   explícitamente un componente de IA para detectar comportamientos
   anómalos. Davis AI ya viene entrenado/configurado (causal, no requiere
   dataset de entrenamiento propio); replicar algo equivalente con
   Prometheus habría significado escribir reglas de umbral a mano o
   integrar una librería externa (Isolation Forest, como sugiere el
   enunciado en su opción base), lo cual habría sido otro proyecto en sí
   mismo.
3. **Topología y causa raíz automáticas.** Davis AI correlaciona la
   anomalía con la topología (Smartscape) sin configuración adicional,
   algo directamente relevante para la arquitectura con dependencias
   (`nginx → app → redis`) de este proyecto.
4. **Trial gratuito suficiente para una demo de alcance acotado**, sin
   comprometerse a un costo real de producción.

**Contrapartida honesta:** en un despliegue real de largo plazo, un stack
OSS (Prometheus + Grafana) es más barato de operar a escala y no depende
de un proveedor comercial; y Splunk sigue siendo la opción más natural si
el objetivo prioritario es la convergencia con seguridad/SIEM. Ninguna de
las cinco es una mala elección — la elegida aquí responde al criterio de
**tiempo de instrumentación disponible dentro del cronograma del curso**,
no a una superioridad técnica absoluta.

## 4. Limitaciones de esta comparativa

- No se realizó un benchmark propio cabeza a cabeza entre las cinco
  herramientas (no era el objetivo del proyecto); la comparación se basa
  en documentación oficial y análisis de terceros.
- Los datos de Gartner MQ citados corresponden al reporte 2025; Gartner
  actualiza este cuadrante anualmente y las posiciones pueden cambiar en
  la edición 2026.

## 5. Referencias

1. Gartner. *Magic Quadrant for Observability Platforms*.
   https://www.gartner.com/en/documents/6688834
2. Dynatrace. *Dynatrace Positioned Highest in Execution in the 2025
   Gartner® Magic Quadrant™ for Observability Platforms*.
   https://www.dynatrace.com/news/press-release/2025-gartner-magic-quadrant-for-observability-platform/
3. Datadog. *Datadog named Leader in 2025 Gartner® Magic Quadrant™ for
   Observability Platforms*.
   https://www.datadoghq.com/blog/datadog-observability-platforms-gartner-magic-quadrant-2025/
4. New Relic. *New Relic Named a Leader in 2025 Gartner® Magic Quadrant™
   for Observability Platforms for the 13th Consecutive Time*.
   https://newrelic.com/press-release/20250710
5. Splunk. *Splunk Named a Leader in the 2025 Gartner® Magic Quadrant™ for
   Observability Platforms*.
   https://www.splunk.com/en_us/blog/observability/splunk-leader-in-2025-gartner-magic-quadrant-for-observability-platforms.html
6. Grafana Labs. *Grafana Labs Named a Leader again in the 2025 Gartner®
   Magic Quadrant™ for Observability Platforms*.
   https://grafana.com/blog/grafana-labs-named-a-leader-again-in-the-2025-gartner-magic-quadrant-for-observability-platforms/
7. ARDURA Consulting. *APM Tools 2026: New Relic vs Datadog vs Dynatrace
   vs Open Source*. https://ardura.consulting/blog/apm-tools-comparison-2026/
   — comparación independiente (no vendor) usada para contrastar
   afirmaciones de cada proveedor sobre sí mismo.

---

[⬅ Volver al inicio](../README.md)

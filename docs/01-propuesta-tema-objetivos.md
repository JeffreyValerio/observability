# Semana 11 — Definición del Tema y Objetivos

**Curso:** Sistemas Operativos II
**Estado:** ✅ Tema aprobado por el profesor
**Tema del enunciado:** Opción (f) *Monitor inteligente de sistema (anomaly detection)*

## 1. Título

Monitoreo Inteligente de Sistemas Operativos en Entornos de Red y Nube:
Detección de Anomalías con Observabilidad basada en IA (Dynatrace / Davis AI)

## 2. Tema de investigación

El proyecto estudia cómo un sistema operativo, integrado dentro de una
arquitectura distribuida de contenedores (red local y nube), puede ser
observado de forma continua —CPU, memoria, procesos y red— para **detectar
comportamientos anómalos automáticamente**, en lugar de depender de umbrales
fijos definidos manualmente.

En vez de construir desde cero el pipeline clásico "lectura de `/proc` →
modelo de IA (Isolation Forest / clustering) → alerta", el proyecto usa una
plataforma de observabilidad de nivel productivo, **Dynatrace**, como
implementación de referencia:

- **OneAgent** cumple el rol de "agente que recolecta métricas del SO"
  (lectura de `/proc`, red, procesos, contenedores).
- **Davis AI** cumple el rol del "modelo de IA para detectar comportamientos
  anómalos": es un motor de IA causal/determinística (análisis de árbol de
  fallas) que correlaciona métricas y topología para encontrar anomalías y su
  causa raíz, no solo su síntoma.
- **Workflows** cumple el rol de "notificar o actuar automáticamente".

Esto permite dedicar el esfuerzo de investigación a los conceptos propios del
curso (sistemas distribuidos, concurrencia, alta disponibilidad, rendimiento,
escalabilidad y seguridad) usando una herramienta real de la industria como
caso de estudio, en vez de a la reimplementación de un modelo de detección de
anomalías ya resuelto por la industria.

## 3. Justificación

- Las arquitecturas de microservicios en contenedores/nube hacen que la
  causa raíz de un problema rara vez esté en el mismo componente donde se
  manifiesta el síntoma; esto motiva estudiar observabilidad *causal* y no
  solo monitoreo de métricas aisladas.
- Dynatrace/Davis AI es ampliamente usado en la industria (AIOps) y permite
  observar, con evidencia real, cómo un sistema de detección de anomalías
  basado en IA se comporta ante carga variable, fallas inyectadas y picos de
  uso de recursos.
- El enunciado del curso permite "Propuesta Propia" con aprobación del
  profesor; se elige adaptar el tema (f) del enunciado a una herramienta de
  observabilidad real en lugar de una implementación académica desde cero,
  manteniendo los mismos conceptos exigidos: lectura de métricas del SO,
  arquitectura cliente-servidor para el envío de métricas y monitoreo remoto.

## 4. Objetivo general

Analizar y demostrar la aplicación de una plataforma de observabilidad
basada en inteligencia artificial (Dynatrace/Davis AI) para la detección
automática de anomalías en un sistema operativo distribuido, contenedorizado
y desplegado en red/nube, evaluando su impacto en alta disponibilidad,
rendimiento, escalabilidad y seguridad.

## 5. Objetivos específicos

1. **Analizar** los fundamentos teóricos de la observabilidad de sistemas
   operativos (métricas, logs, trazas, topología) y su relación con alta
   disponibilidad, rendimiento, escalabilidad y seguridad en sistemas
   distribuidos.
2. **Diseñar** una arquitectura de monitoreo distribuido robusta, compuesta
   por un balanceador de carga, múltiples réplicas de un servicio aplicativo,
   una dependencia de almacenamiento y un agente de observabilidad (OneAgent)
   desplegados mediante contenedores.
3. **Implementar** un entorno de demostración funcional en Docker que genere
   tráfico normal y anomalías controladas (picos de CPU/memoria, saturación
   de un componente), instrumentado con OneAgent para su análisis por
   Davis AI.
4. **Configurar** la detección de anomalías basada en IA (Davis AI) y un
   flujo de automatización (Workflow) que notifique o actúe automáticamente
   cuando se abra un problema.
5. **Definir y medir** criterios de evaluación y métricas de rendimiento:
   tiempo de respuesta, distribución del tráfico entre réplicas, tiempo de
   inactividad (downtime) y tiempo de detección de la anomalía (MTTD).
6. **Proponer mejoras** a la arquitectura de observabilidad con base en los
   resultados obtenidos durante las pruebas.

## 6. Alcance y limitaciones

- El proyecto no reimplementa el algoritmo de detección de anomalías; usa
  Davis AI de Dynatrace como motor de IA ya validado por la industria, y se
  enfoca en el diseño de la arquitectura observada, la instrumentación y el
  análisis de resultados.
- La demostración funcional corre en un único host con Docker Compose
  (múltiples contenedores simulando nodos); no se despliega en un clúster
  Kubernetes multi-nodo real, aunque la arquitectura se diseña para ser
  extensible a ese escenario.
- Se requiere un tenant de Dynatrace (SaaS trial gratuito) con acceso a
  Davis AI y Workflows.

## 7. Coordinación con el profesor

- [x] Tema enviado para aprobación (propuesta propia, adaptación del tema f).
- [x] Retroalimentación del profesor incorporada.
- [x] Aprobación final registrada — **medio: Microsoft Teams**, **fecha:
      2026-08-03**.

El tema y los objetivos de este documento quedan **confirmados** para el
resto del proyecto; los siguientes entregables (Semana 12 en adelante) se
construyen sobre esta versión.

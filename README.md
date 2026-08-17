# Monitoreo Inteligente de Sistemas Operativos en Red y en la Nube

Proyecto de Investigación — **Sistemas Operativos II**
Tema del enunciado: *(f) Monitor inteligente de sistema (anomaly detection)*

## Descripción

Este proyecto investiga y demuestra, de forma aplicada, cómo un sistema operativo
integrado en una red de contenedores y en la nube puede monitorearse de forma
inteligente para **detectar anomalías de forma automática**: picos de CPU,
memoria, procesos sospechosos y saturación de red.

En lugar de implementar desde cero el motor de IA para detección de anomalías
(Isolation Forest, clustering, etc.), este proyecto usa **[Dynatrace](https://www.dynatrace.com/)**
—una plataforma de observabilidad de nivel productivo— como **caso de estudio y
herramienta de implementación**, para poder centrar el esfuerzo de investigación
en los conceptos del curso: sockets/telemetría, concurrencia, sistemas
distribuidos, alta disponibilidad, escalabilidad y seguridad, en lugar de
reinventar un motor de detección de anomalías.

Dynatrace recolecta métricas del sistema operativo mediante **OneAgent** (lectura
de `/proc`, red, procesos) y aplica **Davis AI**, un motor de IA causal y
determinística (fault-tree analysis) que detecta anomalías y encuentra causa
raíz sin depender únicamente de umbrales estáticos. Un **Workflow** de
Dynatrace se encarga de notificar/actuar automáticamente cuando Davis abre un
problema.

> ✅ Tema aprobado por el profesor. Ver [`docs/01-propuesta-tema-objetivos.md`](docs/01-propuesta-tema-objetivos.md)
> para la definición formal (Semana 11).

## Objetivo general

Analizar y demostrar la aplicación de una plataforma de observabilidad basada
en IA (Dynatrace/Davis AI) para la detección automática de anomalías en un
sistema distribuido contenedorizado, evaluando alta disponibilidad, rendimiento,
escalabilidad y seguridad.

Objetivos específicos completos en
[`docs/01-propuesta-tema-objetivos.md`](docs/01-propuesta-tema-objetivos.md#5-objetivos-específicos).

## Arquitectura (resumen)

```
                    ┌─────────────────────┐
   load-generator ─▶│   frontend (nginx)   │─▶  app (N réplicas) ─▶ redis
   (tráfico normal   │   balanceo de carga  │        │
    + anomalías)      └─────────────────────┘        │
                                │                     │
                                ▼                     ▼
                        OneAgent (host) ──── métricas/procesos/red
                                │
                                ▼
                     Dynatrace (Davis AI) ── detección de anomalías
                                │
                                ▼
                       Workflow de notificación
```

Detalle completo en [`docs/arquitectura.md`](docs/arquitectura.md).

## Estructura del repositorio

```
.
├── docs/                  Entregables académicos por semana (cronograma)
├── deploy/                Stack de demo: app, redis, nginx, load-generator, OneAgent
├── workflows/             Ejemplo de Workflow de Dynatrace (notificación ante anomalía)
├── dashboards/            Notas para exportar/versionar dashboards de Dynatrace
└── LICENSE                MIT
```

## Demo funcional (quick start)

Requisitos: Docker + Docker Compose, y un tenant de Dynatrace (SaaS trial
gratuito válido) con acceso a Davis AI y Workflows.

El proyecto corre en **un solo host** (tu máquina): los "nodos" que se
observan son contenedores (`frontend`, N réplicas de `app`, `redis`,
`load-generator`), no máquinas físicas separadas — ver limitaciones en
[`docs/01-propuesta-tema-objetivos.md`](docs/01-propuesta-tema-objetivos.md#6-alcance-y-limitaciones).

Hay dos formas de tener OneAgent en ese host, según si ya lo instalaste o no:

**A) Ya tienes OneAgent instalado en el host** (fuera de Docker): solo
levanta el resto del stack; OneAgent detecta los contenedores nuevos
automáticamente, sin configuración adicional.

```bash
cd deploy
docker compose up --build --scale app=3 -d
```

**B) Todavía no tienes OneAgent en el host:** activa el profile
`with-oneagent` para que Docker Compose lo instale por ti (ver
[`deploy/oneagent/README.md`](deploy/oneagent/README.md) para los tokens
requeridos en `.env`).

```bash
cp .env.example .env
# completar DT_ENVIRONMENT_URL y ONEAGENT_INSTALLER_TOKEN en .env

cd deploy
docker compose --profile with-oneagent up --build --scale app=3 -d
```

> ⚠️ No mezclar A y B: activar el profile `with-oneagent` cuando el host ya
> tiene OneAgent instalado manualmente produce dos instalaciones compitiendo
> por el mismo host.

Esto levanta:

| Servicio        | Rol                                                         |
|------------------|--------------------------------------------------------------|
| `oneagent`       | (solo con el profile `with-oneagent`) Instala OneAgent en el host y envía telemetría a Dynatrace |
| `frontend`       | Balanceador nginx que distribuye tráfico entre las réplicas de `app` |
| `app`            | Servicio Flask de ejemplo con endpoints normales y endpoints `/chaos/*` que simulan anomalías (spike de CPU/memoria) |
| `redis`          | Dependencia de almacenamiento, para observar un sistema con más de un componente |
| `load-generator` | Genera tráfico normal y, con cierta probabilidad, dispara los endpoints de caos para que Davis AI tenga anomalías reales que detectar |

Instrucciones detalladas de OneAgent en [`deploy/oneagent/README.md`](deploy/oneagent/README.md).

## Cronograma y evaluación

| Semana | Actividad | Entregable | Estado |
|---|---|---|---|
| 11 | Definición de tema y objetivos | [`docs/01-propuesta-tema-objetivos.md`](docs/01-propuesta-tema-objetivos.md) | ✅ Aprobado |
| 12 | Plan de trabajo y metodología | [`docs/02-plan-trabajo-metodologia.md`](docs/02-plan-trabajo-metodologia.md) | ✅ Finalizado |
| 13 | Revisión bibliográfica / marco teórico | [`docs/03-revision-bibliografica.md`](docs/03-revision-bibliografica.md) | ✅ Finalizado |
| 14 | Desarrollo y análisis de resultados | [`docs/04-desarrollo-resultados.md`](docs/04-desarrollo-resultados.md) | ✅ Cerrado |
| 15 | Informe final y presentación | [`docs/05-informe-final.md`](docs/05-informe-final.md) | ✅ Cerrado |

## Documentación adicional

No forman parte del cronograma de semanas 11–15, pero sustentan la
justificación de herramienta y la presentación final:

| Documento | Contenido |
|---|---|
| [`docs/06-comparativa-herramientas.md`](docs/06-comparativa-herramientas.md) | Comparativa objetiva Dynatrace vs. Grafana/Prometheus vs. New Relic vs. Splunk, con el Cuadrante Mágico de Gartner 2025 |
| [`docs/07-presentacion.md`](docs/07-presentacion.md) | Guion de la presentación final (5–10 min), slide por slide |

## Licencia

Este proyecto se distribuye bajo la licencia [MIT](LICENSE).

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
gratuito válido) con un token de instalación de OneAgent y un token de API.

```bash
cp .env.example .env
# completar DT_ENVIRONMENT_URL, ONEAGENT_INSTALLER_TOKEN y DT_API_TOKEN en .env

cd deploy
docker compose up --build --scale app=3 -d
```

Esto levanta:

| Servicio        | Rol                                                         |
|------------------|--------------------------------------------------------------|
| `oneagent`       | Instala OneAgent en el host/contenedores y envía telemetría a Dynatrace |
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
| 14 | Desarrollo y análisis de resultados | [`docs/04-desarrollo-resultados.md`](docs/04-desarrollo-resultados.md) | ⏳ Pendiente |
| 15 | Informe final y presentación | [`docs/05-informe-final.md`](docs/05-informe-final.md) | ⏳ Pendiente |

## Licencia

Este proyecto se distribuye bajo la licencia [MIT](LICENSE).

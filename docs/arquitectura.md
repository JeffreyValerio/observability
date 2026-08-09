# Arquitectura

## 1. Vista general

```
┌───────────────────┐        ┌──────────────────────────┐
│  load-generator    │──HTTP─▶│  frontend (nginx)         │
│  tráfico normal +   │        │  balanceo de carga        │
│  anomalías (/chaos) │        └────────────┬─────────────┘
└───────────────────┘                     │
                                            ▼
                        ┌───────────────────────────────────┐
                        │   app (N réplicas, Flask)          │
                        │   /            → info + hostname   │
                        │   /health      → readiness         │
                        │   /work        → carga normal      │
                        │   /chaos/cpu   → spike CPU          │
                        │   /chaos/memory→ spike memoria      │
                        └────────────────┬────────────────────┘
                                          ▼
                                 ┌────────────────┐
                                 │     redis       │
                                 └────────────────┘

Todos los contenedores del host son observados por:

┌──────────────────────────────────────────────────────────────┐
│  OneAgent (host / full-stack)                                  │
│  lee /proc, red, procesos y métricas de cada contenedor         │
└───────────────────────────┬──────────────────────────────────┘
                             ▼
                   ┌───────────────────┐
                   │  Dynatrace (SaaS)  │
                   │  Davis AI          │──▶ Problema detectado
                   └─────────┬─────────┘
                             ▼
                   ┌───────────────────┐
                   │  Workflow          │──▶ Notificación / acción
                   │  (davis-problem)   │
                   └───────────────────┘
```

## 2. Componentes

| Componente | Rol | Concepto del curso que cubre |
|---|---|---|
| `frontend` (nginx) | Balanceo de carga entre réplicas de `app` | Distribución del tráfico, escalabilidad horizontal |
| `app` (Flask, N réplicas) | Servicio observado; expone endpoints normales y de caos | Concurrencia, cliente-servidor, procesos |
| `redis` | Dependencia de almacenamiento compartida | Almacenamiento distribuido, punto único de contención |
| `load-generator` | Cliente que genera tráfico normal y anomalías controladas | Cliente-servidor, generación de carga |
| OneAgent | Agente que recolecta métricas del SO/red/procesos de cada nodo | Lectura de `/proc`, monitoreo remoto |
| Davis AI | Motor de IA causal para detección de anomalías y causa raíz | "IA: modelos para detectar comportamientos anómalos" del enunciado |
| Workflow | Automatización disparada por problemas de Davis AI | Notificación/acción automática |

## 3. Decisiones de diseño

- **Alta disponibilidad:** múltiples réplicas de `app` detrás de un
  balanceador; se mide el tiempo de inactividad al detener una réplica.
- **Rendimiento:** el load-generator produce tráfico variable para poder
  medir tiempo de respuesta p50/p95 en condiciones normales vs. anómalas.
- **Escalabilidad:** `app` se escala horizontalmente vía
  `docker compose up --scale app=N`; la arquitectura no asume un número fijo
  de réplicas (nginx usa resolución dinámica de DNS del servicio `app`).
- **Seguridad:** el token de instalación de OneAgent y el token de API se
  inyectan por variables de entorno (`.env`, no versionado); no se
  hardcodean credenciales en el repositorio. Los endpoints `/chaos/*` son
  exclusivamente para el entorno de demostración y deben documentarse como
  tales (no exponer en un despliegue real).

## 4. Extensibilidad

La arquitectura se diseñó para poder migrar de Docker Compose (un solo host)
a Kubernetes multi-nodo sin cambiar los roles de los componentes: OneAgent
se despliega como DaemonSet, `app` como Deployment con HPA, y el Workflow de
Dynatrace no cambia. Esa migración queda fuera del alcance de este proyecto
(ver limitaciones en `docs/01-propuesta-tema-objetivos.md`).

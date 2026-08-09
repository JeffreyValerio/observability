# Dashboards

Carpeta para versionar los dashboards de Dynatrace usados en la Semana 14
(desarrollo y análisis de resultados) y en el informe final.

## Cómo agregar un dashboard

1. En Dynatrace, crear un dashboard con los tiles relevantes para este
   proyecto:
   - Tiempo de respuesta (p50/p95) del servicio `app`.
   - Uso de CPU y memoria por contenedor/réplica.
   - Distribución de tráfico entre réplicas (nginx/Smartscape).
   - Línea de tiempo de problemas abiertos por Davis AI.
   - Ejecuciones del Workflow `anomaly-auto-notify`.
2. Exportar el dashboard como JSON (`⋮` > *Export to JSON* en la vista del
   dashboard, o `GET /api/config/v1/dashboards/{id}` de la API v1).
3. Guardar el archivo exportado en esta carpeta, por ejemplo
   `dashboards/observability-demo.json`, y referenciarlo desde la sección
   [Resultados](../docs/04-desarrollo-resultados.md#3-resultados) de
   `docs/04-desarrollo-resultados.md`.

No se incluye un dashboard exportado por defecto en este repositorio porque
depende del tenant y de los datos reales generados durante la Semana 14.

---

[⬅ Volver al inicio](../README.md)

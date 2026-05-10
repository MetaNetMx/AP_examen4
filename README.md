# AP_examen4 — Unidad 4 (Despliegue ético y decisión basada en modelos)

Proyecto integrador para Analítica Predictiva:

- Pipeline reproducible (ingesta, limpieza, split, entrenamiento, validación).
- Monitoreo y reglas de retraining.
- Decisiones por umbrales, sensibilidad e impacto económico.
- Documentación ética, cumplimiento y comunicación ejecutiva.

## Estructura

- `notebooks/pipeline_predictivo_integrado.ipynb`: notebook principal reproducible.
- `src/pipeline_financiero.py`: funciones del pipeline.
- `docs/documento_tecnico.md`: fases, métricas, triggers y respuestas técnicas.
- `docs/reporte_ejecutivo.md`: narrativa para comité y recomendaciones.
- `docs/anexo_etico.md`: checklist de cumplimiento y mitigaciones.
- `docs/bitacora_monitoreo.md`: indicadores y decisiones registradas.

## Ejecución

```bash
python3 -m pip install -r requirements.txt
jupyter notebook notebooks/pipeline_predictivo_integrado.ipynb
```

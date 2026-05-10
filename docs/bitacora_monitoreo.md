# Bitácora de monitoreo y retraining

## Objetivo

Registrar indicadores críticos del modelo, decisiones tomadas y justificación para trazabilidad operativa y auditoría.

---

## Definición de indicadores

- **ROC AUC** (clasificación default): detectar pérdida de discriminación.
- **MAE** (regresión pérdida esperada): detectar degradación de error absoluto.
- **PSI promedio**: estabilidad global de distribución de variables.
- **PSI máximo por variable**: identificar drift crítico focalizado.
- **Días desde último entrenamiento**: control de política trimestral.

Umbrales:

- Retraining programado: >= 90 días.
- Drift: PSI promedio > 0.20 o PSI variable > 0.25.
- Performance: caída ROC AUC > 0.05 o aumento MAE > 15%.

---

## Registro de decisiones

| Fecha corte | ROC AUC baseline | ROC AUC actual | MAE baseline | MAE actual | PSI promedio | PSI máximo | Días desde train | Decisión | Motivo |
|---|---:|---:|---:|---:|---:|---:|---:|---|---|
| 2026-05-10 | 0.6986 | 0.6916 | 0.8959 | 0.9446 | 0.0601 | 0.3023 | 115 | Reentrenar | Calendario + drift variable crítico |

---

## Acciones derivadas

1. Lanzar proceso de reentrenamiento y validación independiente.
2. Revisar política de umbral (referencia operativa: PD 0.70).
3. Ejecutar análisis de fairness por subgrupos antes de liberar nueva versión.
4. Actualizar anexo ético y reporte al comité en la siguiente sesión mensual.

---

## Evidencia asociada

Archivos de soporte (generados por notebook):

- `artifacts/drift_indicadores.csv`
- `artifacts/comparativo_metricas.csv`
- `artifacts/decision_retraining.json`
- `artifacts/sensibilidad_umbrales.csv`
- `artifacts/escenarios_impacto_economico.csv`

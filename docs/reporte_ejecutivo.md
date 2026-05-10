# Reporte ejecutivo — Decisiones financieras basadas en modelos (Unidad 4)

## Resumen ejecutivo (no técnico)

Se desarrolló un pipeline reproducible para apoyar decisiones de riesgo crediticio con dos capacidades:

1. **Predecir probabilidad de default** de clientes.
2. **Estimar pérdida esperada** para anticipar impacto financiero.

El sistema incluye monitoreo de drift y desempeño, además de reglas automáticas de retraining.  
En la simulación de operación, el modelo **sí reduce pérdidas esperadas** frente a no usar política, pero en escenarios adversos aún se observan resultados netos negativos, por lo que la decisión óptima requiere combinar analítica con estrategia comercial y controles de riesgo.

---

## Hallazgos clave

1. **Desempeño predictivo robusto en validación**
   - ROC AUC ~0.70 en clasificación de default.
   - MAE ~0.90 en regresión de pérdida esperada.

2. **Se detectó señal de drift relevante en `ratio_deuda_ingreso`**
   - PSI máximo = 0.302 (> 0.25).
   - Disparó alerta de monitoreo.

3. **Retraining recomendado**
   - El modelo supera 90 días desde último entrenamiento.
   - Hay drift por variable crítica.

4. **Umbral operativo recomendado: PD = 0.70**
   - Balancea tasa de aprobación y control de riesgo.
   - Mantiene una política clara para comités de crédito.

---

## Tabla de escenarios (k = miles de unidades monetarias)

| Escenario | Pérdida sin política | Pérdida con política | Ahorro generado | Beneficio neto |
|---|---:|---:|---:|---:|
| Optimista | 2360.05 | 1246.96 | 1113.09 | -820.04 |
| Base | 2776.53 | 1467.01 | 1309.52 | -1097.56 |
| Pesimista | 3503.92 | 1907.12 | 1596.81 | -1595.14 |

Interpretación ejecutiva:

- El modelo reduce pérdida en todos los escenarios.
- En crisis, el ahorro no alcanza por sí solo: se requieren acciones adicionales de negocio y riesgo.

---

## Recomendaciones priorizadas (accionables)

### Prioridad alta (inmediata)

1. **Ejecutar retraining** del modelo en el próximo ciclo operativo.
2. **Activar control reforzado** sobre clientes con PD > 0.70.
3. **Monitorear semanalmente** PSI de variables críticas y ROC AUC/MAE.

### Prioridad media

4. Incorporar variables macroeconómicas (inflación, desempleo, tasa de interés) para robustecer escenarios.
5. Ajustar pricing y límites para segmentos con mayor pérdida esperada.

### Prioridad de gobernanza

6. Formalizar comité de revisión mensual (Riesgo + Cumplimiento + Negocio) con bitácora firmada.

---

## Plan de seguimiento (90 días)

- **Semanal**: monitoreo de drift/performance y registro en bitácora.
- **Mensual**: revisión de umbrales y sensibilidad por comité.
- **Trimestral**: retraining programado + validación ética/cumplimiento.

---

## Guion sugerido para presentación de 5–7 minutos

1. Problema de negocio y riesgo (1 min).
2. Qué hace el pipeline y por qué es confiable (1.5 min).
3. Resultados clave de métricas y escenarios (2 min).
4. Recomendaciones priorizadas y plan de seguimiento (1.5 min).
5. Cierre: decisión solicitada al comité (1 min).

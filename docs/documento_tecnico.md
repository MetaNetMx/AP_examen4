# Documento técnico — Pipeline predictivo integrado y despliegue ético

## 1) Objetivo

Construir un pipeline reproducible para decisiones financieras basadas en modelos, integrando:

- Evidencia predictiva (clasificación de default y regresión de pérdida esperada).
- Criterios de activación y análisis de sensibilidad.
- Monitoreo continuo y reglas de retraining.
- Trazabilidad, ética y gobernanza para auditoría regulatoria.

---

## 2) Arquitectura del pipeline (Parte 4.1)

Implementación principal:

- `src/pipeline_financiero.py`
- `notebooks/pipeline_predictivo_integrado.ipynb`

### 2.1 Flujo de orquestación

1. **Ingesta**: generación/carga de datos financieros.
2. **Limpieza**:
   - imputación de faltantes (`SimpleImputer`, mediana),
   - escalamiento (`StandardScaler`) para estabilidad numérica.
3. **Split reproducible**:
   - train 60% / validation 20% / test 20%,
   - estratificación por variable de default.
4. **Entrenamiento**:
   - Modelo 1 (clasificación): `LogisticRegression`.
   - Modelo 2 (regresión): `RandomForestRegressor`.
5. **Validación**:
   - Clasificación: ROC AUC, F1, precision, recall.
   - Regresión: MAE, RMSE, R².
6. **Monitoreo**:
   - Drift por variable con PSI.
   - Degradación de desempeño (ROC AUC y MAE).
7. **Retraining**:
   - Por calendario.
   - Por drift.
   - Por degradación de performance.

---

## 3) Métricas clave de entrenamiento/validación

Resultados obtenidos en validación baseline:

| Métrica | Valor |
|---|---:|
| ROC AUC | 0.6986 |
| F1 | 0.6714 |
| Precision | 0.6811 |
| Recall | 0.6620 |
| MAE | 0.8959 |
| RMSE | 1.3989 |
| R² | 0.9874 |

Interpretación:

- El clasificador discrimina riesgo de default con desempeño moderado-alto (ROC AUC ~0.70).
- El regresor captura bien variación de pérdida esperada (R² alto; MAE controlado).

---

## 4) Monitoreo y retraining (Parte 4.1)

### 4.1 Indicadores de monitoreo

1. **Drift de datos (PSI)**:
   - PSI promedio: `0.0601`.
   - PSI máximo: `0.3023` (variable `ratio_deuda_ingreso`).
2. **Caída de desempeño en ventana actual**:
   - ROC AUC: 0.6986 -> 0.6916 (caída 0.0070).
   - MAE: 0.8959 -> 0.9446 (subida relativa ~5.4%).

### 4.2 Triggers de retraining definidos

- **Calendario**: reentrenar cada 90 días.
- **Drift**:
  - PSI promedio > 0.20, o
  - PSI por variable > 0.25.
- **Desempeño**:
  - caída ROC AUC > 0.05, o
  - aumento MAE > 15% relativo.

### 4.3 Resultado de decisión de retraining

Salida del motor de decisión:

- `reentrenar = true`
- Motivos:
  1. `retraining_programado_115_dias`
  2. `drift_variable_alto_0.302`

---

## 5) Decisiones, umbrales y sensibilidad (Parte 4.2)

### 5.1 Criterios de activación (mínimo 3)

1. **C1**: activar alerta si `P(default) > 0.70`.
2. **C2**: activar alerta si `caida_ingresos_12m > 15%`.
3. **C3**: activar alerta si `PSI_promedio > 0.20`.

### 5.2 Sensibilidad por umbral de probabilidad

| Umbral PD | Tasa aprobación | Default en aprobados | Default en rechazados |
|---:|---:|---:|---:|
| 0.50 | 0.2950 | 0.3475 | 0.6135 |
| 0.60 | 0.4908 | 0.4007 | 0.6645 |
| 0.70 | 0.6842 | 0.4373 | 0.7467 |
| 0.80 | 0.8608 | 0.4947 | 0.7844 |

Lectura:

- Al subir el umbral, crece aprobación, pero también aumenta default dentro del grupo aprobado.
- Umbral 0.70 logra equilibrio entre cobertura comercial y contención de riesgo.

### 5.3 Impacto económico por escenario

Unidades monetarias en miles (k), política con umbral PD=0.70:

| Escenario | Pérdida sin política | Pérdida con política | Ahorro vs sin política | Ingresos | Beneficio neto |
|---|---:|---:|---:|---:|---:|
| Optimista | 2360.05 | 1246.96 | 1113.09 | 426.92 | -820.04 |
| Base | 2776.53 | 1467.01 | 1309.52 | 369.45 | -1097.56 |
| Pesimista | 3503.92 | 1907.12 | 1596.81 | 311.98 | -1595.14 |

Conclusión:

- La política reduce pérdida esperada de forma consistente.
- En escenarios de estrés, la mejora relativa existe, pero no evita deterioro del beneficio neto; se requieren medidas complementarias (precio, garantías, límites por segmento).

---

## 6) Respuestas a preguntas de examen

### 6.1 ¿Cómo garantizar trazabilidad auditada por comité regulador?

Con una cadena de evidencia completa:

1. Versionado de código y parámetros (Git + tags de versión del modelo).
2. Registro de datasets por corte (hash, fecha, fuente, responsable).
3. Bitácora inmutable de métricas baseline y de producción.
4. Políticas de retraining codificadas y trazables (reglas explícitas).
5. Persistencia de artefactos de monitoreo (`CSV/JSON`) con timestamp.
6. Flujo de aprobación con doble validación (riesgo + cumplimiento).

### 6.2 ¿Riesgos de umbrales demasiado conservadores en crisis?

- Sobre-restricción crediticia y pérdida de ingresos.
- Exclusión injustificada de clientes solventes (falsos positivos).
- Sesgo de acceso financiero para grupos sensibles.
- Efecto procíclico: el modelo amplifica la contracción económica.

### 6.3 ¿Cómo comunicar cumplimiento ético/gobernanza a comité de inversión?

- Usar tablero ejecutivo con semáforos de privacidad, equidad y transparencia.
- Mostrar métricas de sesgo, controles de explicabilidad y plan de mitigación.
- Evidenciar responsables, frecuencia de monitoreo y gatillos de intervención.
- Presentar pruebas de cumplimiento normativo y decisiones trazables.

### 6.4 ¿Cómo diferenciar comunicación técnica vs ejecutiva?

- **Público técnico**: métricas, hipótesis, supuestos estadísticos, validación y límites del modelo.
- **Comité ejecutivo**: impacto en riesgo/retorno, escenarios, decisiones recomendadas y plan de acción.

---

## 7) Instrucciones de reproducción

```bash
python3 -m pip install -r requirements.txt
jupyter notebook notebooks/pipeline_predictivo_integrado.ipynb
```

Artefactos esperados al ejecutar:

- `artifacts/drift_indicadores.csv`
- `artifacts/sensibilidad_umbrales.csv`
- `artifacts/escenarios_impacto_economico.csv`
- `artifacts/decision_retraining.json`
- `artifacts/comparativo_metricas.csv`

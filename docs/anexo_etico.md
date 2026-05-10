# Anexo ético — Despliegue responsable del modelo financiero

## 1) Alcance y propósito

Este anexo documenta cómo el pipeline predictivo cumple principios de uso responsable para despliegue en decisiones financieras, incluyendo privacidad, equidad, transparencia y gobernanza.

---

## 2) Principios aplicados

## 2.1 Privacidad y protección de datos

- Minimización de datos: se usan variables necesarias para el objetivo de riesgo.
- Separación de datos sensibles directos (no se incluyen identificadores personales en el modelo base).
- Trazabilidad de acceso y procesamiento por lote.
- Recomendación operativa: cifrado en tránsito y en reposo, y controles de acceso por rol.

## 2.2 Equidad y no discriminación

- Revisión de variables proxy que puedan inducir sesgo indirecto.
- Monitoreo de métricas por subgrupos (ej. aprobación, falsos positivos, falsos negativos).
- Definición de umbrales con análisis de impacto, evitando exclusión desproporcionada.

## 2.3 Transparencia y explicabilidad

- Documentación clara de supuestos, métricas y umbrales.
- Evidencia auditable de retraining y monitoreo.
- Comunicación diferenciada para público técnico y ejecutivo.

## 2.4 Robustez y seguridad

- Validación train/validation/test reproducible.
- Monitoreo de drift de datos y degradación de performance.
- Plan de contingencia cuando se exceden umbrales (alerta + revisión humana + retraining).

## 2.5 Gobernanza y supervisión humana

- Decisiones automatizadas sujetas a revisión por comité de riesgo.
- Responsables definidos por etapa: model owner, risk owner, compliance owner.
- Escalamiento formal cuando hay señales de sesgo, drift severo o impacto económico adverso.

---

## 3) Checklist de cumplimiento

| Criterio | Estado | Evidencia |
|---|---|---|
| Política de minimización de datos | Cumple | Variables de negocio acotadas en pipeline |
| Versionado y trazabilidad | Cumple | Código y artefactos versionados |
| Monitoreo continuo de drift/performance | Cumple | PSI + ROC AUC/MAE con bitácora |
| Reglas explícitas de retraining | Cumple | Triggers codificados y auditables |
| Transparencia para stakeholders | Cumple | Documento técnico + reporte ejecutivo |
| Revisión de sesgo por subgrupos | Parcial | Recomendado como paso siguiente obligatorio |
| Procedimiento de apelación/revisión humana | Parcial | Definir flujo operativo formal |
| Alineación regulatoria documentada | Parcial | Ajustar según normativa local específica |

---

## 4) Alineación regulatoria (referencial)

Este diseño se alinea conceptualmente con:

- **OECD AI Principles**: robustez, transparencia, responsabilidad y enfoque centrado en personas.
- Marco de gestión de riesgo de modelos para sector financiero (gobernanza + validación independiente).
- Normativa local de protección de datos personales (debe adaptarse al país/entidad aplicable).

> Nota: antes del despliegue productivo, el área legal/compliance debe mapear este anexo a la regulación específica de la jurisdicción.

---

## 5) Supuestos y sesgos potenciales

Supuestos de modelado:

1. Las relaciones históricas entre variables y default se mantienen en ventana corta.
2. Las variables disponibles representan adecuadamente riesgo de crédito.
3. El costo de error tipo I/II se gestiona vía umbrales y políticas de comité.

Sesgos potenciales:

- Sesgo de selección en datos históricos.
- Sesgo de medición en variables de ingreso/deuda.
- Sesgo por drift macroeconómico no capturado oportunamente.

---

## 6) Medidas de mitigación propuestas

1. Evaluación periódica de fairness por segmento relevante.
2. Retraining basado en calendario + señales de drift/desempeño.
3. Inclusión de variables macro para estabilidad en crisis.
4. Validación independiente previa a cambios de umbral.
5. Proceso de override humano documentado y auditado.

---

## 7) Comunicación al comité de inversión (pregunta de examen 4.3)

Para comunicar cumplimiento ético/gobernanza de forma efectiva:

- Presentar una **matriz semaforizada** (cumple/parcial/no cumple) con evidencia.
- Mostrar riesgos residuales y controles compensatorios.
- Explicar responsabilidades, frecuencia de monitoreo y rutas de escalamiento.
- Enfatizar que el modelo **no reemplaza** el juicio humano en decisiones de alto impacto.

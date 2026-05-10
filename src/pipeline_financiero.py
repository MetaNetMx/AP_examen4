"""Pipeline predictivo financiero con monitoreo y retraining.

Este módulo concentra funciones reutilizables para:
1) Generar datos sintéticos de riesgo crediticio.
2) Orquestar limpieza, split y entrenamiento.
3) Evaluar modelos de clasificación y regresión.
4) Monitorear drift y degradación de desempeño.
5) Definir reglas auditables de reentrenamiento.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, Tuple

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestRegressor
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    f1_score,
    mean_absolute_error,
    mean_squared_error,
    precision_score,
    r2_score,
    recall_score,
    roc_auc_score,
)
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler


FEATURE_COLUMNS = [
    "edad",
    "ingreso_mensual",
    "ratio_deuda_ingreso",
    "utilizacion_credito",
    "historial_moras_12m",
    "antiguedad_laboral_anios",
    "caida_ingresos_12m",
    "saldo_promedio",
]


@dataclass(frozen=True)
class SplitData:
    """Estructura de datos para train/validation/test."""

    x_train: pd.DataFrame
    x_val: pd.DataFrame
    x_test: pd.DataFrame
    y_train_clf: pd.Series
    y_val_clf: pd.Series
    y_test_clf: pd.Series
    y_train_reg: pd.Series
    y_val_reg: pd.Series
    y_test_reg: pd.Series


def generar_datos_sinteticos(n_muestras: int = 6000, semilla: int = 42) -> pd.DataFrame:
    """Genera un dataset sintético para riesgo de crédito."""
    rng = np.random.default_rng(semilla)

    edad = rng.normal(39, 10, n_muestras).clip(21, 75)
    ingreso_mensual = rng.lognormal(mean=7.9, sigma=0.42, size=n_muestras)
    ratio_deuda_ingreso = rng.beta(2.2, 4.5, n_muestras)
    utilizacion_credito = rng.beta(2.8, 3.2, n_muestras)
    historial_moras_12m = rng.poisson(0.9, n_muestras).clip(0, 8)
    antiguedad_laboral_anios = rng.gamma(shape=3.0, scale=2.2, size=n_muestras).clip(0.5, 35)
    caida_ingresos_12m = rng.normal(0.04, 0.13, n_muestras).clip(-0.2, 0.6)
    saldo_promedio = ingreso_mensual * rng.uniform(1.0, 3.8, n_muestras)

    # Probabilidad de default (clasificación)
    logit = (
        -2.2
        + 3.6 * ratio_deuda_ingreso
        + 2.2 * utilizacion_credito
        + 0.25 * historial_moras_12m
        + 2.7 * caida_ingresos_12m
        - 0.03 * antiguedad_laboral_anios
        - 0.012 * (edad - 40)
    )
    prob_default = 1 / (1 + np.exp(-logit))
    default = rng.binomial(1, prob_default)

    # Severidad de pérdida esperada (regresión) en miles de unidades monetarias.
    perdida_esperada_k = (
        1.8
        + 0.0028 * saldo_promedio
        + 3.2 * ratio_deuda_ingreso
        + 2.7 * utilizacion_credito
        + 2.1 * caida_ingresos_12m
        + 0.55 * default
        + rng.normal(0, 0.9, n_muestras)
    ).clip(0.2, None)

    data = pd.DataFrame(
        {
            "edad": edad,
            "ingreso_mensual": ingreso_mensual,
            "ratio_deuda_ingreso": ratio_deuda_ingreso,
            "utilizacion_credito": utilizacion_credito,
            "historial_moras_12m": historial_moras_12m,
            "antiguedad_laboral_anios": antiguedad_laboral_anios,
            "caida_ingresos_12m": caida_ingresos_12m,
            "saldo_promedio": saldo_promedio,
            "default": default,
            "perdida_esperada_k": perdida_esperada_k,
        }
    )

    # Introduce faltantes para simular calidad de dato real.
    for col in ["ingreso_mensual", "ratio_deuda_ingreso", "utilizacion_credito"]:
        idx = rng.choice(data.index, size=int(n_muestras * 0.025), replace=False)
        data.loc[idx, col] = np.nan

    return data


def preparar_datos(data: pd.DataFrame, semilla: int = 42) -> SplitData:
    """Realiza split estratificado train/validation/test."""
    x = data[FEATURE_COLUMNS]
    y_clf = data["default"]
    y_reg = data["perdida_esperada_k"]

    x_temp, x_test, y_temp_clf, y_test_clf, y_temp_reg, y_test_reg = train_test_split(
        x,
        y_clf,
        y_reg,
        test_size=0.2,
        random_state=semilla,
        stratify=y_clf,
    )

    x_train, x_val, y_train_clf, y_val_clf, y_train_reg, y_val_reg = train_test_split(
        x_temp,
        y_temp_clf,
        y_temp_reg,
        test_size=0.25,  # 0.25 de 0.8 = 0.2
        random_state=semilla,
        stratify=y_temp_clf,
    )

    return SplitData(
        x_train=x_train,
        x_val=x_val,
        x_test=x_test,
        y_train_clf=y_train_clf,
        y_val_clf=y_val_clf,
        y_test_clf=y_test_clf,
        y_train_reg=y_train_reg,
        y_val_reg=y_val_reg,
        y_test_reg=y_test_reg,
    )


def construir_preprocesador() -> ColumnTransformer:
    """Crea preprocesamiento numérico estándar."""
    numeric_pipeline = Pipeline(
        steps=[("imputer", SimpleImputer(strategy="median")), ("scaler", StandardScaler())]
    )
    return ColumnTransformer([("numeric", numeric_pipeline, FEATURE_COLUMNS)])


def entrenar_modelos(split_data: SplitData) -> Dict[str, Pipeline]:
    """Entrena modelos de clasificación y regresión."""
    pre = construir_preprocesador()

    model_clf = Pipeline(
        steps=[
            ("preprocess", pre),
            (
                "model",
                LogisticRegression(
                    max_iter=1200,
                    class_weight="balanced",
                    solver="lbfgs",
                    random_state=42,
                ),
            ),
        ]
    )

    model_reg = Pipeline(
        steps=[
            ("preprocess", pre),
            ("model", RandomForestRegressor(n_estimators=260, min_samples_leaf=4, random_state=42)),
        ]
    )

    model_clf.fit(split_data.x_train, split_data.y_train_clf)
    model_reg.fit(split_data.x_train, split_data.y_train_reg)

    return {"clasificacion_default": model_clf, "regresion_perdida": model_reg}


def evaluar_modelos(split_data: SplitData, modelos: Dict[str, Pipeline]) -> Dict[str, float]:
    """Evalúa métricas de validación para ambos modelos."""
    clf = modelos["clasificacion_default"]
    reg = modelos["regresion_perdida"]

    y_val_prob = clf.predict_proba(split_data.x_val)[:, 1]
    y_val_pred = (y_val_prob >= 0.5).astype(int)
    y_val_reg = reg.predict(split_data.x_val)

    roc_auc = roc_auc_score(split_data.y_val_clf, y_val_prob)
    f1 = f1_score(split_data.y_val_clf, y_val_pred)
    precision = precision_score(split_data.y_val_clf, y_val_pred)
    recall = recall_score(split_data.y_val_clf, y_val_pred)

    mae = mean_absolute_error(split_data.y_val_reg, y_val_reg)
    rmse = mean_squared_error(split_data.y_val_reg, y_val_reg) ** 0.5
    r2 = r2_score(split_data.y_val_reg, y_val_reg)

    return {
        "roc_auc": float(roc_auc),
        "f1": float(f1),
        "precision": float(precision),
        "recall": float(recall),
        "mae": float(mae),
        "rmse": float(rmse),
        "r2": float(r2),
    }


def population_stability_index(expected: pd.Series, actual: pd.Series, bins: int = 10) -> float:
    """Calcula PSI para detectar drift de distribución."""
    expected = expected.dropna()
    actual = actual.dropna()
    quantiles = np.linspace(0, 1, bins + 1)
    cuts = np.unique(np.quantile(expected, quantiles))
    if len(cuts) < 3:
        return 0.0

    eps = 1e-6
    exp_bins = pd.cut(expected, bins=cuts, include_lowest=True)
    act_bins = pd.cut(actual, bins=cuts, include_lowest=True)
    exp_dist = exp_bins.value_counts(normalize=True, sort=False).clip(eps, 1)
    act_dist = act_bins.value_counts(normalize=True, sort=False).clip(eps, 1)
    psi = np.sum((act_dist - exp_dist) * np.log(act_dist / exp_dist))
    return float(psi)


def monitorear_drift(train_df: pd.DataFrame, nuevo_df: pd.DataFrame) -> pd.DataFrame:
    """Calcula PSI por variable para monitoreo mensual."""
    rows: List[Dict[str, float]] = []
    for col in FEATURE_COLUMNS:
        psi = population_stability_index(train_df[col], nuevo_df[col], bins=10)
        rows.append({"variable": col, "psi": psi})
    drift_df = pd.DataFrame(rows).sort_values("psi", ascending=False).reset_index(drop=True)
    return drift_df


def decidir_retraining(
    baseline_metrics: Dict[str, float],
    current_metrics: Dict[str, float],
    drift_df: pd.DataFrame,
    fecha_ultimo_entrenamiento: str,
    fecha_actual: str,
    umbral_psi_promedio: float = 0.2,
    umbral_psi_variable: float = 0.25,
    umbral_caida_roc_auc: float = 0.05,
    umbral_subida_mae: float = 0.15,
) -> Dict[str, object]:
    """Evalúa condiciones de reentrenamiento con reglas auditables."""
    reasons = []

    dt_last = datetime.strptime(fecha_ultimo_entrenamiento, "%Y-%m-%d")
    dt_current = datetime.strptime(fecha_actual, "%Y-%m-%d")
    days = (dt_current - dt_last).days
    if days >= 90:
        reasons.append(f"retraining_programado_{days}_dias")

    psi_promedio = float(drift_df["psi"].mean())
    psi_max = float(drift_df["psi"].max())
    if psi_promedio > umbral_psi_promedio:
        reasons.append(f"drift_promedio_alto_{psi_promedio:.3f}")
    if psi_max > umbral_psi_variable:
        reasons.append(f"drift_variable_alto_{psi_max:.3f}")

    caida_auc = baseline_metrics["roc_auc"] - current_metrics["roc_auc"]
    if caida_auc > umbral_caida_roc_auc:
        reasons.append(f"caida_roc_auc_{caida_auc:.3f}")

    subida_mae = (current_metrics["mae"] - baseline_metrics["mae"]) / max(baseline_metrics["mae"], 1e-6)
    if subida_mae > umbral_subida_mae:
        reasons.append(f"subida_mae_relativa_{subida_mae:.3f}")

    return {
        "reentrenar": len(reasons) > 0,
        "motivos": reasons,
        "dias_desde_ultimo_train": days,
        "psi_promedio": psi_promedio,
        "psi_max": psi_max,
    }

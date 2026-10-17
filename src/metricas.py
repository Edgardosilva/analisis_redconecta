"""Métricas y pruebas estadísticas reutilizables (NumPy, SciPy y Joblib)."""
import numpy as np
import pandas as pd
from joblib import Parallel, delayed
from scipy import stats

from carga import NUMERICAS


def resumen_grupos(df: pd.DataFrame, claves: list) -> pd.DataFrame:
    """Indicadores operacionales por grupo (pandas)."""
    return (
        df.groupby(claves)
        .agg(
            registros=("fecha_registro", "count"),
            trafico_prom_gb=("trafico_datos_gb", "mean"),
            latencia_prom_ms=("latencia_ms", "mean"),
            incidencias_total=("incidencias_reportadas", "sum"),
            tickets_total=("tickets_soporte", "sum"),
            tiempo_resolucion_prom_hr=("tiempo_resolucion_hr", "mean"),
            clientes_afectados_total=("clientes_afectados", "sum"),
            pct_sla_cumple=("sla_cumple", lambda s: 100 * s.mean()),
        )
        .round(2)
        .reset_index()
    )


def matriz_correlacion(df: pd.DataFrame, columnas=NUMERICAS + ["sla_cumple"]) -> pd.DataFrame:
    """Correlación de Pearson calculada con NumPy."""
    r = np.corrcoef(df[columnas].to_numpy(dtype=float), rowvar=False)
    return pd.DataFrame(r, index=columnas, columns=columnas).round(3)


def comparar_grupos(df: pd.DataFrame, factor: str,
                    variables=("latencia_ms", "tiempo_resolucion_hr", "tickets_soporte", "clientes_afectados")) -> pd.DataFrame:
    """Kruskal-Wallis (SciPy): ¿difiere cada variable entre las categorías del factor?"""
    filas = []
    for v in variables:
        h, p = stats.kruskal(*[g[v].to_numpy() for _, g in df.groupby(factor)])
        filas.append({"factor": factor, "variable": v, "H": round(float(h), 3), "p_valor": round(float(p), 3)})
    return pd.DataFrame(filas)


def independencia_sla(df: pd.DataFrame, factor: str) -> dict:
    """Chi-cuadrado (SciPy): ¿el cumplimiento de SLA depende del factor?"""
    chi2, p, _, _ = stats.chi2_contingency(pd.crosstab(df[factor], df["cumplimiento_sla"]))
    return {"factor": factor, "chi2": round(float(chi2), 3), "p_valor": round(float(p), 3)}


def _ic_bootstrap(valores: np.ndarray, n_boot: int, semilla: int) -> tuple:
    rng = np.random.default_rng(semilla)
    medias = rng.choice(valores, size=(n_boot, len(valores)), replace=True).mean(axis=1)
    inf, sup = np.percentile(medias, [2.5, 97.5]) * 100
    return round(float(inf), 1), round(float(sup), 1)


def ic_sla_bootstrap(df: pd.DataFrame, claves: list, n_boot: int = 2000,
                     semilla: int = 42, n_jobs: int = -1) -> pd.DataFrame:
    """IC 95 % bootstrap del % de SLA por grupo; un grupo por tarea paralela (Joblib)."""
    grupos = list(df.groupby(claves))
    intervalos = Parallel(n_jobs=n_jobs)(
        delayed(_ic_bootstrap)(g["sla_cumple"].to_numpy(), n_boot, semilla) for _, g in grupos
    )
    filas = [dict(zip(claves, clave), ic95_sla_inf=inf, ic95_sla_sup=sup)
             for (clave, _), (inf, sup) in zip(grupos, intervalos)]
    return pd.DataFrame(filas)

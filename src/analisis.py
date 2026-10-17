"""Análisis exploratorio de RedConecta Telecom S. A.

Uso: python src/analisis.py
Genera en output/: soporte_tecnico.csv, experiencia_clientes.csv,
                   resumen_region_servicio.csv, correlaciones.csv, dashboard.html
"""
from pathlib import Path

import pandas as pd

from carga import cargar_datos
from metricas import (comparar_grupos, ic_sla_bootstrap, independencia_sla,
                      matriz_correlacion, resumen_grupos)
from visualizacion import guardar_dashboard

RAIZ = Path(__file__).resolve().parents[1]
ENTRADA = RAIZ / "data" / "raw" / "dataset_set_D_telecomunicaciones.xlsx"
SALIDA = RAIZ / "output"
CSV = {"index": False, "encoding": "utf-8-sig"}


def exportar_areas(df: pd.DataFrame) -> None:
    df[["fecha_registro", "region", "tipo_servicio", "incidencias_reportadas",
        "tickets_soporte", "tiempo_resolucion_hr"]].sort_values("fecha_registro").to_csv(
        SALIDA / "soporte_tecnico.csv", **CSV)
    df[["fecha_registro", "tipo_servicio", "clientes_afectados", "latencia_ms",
        "cumplimiento_sla"]].sort_values("fecha_registro").to_csv(
        SALIDA / "experiencia_clientes.csv", **CSV)


def main() -> None:
    SALIDA.mkdir(exist_ok=True)
    df = cargar_datos(ENTRADA)

    claves = ["region", "tipo_servicio"]
    res = resumen_grupos(df, claves).merge(ic_sla_bootstrap(df, claves), on=claves)
    res.to_csv(SALIDA / "resumen_region_servicio.csv", **CSV)
    corr = matriz_correlacion(df)
    corr.to_csv(SALIDA / "correlaciones.csv", encoding="utf-8-sig")

    exportar_areas(df)
    guardar_dashboard(df, res, corr, SALIDA / "dashboard.html")

    pruebas = pd.concat([comparar_grupos(df, "region"), comparar_grupos(df, "tipo_servicio")])
    sla = pd.DataFrame([independencia_sla(df, "region"), independencia_sla(df, "tipo_servicio")])
    print("\nResumen región x servicio:\n", res.to_string(index=False))
    print("\nCorrelaciones:\n", corr)
    print("\nPruebas Kruskal-Wallis:\n", pruebas.to_string(index=False))
    print("\nChi-cuadrado SLA vs factor:\n", sla.to_string(index=False))
    print("\nSalidas generadas en", SALIDA)


if __name__ == "__main__":
    main()

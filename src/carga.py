"""Carga y preparación básica de los datos (pandas)."""
from pathlib import Path

import pandas as pd

NUMERICAS = [
    "trafico_datos_gb", "latencia_ms", "incidencias_reportadas",
    "tickets_soporte", "tiempo_resolucion_hr", "clientes_afectados",
]


def cargar_datos(ruta: Path) -> pd.DataFrame:
    """Lee el Excel, convierte la fecha y crea la variable binaria sla_cumple."""
    df = pd.read_excel(ruta)
    df["fecha_registro"] = pd.to_datetime(df["fecha_registro"])
    df["sla_cumple"] = (df["cumplimiento_sla"] == "Cumple").astype(int)
    return df

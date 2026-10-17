"""Construcción del dashboard exploratorio (HTML interactivo con Plotly)."""
from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots


def _tarjetas(df: pd.DataFrame) -> str:
    kpis = [
        ("Latencia prom. (ms)", f"{df.latencia_ms.mean():.1f}"),
        ("Resolución prom. (hr)", f"{df.tiempo_resolucion_hr.mean():.1f}"),
        ("Tickets totales", f"{df.tickets_soporte.sum():,}"),
        ("Incidencias totales", f"{df.incidencias_reportadas.sum():,}"),
        ("Cumplimiento SLA", f"{100 * df.sla_cumple.mean():.1f}%"),
    ]
    return "".join(f'<div class="k"><span>{n}</span><b>{v}</b></div>' for n, v in kpis)


def _barras(df: pd.DataFrame, eje: str, nombre: str) -> go.Figure:
    t = df.groupby(eje).agg(latencia=("latencia_ms", "mean"), resolucion=("tiempo_resolucion_hr", "mean"),
                            tickets=("tickets_soporte", "mean")).reset_index()
    f = make_subplots(rows=1, cols=3, subplot_titles=("Latencia prom. (ms)", "Resolución prom. (hr)", "Tickets prom."))
    for i, col in enumerate(["latencia", "resolucion", "tickets"], start=1):
        f.add_trace(go.Bar(x=t[eje], y=t[col].round(2), showlegend=False, text=t[col].round(1),
                           textposition="outside"), row=1, col=i)
    f.update_layout(title=f"Desempeño por {nombre}", height=380)
    return f


def _figuras(df: pd.DataFrame, res: pd.DataFrame, corr: pd.DataFrame) -> list:
    figs = [_barras(df, "region", "región"), _barras(df, "tipo_servicio", "tipo de servicio")]

    for col, titulo, escala in (("latencia_prom_ms", "Latencia promedio (ms)", "RdYlGn_r"),
                                ("tiempo_resolucion_prom_hr", "Tiempo de resolución promedio (hr)", "RdYlGn_r"),
                                ("pct_sla_cumple", "% cumplimiento SLA", "RdYlGn")):
        pv = res.pivot(index="region", columns="tipo_servicio", values=col)
        figs.append(px.imshow(pv, text_auto=".1f", aspect="auto", title=titulo, color_continuous_scale=escala))

    # Los intervalos se traslapan: las diferencias de SLA entre grupos no son concluyentes.
    g = res.assign(grupo=res["region"] + " - " + res["tipo_servicio"])
    fig_ic = go.Figure(go.Scatter(
        x=g["pct_sla_cumple"], y=g["grupo"], mode="markers",
        error_x=dict(type="data", symmetric=False, array=g["ic95_sla_sup"] - g["pct_sla_cumple"],
                     arrayminus=g["pct_sla_cumple"] - g["ic95_sla_inf"])))
    fig_ic.update_layout(title="% SLA por grupo con IC 95 % (bootstrap)", height=450)
    figs.append(fig_ic)

    sla = df.groupby(["region", "tipo_servicio", "cumplimiento_sla"]).size().reset_index(name="n")
    figs.append(px.bar(sla, x="tipo_servicio", y="n", color="cumplimiento_sla", facet_col="region",
                       barmode="stack", title="Cumplimiento de SLA por servicio y región"))
    figs.append(px.scatter(df, x="trafico_datos_gb", y="latencia_ms", color="tipo_servicio",
                           symbol="cumplimiento_sla", title="Tráfico vs latencia"))
    figs.append(px.scatter(df, x="incidencias_reportadas", y="tickets_soporte", color="region",
                           title="Incidencias vs tickets de soporte"))
    figs.append(px.box(df, x="tipo_servicio", y="latencia_ms", color="cumplimiento_sla",
                       title="Latencia según cumplimiento SLA"))
    figs.append(px.imshow(corr, text_auto=".2f", zmin=-1, zmax=1, color_continuous_scale="RdBu_r",
                          title="Matriz de correlación"))
    return figs


def guardar_dashboard(df: pd.DataFrame, res: pd.DataFrame, corr: pd.DataFrame, ruta: Path) -> None:
    cuerpo = "".join(f.to_html(full_html=False, include_plotlyjs="cdn" if i == 0 else False)
                     for i, f in enumerate(_figuras(df, res, corr)))
    html = f"""<!DOCTYPE html><html lang="es"><head><meta charset="utf-8">
<title>Dashboard RedConecta Telecom</title>
<style>body{{font-family:Segoe UI,Arial;margin:20px;background:#f5f6fa}}
h1{{color:#1f3a5f}}.kp{{display:flex;gap:12px;flex-wrap:wrap}}
.k{{background:#fff;padding:14px 20px;border-radius:8px;box-shadow:0 1px 4px #0002}}
.k span{{display:block;font-size:12px;color:#666}}.k b{{font-size:24px;color:#1f3a5f}}
</style></head><body><h1>RedConecta Telecom - Dashboard exploratorio de calidad de servicio</h1>
<div class="kp">{_tarjetas(df)}</div>{cuerpo}</body></html>"""
    Path(ruta).write_text(html, encoding="utf-8")

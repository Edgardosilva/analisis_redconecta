# RedConecta Telecom S. A. - Análisis de calidad del servicio

Proyecto de ciencia de datos que analiza la información operacional de RedConecta Telecom S. A. (telefonía móvil, internet hogar y soluciones corporativas) para apoyar decisiones de mejora de la calidad del servicio.

## Contexto
La Ing. Valentina Morales Araya detectó desempeños dispares: aumentos puntuales de latencia, tiempos de resolución distintos y variaciones en los clientes afectados según región y servicio. La gerencia requiere evidencia analítica reproducible para evaluar el soporte, priorizar mejoras y optimizar recursos.

## Objetivos
**General:** generar evidencia analítica reproducible sobre el desempeño del servicio para respaldar decisiones en Soporte Técnico y Experiencia de Clientes.

**Específicos**
- Comparar el desempeño operacional por región y tipo de servicio.
- Medir la carga del soporte y la eficiencia de resolución.
- Evaluar el impacto del desempeño técnico en clientes (afectados, latencia, SLA).
- Entregar archivos de salida específicos para cada área y un dashboard exploratorio.

**Preguntas de investigación**
1. ¿Qué región y servicio presentan mayor latencia y mayor tiempo de resolución?
2. ¿El volumen de tráfico se asocia a mayor latencia?
3. ¿Las incidencias aumentan la carga de tickets y los tiempos de resolución?
4. ¿Cómo varía el cumplimiento de SLA por región y servicio, y se relaciona con la latencia?

## Descripción de los datos
Archivo: `data/raw/dataset_set_D_telecomunicaciones.xlsx` (una hoja, 200 registros, 10 variables). Cubre desde 2025-03-01 hasta 2025-09-16, con un registro por día.

| Variable | Tipo | Descripción |
|---|---|---|
| `fecha_registro` | fecha | Fecha del registro |
| `region` | texto | Centro, Norte o Sur |
| `tipo_servicio` | texto | Empresas, Internet Hogar o Móvil |
| `trafico_datos_gb` | numérica | Volumen de tráfico de datos, en GB |
| `latencia_ms` | numérica | Latencia, en milisegundos |
| `incidencias_reportadas` | entera | Cantidad de incidencias |
| `tickets_soporte` | entera | Tickets de soporte atendidos |
| `tiempo_resolucion_hr` | numérica | Tiempo de resolución, en horas |
| `clientes_afectados` | entera | Clientes afectados |
| `cumplimiento_sla` | texto | "Cumple" o "No cumple" |

**SLA (Service Level Agreement):** compromiso de nivel de servicio con el cliente. El dataset no indica el umbral que define el cumplimiento.

## Metodología
El flujo se orquesta en `src/analisis.py`, que usa funciones reutilizables de tres módulos:

| Módulo | Funciones | Librerías |
|---|---|---|
| `src/carga.py` | `cargar_datos` | pandas |
| `src/metricas.py` | `resumen_grupos`, `matriz_correlacion`, `comparar_grupos`, `independencia_sla`, `ic_sla_bootstrap` | NumPy, SciPy, Joblib |
| `src/visualizacion.py` | `guardar_dashboard` | Plotly |

Etapas:
1. **Carga** (`cargar_datos`): lee el Excel, convierte la fecha y crea `sla_cumple` (1 = cumple, 0 = no cumple).
2. **Procesamiento** (`resumen_grupos`): agrupa por región y servicio y calcula latencia, tráfico, incidencias, tickets, resolución, clientes afectados y % de SLA.
3. **Análisis:**
   - NumPy: matriz de correlación de Pearson (`matriz_correlacion`).
   - SciPy: Kruskal-Wallis (`comparar_grupos`) y chi-cuadrado (`independencia_sla`) para contrastar si las diferencias entre grupos son significativas.
   - Joblib: intervalo de confianza 95 % bootstrap del % de SLA, con un grupo por tarea en paralelo (`ic_sla_bootstrap`).
4. **Visualización y salidas** (`exportar_areas`, `guardar_dashboard`): archivos para cada área y dashboard interactivo con Plotly.

## Principales resultados
- **SLA:** cumplimiento global de 48 %. Sur es la mejor región (55,2 %) frente a Centro (44,1 %) y Norte (44,6 %). Por servicio las diferencias son pequeñas (46,8 % a 49,1 %). La combinación más débil es Centro-Internet Hogar (37,0 %) y la mejor Sur-Internet Hogar (63,6 %).
- **Latencia:** promedio de 64,9 ms. Más alta en Norte-Móvil, Centro-Empresas y Sur-Empresas (cerca de 69,4 ms) y más baja en Sur-Móvil (53,5 ms).
- **Soporte:** Centro-Internet Hogar concentra la mayor carga de tickets (989). Sur-Internet Hogar tiene el mayor tiempo de resolución (30,6 hr) y Centro-Empresas el segundo (27,9 hr).
- **Relaciones entre variables:** todas las correlaciones son débiles (|r| < 0,25); la mayor es tráfico vs. tiempo de resolución (-0,21). El tráfico no explica la latencia. La latencia media es mayor en los registros que cumplen SLA (68,0 ms) que en los que no (62,0 ms), por lo que el SLA parece depender de otros factores o de su definición.

**Cómo apoyan las decisiones**
- Priorizar recursos técnicos en Centro-Internet Hogar (alto volumen de tickets y SLA más bajo).
- Revisar los procesos de resolución en Sur-Internet Hogar y Centro-Empresas.
- Identificar y replicar prácticas de la región Sur.
- Revisar cómo se define y mide el SLA.

## Archivos de salida (`output/`)
| Archivo | Contenido |
|---|---|
| `dashboard.html` | Dashboard interactivo: indicadores, comparación por región y servicio, mapas de calor, SLA, relaciones entre variables |
| `soporte_tecnico.csv` | **Soporte Técnico:** fecha_registro, region, tipo_servicio, incidencias_reportadas, tickets_soporte, tiempo_resolucion_hr |
| `experiencia_clientes.csv` | **Experiencia de Clientes:** fecha_registro, tipo_servicio, clientes_afectados, latencia_ms, cumplimiento_sla |
| `resumen_region_servicio.csv` | Indicadores por combinación de región y servicio, con IC 95 % del % de SLA |
| `correlaciones.csv` | Matriz de correlación entre variables numéricas y SLA |

## Estructura del repositorio
```
├── data/raw/            Dataset original, sin modificar
├── src/
│   ├── analisis.py      Script principal (orquesta el flujo)
│   ├── carga.py         Carga de datos
│   ├── metricas.py      Estadística reutilizable (NumPy, SciPy, Joblib)
│   └── visualizacion.py Dashboard
├── output/              Resultados generados
├── notebooks/           Notebook exploratorio (registro del desarrollo)
├── README.md            Documentación
├── requirements.txt     Dependencias
└── .gitignore
```

## Cómo reproducir el análisis
Requisitos: Python 3.10 o superior.

```bash
# 1. Descargar o clonar el repositorio y abrir una terminal en su carpeta raíz

# 2. (Opcional) crear un entorno virtual
python -m venv .venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate   # Linux/macOS

# 3. Instalar dependencias (pandas, openpyxl, plotly, numpy, scipy, joblib)
pip install -r requirements.txt

# 4. Ejecutar el análisis
python src/analisis.py
```
El script imprime un resumen en consola y regenera todos los archivos de `output/`. Abrir `output/dashboard.html` en el navegador para ver el dashboard.

## Actualización con nuevos registros
1. Agregar las filas nuevas al archivo de `data/raw/` manteniendo las 10 columnas, sus nombres y categorías.
2. Ejecutar `python src/analisis.py`.
3. Registrar el cambio en Git (`git add .` y `git commit`).

## Limitaciones
- Son 200 registros. Las pruebas de Kruskal-Wallis y chi-cuadrado no detectan diferencias significativas entre regiones ni servicios (p > 0,10) y los intervalos de confianza del SLA se traslapan: las diferencias observadas son orientativas.
- Se desconoce el umbral que define el cumplimiento del SLA.
- Las correlaciones son débiles, por lo que las variables disponibles no explican por sí solas la calidad del servicio. Conviene incorporar variables como hora, tipo de falla y capacidad de red.

import pandas as pd
import geopandas as gpd
from bokeh.io import curdoc
from bokeh.plotting import figure
from bokeh.models import GeoJSONDataSource, LinearColorMapper, ColorBar, HoverTool, Slider, Div
from bokeh.layouts import column, row, gridplot
from bokeh.palettes import Viridis256
import json

# Cargar los datos de COVID-19 desde el archivo JSON
with open('daily.json', 'r') as f:
    data = json.load(f)

# Convertir los datos a un DataFrame de pandas
df_covid = pd.DataFrame(data)

# Convertir la columna 'date' a tipo datetime para facilitar la manipulación
df_covid['date'] = pd.to_datetime(df_covid['date'], format='%Y%m%d')

# Cargar los datos geográficos de los estados de EE.UU.
states = gpd.read_file('https://raw.githubusercontent.com/python-visualization/folium/master/examples/data/us-states.json')
states['state'] = states['id']

# Obtener las fechas únicas en el dataset y ordenarlas
dates = sorted(df_covid['date'].unique())

# Crear GeoJSONDataSource inicial
def create_geosource(date):
    df_covid_date = df_covid[df_covid['date'] == date]
    merged = states.merge(df_covid_date, on='state', how='left')
    merged['date'] = merged['date'].astype(str)
    return GeoJSONDataSource(geojson=merged.to_json())

# Crear el mapa inicial para cada métrica
def create_plot(column_name, title):
    geosource = create_geosource(dates[0])
    
    palette = Viridis256[::-1]  # Invertir la paleta para que colores más oscuros representen valores más altos
    color_mapper = LinearColorMapper(palette=palette, low=df_covid[column_name].min(), high=df_covid[column_name].max())

    p = figure(title=f'{title} en {dates[0].strftime("%Y-%m-%d")}',
               height=400, width=400,
               toolbar_location='below', tools="pan,wheel_zoom,box_zoom,reset")
    
    # Añadir leyendas a los ejes X e Y
    p.xaxis.axis_label = "Longitud"
    p.yaxis.axis_label = "Latitud"
    
    p.xgrid.grid_line_color = None
    p.ygrid.grid_line_color = None

    p.patches('xs', 'ys', source=geosource,
              fill_color={'field': column_name, 'transform': color_mapper},
              line_color='black', line_width=0.25, fill_alpha=1)

    color_bar = ColorBar(color_mapper=color_mapper, label_standoff=8, width=500, height=20,
                         border_line_color=None, location=(0, 0), orientation='horizontal')
    p.add_layout(color_bar, 'below')

    hover = HoverTool(tooltips=[('Estado', '@state'), (title, f'@{column_name}')])
    p.add_tools(hover)

    return p, geosource, color_mapper

# Función que actualiza el mapa según la fecha seleccionada
def update_plot(attr, old, new):
    date_to_plot = dates[new]
    
    for p, geosource, color_mapper, column_name in plots:
        df_covid_latest = df_covid[df_covid['date'] == date_to_plot]
        merged = states.merge(df_covid_latest, on='state', how='left')
        merged['date'] = merged['date'].astype(str)
        
        color_mapper.low = merged[column_name].min()
        color_mapper.high = merged[column_name].max()
        
        geosource.geojson = merged.to_json()
        p.title.text = f'{column_name.replace("_", " ").title()} en {date_to_plot.strftime("%Y-%m-%d")}'
    
    date_display.text = f"Fecha seleccionada: {date_to_plot.strftime('%Y-%m-%d')}"

# Crear gráficos y almacenar referencias para actualizar
plots = []

for col_name, title in [('death', 'Muertes por COVID-19'),
                        ('deathIncrease', 'Incremento de muertes por COVID-19'),
                        ('hospitalizedCurrently', 'Hospitalizaciones actuales por COVID-19'),
                        ('positive', 'Positivos')]:
    
    p, geosource, color_mapper = create_plot(col_name, title)
    plots.append((p, geosource, color_mapper, col_name))

# Crear un Slider para seleccionar la fecha
slider = Slider(title="Fecha", start=0, end=len(dates)-1, value=0, step=1)
slider.on_change('value', update_plot)

# Mostrar la fecha seleccionada en un Div
date_display = Div(text=f"Fecha seleccionada: {dates[0].strftime('%Y-%m-%d')}", width=300, height=30)

# Layout en una matriz de 2x2
grid = gridplot([[plots[0][0], plots[1][0]], [plots[2][0], plots[3][0]]])

layout = column(Div(text="<h1>COVID-19 Visualizaciones conjuntas</h1>"), slider, date_display, grid)

# Añadir al documento
curdoc().add_root(layout)
curdoc().title = "COVID-19 Visualizaciones"




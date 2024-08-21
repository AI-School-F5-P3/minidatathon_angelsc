import pandas as pd
import geopandas as gpd
from bokeh.io import output_file, show, curdoc
from bokeh.plotting import figure
from bokeh.models import GeoJSONDataSource, LinearColorMapper, ColorBar, HoverTool, Slider
from bokeh.layouts import column
from bokeh.palettes import Viridis256
import json
from bokeh.models.widgets import Div

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
date_strs = [date.strftime('%Y-%m-%d') for date in dates]

# Crear la función que actualiza el mapa según la fecha seleccionada
def update_plot(attr, old, new):
    date_to_plot = dates[new]
    df_covid_latest = df_covid[df_covid['date'] == date_to_plot]
    merged = states.merge(df_covid_latest, on='state', how='left')
    
    # Convertir columnas de fechas a cadenas antes de crear GeoJSONDataSource
    merged['date'] = merged['date'].astype(str)
    
    # Actualizar el rango de colores
    color_mapper.low = merged['death'].min()
    color_mapper.high = merged['death'].max()
    
    geosource.geojson = merged.to_json()
    p.title.text = f'Hospitalizaciones por Estado a fecha de {date_to_plot.strftime("%Y-%m-%d")}'
    date_display.text = f"Fecha seleccionada: {date_to_plot.strftime('%Y-%m-%d')}"

# Crear GeoJSONDataSource inicial
df_covid_initial = df_covid[df_covid['date'] == dates[0]]
merged = states.merge(df_covid_initial, on='state', how='left')

# Convertir columnas de fechas a cadenas antes de crear GeoJSONDataSource
merged['date'] = merged['date'].astype(str)

geosource = GeoJSONDataSource(geojson=merged.to_json())

# Crear el mapa inicial
palette = Viridis256[::-1]  # Invertir la paleta para que colores más oscuros representen valores más altos
color_mapper = LinearColorMapper(palette=palette, low=merged['hospitalizedCurrently'].min(), high=merged['hospitalizedCurrently'].max())

p = figure(title=f'Hospitalizaciones por Estado a fecha de {dates[0].strftime("%Y-%m-%d")}',
           height=600, width=950,
           toolbar_location='below', tools="pan,wheel_zoom,box_zoom,reset")
p.xgrid.grid_line_color = None
p.ygrid.grid_line_color = None

p.patches('xs', 'ys', source=geosource,
          fill_color={'field': 'hospitalizedCurrently', 'transform': color_mapper},
          line_color='black', line_width=0.25, fill_alpha=1)

# Añadir la barra de color
color_bar = ColorBar(color_mapper=color_mapper, label_standoff=8, width=500, height=20,
                     border_line_color=None, location=(0, 0), orientation='horizontal')
p.add_layout(color_bar, 'below')

# Configurar el hover tool
hover = HoverTool(tooltips=[('Estado', '@state'), ('Muertes', '@hospitalizedCurrently')])
p.add_tools(hover)

# Crear un Slider para seleccionar la fecha
slider = Slider(title="Fecha", start=0, end=len(dates)-1, value=0, step=1)
slider.on_change('value', update_plot)

# Mostrar la fecha seleccionada en un Div
date_display = Div(text=f"Fecha seleccionada: {dates[0].strftime('%Y-%m-%d')}", width=300, height=30)

# Disponer el layout
layout = column(p, slider, date_display)

# Mostrar el mapa
curdoc().add_root(layout)
output_file("covid_hospi_us_map.html")
show(layout)
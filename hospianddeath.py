import pandas as pd
import geopandas as gpd
from bokeh.io import output_file, show, curdoc
from bokeh.plotting import figure
from bokeh.models import GeoJSONDataSource, LinearColorMapper, ColorBar, HoverTool, Slider, Tabs, Panel
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

# Crear una función para generar cada mapa
def create_map(field, title):
    def update_plot(attr, old, new):
        date_to_plot = dates[new]
        df_covid_latest = df_covid[df_covid['date'] == date_to_plot]
        merged = states.merge(df_covid_latest, on='state', how='left')
        
        merged['date'] = merged['date'].astype(str)
        
        color_mapper.low = merged[field].min()
        color_mapper.high = merged[field].max()
        
        geosource.geojson = merged.to_json()
        p.title.text = f'{title} por Estado en {date_to_plot.strftime("%Y-%m-%d")}'
        date_display.text = f"Fecha seleccionada: {date_to_plot.strftime('%Y-%m-%d')}"

    df_covid_initial = df_covid[df_covid['date'] == dates[0]]
    merged = states.merge(df_covid_initial, on='state', how='left')
    merged['date'] = merged['date'].astype(str)
    
    geosource = GeoJSONDataSource(geojson=merged.to_json())
    
    palette = Viridis256[::-1]
    color_mapper = LinearColorMapper(palette=palette, low=merged[field].min(), high=merged[field].max())
    
    p = figure(title=f'{title} por Estado en {dates[0].strftime("%Y-%m-%d")}',
               height=600, width=950,
               toolbar_location='below', tools="pan,wheel_zoom,box_zoom,reset")
    p.xgrid.grid_line_color = None
    p.ygrid.grid_line_color = None
    
    p.patches('xs', 'ys', source=geosource,
              fill_color={'field': field, 'transform': color_mapper},
              line_color='black', line_width=0.25, fill_alpha=1)
    
    color_bar = ColorBar(color_mapper=color_mapper, label_standoff=8, width=500, height=20,
                         border_line_color=None, location=(0, 0), orientation='horizontal')
    p.add_layout(color_bar, 'below')
    
    hover = HoverTool(tooltips=[('Estado', '@state'), (title, f'@{field}')])
    p.add_tools(hover)
    
    slider = Slider(title="Fecha", start=0, end=len(dates)-1, value=0, step=1)
    slider.on_change('value', update_plot)
    
    date_display = Div(text=f"Fecha seleccionada: {dates[0].strftime('%Y-%m-%d')}", width=300, height=30)
    
    return column(p, slider, date_display)

# Crear los tres mapas
cases_layout = create_map('positive', 'Casos de COVID-19')
hospitalizations_layout = create_map('hospitalized', 'Hospitalizaciones por COVID-19')
deaths_layout = create_map('deathConfirmed', 'Muertes por COVID-19')

# Crear pestañas para cada mapa
tab1 = Panel(child=cases_layout, title="Casos")
tab2 = Panel(child=hospitalizations_layout, title="Hospitalizaciones")
tab3 = Panel(child=deaths_layout, title="Muertes")

tabs = Tabs(tabs=[tab1, tab2, tab3])

# Mostrar los mapas
curdoc().add_root(tabs)
output_file("covid_us_maps.html")
show(tabs)
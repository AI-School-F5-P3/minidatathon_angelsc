from bokeh.io import curdoc
from bokeh.models.widgets import Tabs, Panel
from death import layout as death_layout
from hospicurrent import layout as hospitalizations_layout
from casos import layout as casos_layout
from deathIncrease import layout as deathIncrease_layout

layouts = [
   
    Panel(child=death_layout, title="Muertes por COVID"),
    Panel(child=deathIncrease_layout, title="Incremento de muertes por COVID"),
    Panel(child=hospitalizations_layout, title="Hospitalizaciones"),
    Panel(child=casos_layout, title="Casos Positivos")
]
tabs = Tabs(tabs=layouts)
curdoc().add_root(tabs)
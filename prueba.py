from bokeh.plotting import figure, curdoc
from bokeh.layouts import column
from bokeh.models import Slider

p = figure(title="Simple plot")
p.line([1, 2, 3, 4, 5], [6, 7, 2, 4, 5])

slider = Slider(start=0, end=10, value=1, step=0.1, title="Slider")

layout = column(p, slider)
curdoc().add_root(layout)

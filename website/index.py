import js, json, plotly
from plotly.graph_objs import Figure
from clustering.plots import get_plot


def plot(figure: Figure):
    js.Plotly.newPlot(
        "plot", js.JSON.parse(json.dumps(figure, cls=plotly.utils.PlotlyJSONEncoder))
    )
    # remove children with class 'lds-ellipsis' from the loading div
    elements = js.document.getElementById("plot").getElementsByClassName("lds-ellipsis")
    for element in elements:
        element.parentNode.removeChild(element)


plot(get_plot())

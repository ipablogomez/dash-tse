from dash import html
import dash_bootstrap_components as dbc


def card(tittle,id,units,color):
    """
    This component plots large numbers with units
    :title to display
    :id of dash component
    :units of the metric
    :color of the number and units text
    """
    card = dbc.Card([
                dbc.CardBody([
                    html.H5(tittle,style={"height":"50px"}),
                    html.P(id=id,style={"font-size": "90px",'color':color,"font-weight": "600","height":"100px","margin-top": "-45px"}),
                    html.H4(units, className="card-text",style={'color':color}),
                    ])],
                style={"width": "23rem"},
        )
    return card


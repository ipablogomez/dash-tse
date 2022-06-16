from math import e
from dash import dcc, html, dash_table, Input, Output, callback, callback_context
import dash_bootstrap_components as dbc
layout =  dbc.Container(
                    dbc.Row(
                            html.Img(
                                    src='https://d1io3yog0oux5.cloudfront.net/_436d0947e0c817118f3420ef2c05c366/dgoc/db/493/3392/image_home.jpg',
                                    style = {'height':'auto'}
                                    )),
                fluid=True)
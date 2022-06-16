from dash import Dash, Input, Output, State, callback, callback_context
from dash.dependencies import ClientsideFunction
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from pages import district, route, site, landing
import urllib.parse as urlparse
import dash_auth
from users import USERNAME_PASSWORD_PAIRS
from utils.common_functions import assets
import datetime
import json

PLOTLY_LOGO = "assets\logo.png"
# the style arguments for the sidebar. We use position:fixed and a fixed width
SIDEBAR_STYLE = {
    "position": "fixed",
    "top": 60,
    "left": 0,
    "bottom": 0,
    "width": "9rem",
    "height": "100%",
    "z-index": 1,
    "overflow-x": "hidden",
    "transition": "all 0.5s",
    "padding": "0rem 0rem",
    "background-color": "#f8f9fa",
}

SIDEBAR_HIDEN = {
    "position": "fixed",
    "top": 60,
    "left": "-10rem",
    "bottom": 0,
    "width": "10rem",
    "height": "100%",
    "z-index": 1,
    "overflow-x": "hidden",
    "transition": "all 0.5s",
    "padding": "0rem 0rem",
    "background-color": "#f8f9fa",
}

# the styles for the main content position it to the right of the sidebar and
# add some padding.
CONTENT_STYLE = {
    "transition": "margin-left .5s",
    "margin-left": "9rem",
    "margin-right": "1rem",
    "padding": "0.5rem 0.5rem",
    "background-color": "#f8f9fa",
}

CONTENT_STYLE1 = {
    "transition": "margin-left .5s",
    "margin-left": "1rem",
    "margin-right": "1rem",
    "padding": "0.5rem 0.5rem",
    "background-color": "#f8f9fa",
}

app = Dash(external_stylesheets=[dbc.themes.BOOTSTRAP,
                                'https://use.fontawesome.com/releases/v5.8.1/css/all.css'])
auth = dash_auth.BasicAuth(
    app,
    USERNAME_PASSWORD_PAIRS
)

app.config.suppress_callback_exceptions = True
server = app.server

navbar = dbc.Navbar(
    [
        dbc.Container([
            html.A( 
                dbc.Row(
                    [
                        dbc.Col(html.Img(src=PLOTLY_LOGO, height="30px")),
                        dbc.Col(dbc.NavbarBrand("Diversified Energy", className="ms-2")),
                    ],
                    className="g-0",
                    justify= 'start'
                ),
                style={"textDecoration": "none"},
                id = "btn_sidebar"
            ),
            dbc.Row( dbc.Col(dbc.NavbarBrand("Tittle", className="ms-4",id='title',style={"font-size": "30px","font-weight": "600"}))),
            dbc.Row(
                dbc.Col(
                    dcc.DatePickerRange(
                    id='date-picker-range',
                    initial_visible_month= datetime.date.today() - datetime.timedelta(days=360),
                    start_date=datetime.date.today() - datetime.timedelta(days=360),
                    end_date=datetime.date.today() - datetime.timedelta(days=120)
                 )))
            
             ],fluid=True),
        
    ],
    color="dark",
    dark=True,
    sticky ="top"
)

modal = dbc.Modal(
            [
                #dbc.ModalHeader(dbc.ModalTitle("Header")),
                dbc.ModalHeader("", id = "modal-content"),
                dbc.ModalFooter(
                    dbc.NavLink("Go Site", id = "modal-link")
                ),
            ],
            id="modal",
            is_open=False,
        )

sidebar = html.Div(
    [
        
        dbc.Nav(
            [
                dbc.NavLink("Districts", href="/district", id="page-1-link"),
                dbc.NavLink("Routes", href="/route", id="page-2-link"),
                dbc.NavLink("Sites", href="/site", id="page-3-link"),
            ],
            vertical=True,
            pills=True,
        ),
    ],
    id="sidebar",
    style=SIDEBAR_HIDEN,
)

content = html.Div(

    id="page-content",
    style=CONTENT_STYLE1)

app.layout = html.Div([
    dcc.Store(id='sharing-data'),
    dcc.Store(id='side_click'),
    dcc.Store(id='asset_dict', data = assets().to_dict()),
    dcc.Location(id='url', refresh=False),
    navbar,
    modal,
    sidebar,
    content
])


@callback(
    [
        Output("sidebar", "style"),
        Output("page-content", "style"),
        Output("side_click", "data"),
    ],

    [Input("btn_sidebar", "n_clicks")],
    [
        State("side_click", "data"),
    ]
)
def toggle_sidebar(n, nclick):
    if n:
        if nclick == "SHOW":
            sidebar_style = SIDEBAR_HIDEN
            content_style = CONTENT_STYLE1
            cur_nclick = "HIDDEN"
        else:
            sidebar_style = SIDEBAR_STYLE
            content_style = CONTENT_STYLE
            cur_nclick = "SHOW"
    else:
        sidebar_style = SIDEBAR_STYLE
        content_style = CONTENT_STYLE
        cur_nclick = "SHOW"

    return sidebar_style, content_style, cur_nclick


@callback(Output('page-content', 'children'),
          Output('title','children'),
          Input('url', 'href'))
def display_page(url):
    parsed = urlparse.urlparse(url)
    pathname = parsed.path
    if pathname == '/site':
        return site.layout,'Site Overview'
    elif pathname == '/route':
        return route.layout,'Route Overview'
    elif pathname == '/district':
        return district.layout, 'District Overview'
    else:
        return landing.layout, 'Production Forecast'


app.clientside_callback(
    ClientsideFunction(
        namespace='clientside',
        function_name='large_params_function'
    ),
    Output('selected-data','children'),Input('sharing-data','data'))

if __name__ == '__main__':
    app.run_server(debug=True)
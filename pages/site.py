from dash import dcc, html, Input, Output, State, callback, callback_context
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import urllib.parse as urlparse
from pandas import DataFrame
import numpy as np
from utils.common_functions import metrics, rolling_calc
from components import templates, charts


filters  = dbc.Row([
    # District Filter
    dbc.Col(html.Div(children= "District", style={'textAlign': 'center',}),width="auto",align="center"),
    dbc.Col(html.Div(dcc.Dropdown(id="district",)),lg=3,width=12),
    # Route Filter
    dbc.Col(html.Div(children= "Route", style={'textAlign': 'center',}),width="auto",align="center"),
    dbc.Col(html.Div(dcc.Dropdown(id="routes")),lg=3,width=12),
    # Site Filter
    dbc.Col(html.Div(children= "FDC Site", style={'textAlign': 'center',}),width="auto",align="center"),
    dbc.Col(html.Div(dcc.Dropdown(id="fdc_sites")),lg=3,width=12),
])


cards = dbc.Row([
        dbc.Col(templates.card("Average Volume Rate", 's_card1', 'MCF', 'rgb(4, 132, 108)','24rem'),width="auto"),
        dbc.Col(templates.card("Total Volume", "s_card2", 'MCF', 'rgb(4, 132, 108)','27rem'),width="auto"),
        dbc.Col(templates.card("Total Predicted Volume","s_card3", 'MCF','rgb(227, 123, 4)','27rem'),width="auto"),
        dbc.Col(templates.card("Anomaly Count","s_card4", '#', 'rgb(227, 123, 4)','20rem'),width="auto"),
       
])

layout = dbc.Container([
   
    dbc.Row(dbc.Col(filters), align="center"),
    dbc.Row(dbc.Col(cards), align="center",style={"padding-top":"15px"}),

    dbc.Row(dcc.Graph(id='volume_prediction',style={"height":"350px","padding-top":"15px"})),

    dbc.Row(dcc.Graph(id='volume_variance_percentage',style={"height":"250px","padding-top":"15px"})),
    ],
fluid=True,
)

@callback(Output('district','options'),
          Output('district','value'),
          Input('url', 'href'),
          Input('asset_dict','data'))
def load_district_dropdown(url,asset_dict):
    asset_df = DataFrame.from_dict(asset_dict)
    options = [{"label": str(i), "value": str(i), "title": str(i)} for i in asset_df.district.drop_duplicates().sort_values().dropna()],
    value =  asset_df.district.drop_duplicates().sort_values().dropna().iloc[0]
    parsed = urlparse.urlparse(url)
    parameters = urlparse.parse_qs(parsed.query)
    if 'district' in parameters:
        value = parameters['district'][0]
    return options[0], value

@callback(
    Output('routes', 'options'),
    Output('routes', 'value'),
    Input('url', 'href'),
    Input('district', 'value'),
    Input('asset_dict','data'))
def set_routes_options(url,selected_district,asset_dict):
    asset_df = DataFrame.from_dict(asset_dict)
    value = ''
    options = []
    if selected_district:
        routes = asset_df.loc[asset_df['district'] == selected_district, 'route_name'].unique()
        options = [{"label": str(i), "value": str(i), "title": str(i) } for i in routes]
        value = routes[0]

    # URL Tratement 
    parsed = urlparse.urlparse(url)
    parameters = urlparse.parse_qs(parsed.query)
    district_url = ''
    if 'district' in parameters:
        district_url = parameters['district'][0]

    if 'route' in parameters and selected_district == district_url:
        value = parameters['route'][0]
    
    return options, value

@callback(
    Output('fdc_sites', 'options'),
    Output('fdc_sites', 'value'),
    Input('url', 'href'),
    Input('routes', 'value'),
    Input('asset_dict','data'))
def set_fdc_sites_options(url,selected_route,asset_dict):
    asset_df = DataFrame.from_dict(asset_dict)
    value = ''
    options = []
    if selected_route:
        sites = asset_df.loc[asset_df['route_name'] == selected_route, 'fdcsite_name'].unique()
        options = [{"label": str(i), "value": str(i), "title": str(i) } for i in sites]
        value = sites[0]

    # URL Tratement 
    parsed = urlparse.urlparse(url)
    parameters = urlparse.parse_qs(parsed.query) 
    route_url = ''
    if 'route' in parameters:
        route_url = parameters['district'][0]
    if 'site' in parameters and selected_route == route_url:
        value = parameters['site'][0]
    
    return options, value

@callback(
    Output('volume_prediction','figure'),
    Output('volume_variance_percentage','figure'),
    Output('s_card1','children'),
    Output('s_card2','children'),
    Output('s_card3','children'),
    Output('s_card4','children'),
    State('district', 'value'),
    State('routes', 'value'),
    Input('fdc_sites', 'value'),
    Input('date-picker-range','start_date'),
    Input('date-picker-range','end_date'),
    Input('asset_dict','data')
)
def site_calculations(district,route,site,start_date,end_date,asset_dict):
    # Read asset data
    asset_df = DataFrame.from_dict(asset_dict)
    # Read data
    data = metrics(district,start_date,end_date)
    #data['time'] = pd.to_datetime(data['time']).dt.floor('d')

    #Filter data by route 
    site_data = data[(data.route_name == route) & (data.fdcsite_name == site)]
    # Average Metric
    average_metric_rate = round(site_data.metric.mean(),1)
    # Total Metric Sum
    sum_metric = round(site_data.metric.sum(),0)
    # Total Metric Predicted Sum 
    sum_predicted_metric = round(site_data.predicted_metric.sum(),0)
    # Anomaly Count
    anomaly_count = site_data.anomaly.loc[site_data.anomaly == True].sum()
    # Get anomaly Points 
    site_data['anomaly_point'] = site_data['metric'] * site_data['anomaly']
    site_data.loc[site_data['anomaly_point'] == 0, 'anomaly_point'] = np.nan 
   
    
    # Rolling Calc
    df_variance_by_site = rolling_calc(site_data,'fdcsite_name','metric')
    df_predicted_variance_by_site = rolling_calc(site_data,'fdcsite_name','predicted_metric')
    df_variance_by_site['five_percent'] = 5
    df_variance_by_site['minus_five_percent'] = -5
    
    fig = charts.volume_prediction_chart(site_data)

    fig2 = charts.single_rolling_calc_chart(df_variance_by_site,df_predicted_variance_by_site)   

    return fig, fig2,\
            average_metric_rate,\
            sum_metric,\
            sum_predicted_metric,\
            anomaly_count
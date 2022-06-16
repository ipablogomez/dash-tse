from dash import dcc, html, dash_table, Input, Output, State, callback, callback_context
import dash_bootstrap_components as dbc
import pandas as pd
import urllib.parse as urlparse
from urllib.parse import urlencode
from utils.common_functions import metrics, data_bars, rolling_calc
from components import templates, charts
from pandas import DataFrame
import re

filters  = dbc.Row([
    # District Filter
    dbc.Col(html.Div(children= "District", style={'textAlign': 'center',}),width="auto",align="center"),
    dbc.Col(html.Div(dcc.Dropdown(id = "r_district")),lg=5,width=12),
    # Route Filter
    dbc.Col(html.Div(children= "Route", style={'textAlign': 'center',}),width="auto",align="center"),
    dbc.Col(html.Div(dcc.Dropdown(id="r_routes",multi=True,),style={'height':'30px'}),lg=5,width=12)
    
])

cards = dbc.Row([
        dbc.Col(templates.card("Average Volume Rate", 'r_card1', 'MCF', 'rgb(4, 132, 108)','24rem'),width="auto"),
        dbc.Col(templates.card("Total Volume", "r_card2", 'MCF', 'rgb(4, 132, 108)','27rem'),width="auto"),
        dbc.Col(templates.card("Total Predicted Volume","r_card3", 'MCF','rgb(227, 123, 4)','27rem'),width="auto"),
        dbc.Col(templates.card("Anomaly Count","r_card4", '#', 'rgb(227, 123, 4)','20rem'),width="auto"),
       
])

layout = dbc.Container([
 
    dbc.Row(dbc.Col(filters), align="center"),

    dbc.Row(dbc.Col(cards), align="center",style={"padding-top":"15px"}),
            
    dbc.Row(dcc.Graph(id='all_sites',style={"height":"500px","padding-top":"15px"})),

    dbc.Row([
            dbc.Col(dcc.Graph(
                    id='anomalies_map',
                    style={"height":"400px","margin-top":"15px",
                    }),
            lg=6,width=12,align="center",   
            ),
            dbc.Col(dash_table.DataTable(
                    id="anomaly_count_table",
                    columns=[
                        {'name': 'FDC Site', 'id': 'name'},
                        {'name': 'Total Anomalies', 'id': 'value'}],
                    style_cell={
                        'width': '100px',
                        'minWidth': '100px',
                        'maxWidth': '100px',
                        'overflow': 'hidden',
                        'textOverflow': 'ellipsis',
                        },
                    fixed_rows={'headers': True},
                    style_table={'height': '400px', 'overflowY': 'auto',"border-style":"solid","border-width":'0.2px',"border-color":'rgb(229, 229, 229)'}),
                    lg=6,width=12,align="center",style={"margin-top": "15px","padding-right": "15px"}
                    ),
    ]),
    dbc.Row(dcc.Graph(id='r_volume_prediction',style={"height":"350px","padding-top":"15px"})),
    dbc.Row(dcc.Graph(id='variance_by_site',style={"height":"500px","padding-top":"15px"})),
    ],
fluid=True,
)

@callback(Output('r_district','options'),
          Output('r_district','value'),
          Input('asset_dict','data'),)
def load_district_dropdown(asset_dict):
    asset_df = DataFrame.from_dict(asset_dict)
    options = [{"label": str(i), "value": str(i), "title": str(i)} for i in asset_df.district.drop_duplicates().sort_values().dropna()],
    value =  asset_df.district.drop_duplicates().sort_values().dropna().iloc[0]
    return options[0], value

@callback(
    Output('r_routes', 'value'),
    Output('r_routes', 'options'),
    Input('r_district', 'value'),
    Input('asset_dict','data'))
def set_routes_options(selected_district,asset_dict):
    asset_df = DataFrame.from_dict(asset_dict)
    if selected_district:
        options = [{"label": str(i), "value": str(i), "title": str(i) } for i in asset_df.loc[asset_df['district'] == selected_district, 'route_name'].unique()]
        options = [{'label': 'Select all', 'value': 'all_values', "title":'All Values'}] + options
        return ['all_values'], options
    return "", []

"""@callback(
    Output('sharing-data','data'),
    Input('all_sites','clickData'),
    State('all_sites','figure'),
    prevent_initial_call=True,
    )
def display_selected_data(click_info,figure):
    pass
    triger_id = callback_context.triggered_id
    url = 'http://localhost:8050/site'
    if click_info is not None:
        info_dict = dict(click_info)
        curve_number  = info_dict['points'][0]['curveNumber']
        route_name = figure['data'][curve_number]['name']
        hover_data = figure['data'][curve_number]['hovertemplate']

        site_name = re.search('fdcsite_name=(.*)<br>time', hover_data)
        params = {'district':'ASHLAND', 'route':route_name, 'site':site_name.group(1)} 
        url_parts = list(urlparse.urlparse(url))
        query = dict(urlparse.parse_qsl(url_parts[4]))
        query.update(params)
        url_parts[4] = urlencode(query)

        return urlparse.urlunparse(url_parts)"""

@callback(
    Output("modal", "is_open"),
    Output("modal-link","href"),
    Output("modal-content","children"),
    [Input("all_sites", "clickData")],
    [State("modal", "is_open"),State('all_sites','figure'),State('asset_dict','data')],
)
def toggle_modal(n1,  is_open, figure,asset_dict):
    if n1 is not None:
        asset_df = DataFrame.from_dict(asset_dict)
        url = '/site'
        info_dict = dict(n1)
        curve_number  = info_dict['points'][0]['curveNumber']
        route_name = figure['data'][curve_number]['name']
        hover_data = figure['data'][curve_number]['hovertemplate']
        site_name = re.search('fdcsite_name=(.*)<br>time', hover_data)
        distric = asset_df[(asset_df.route_name == route_name) & (asset_df.fdcsite_name == site_name.group(1))].district
        
        params = {'district':distric.iloc[0], 'route':route_name, 'site':site_name.group(1)} 
        url_parts = list(urlparse.urlparse(url))
        query = dict(urlparse.parse_qsl(url_parts[4]))
        query.update(params)
        url_parts[4] = urlencode(query)

        return not is_open, urlparse.urlunparse(url_parts), site_name.group(1)
    return is_open, "", ""    

@callback(
    Output('anomaly_count_table','data'),
    Output('anomaly_count_table','style_data_conditional'),
    Output('anomalies_map','figure'),
    Output('r_volume_prediction','figure'),
    Output('all_sites','figure'),
    Output('variance_by_site','figure'),
    Output('r_card1','children'),
    Output('r_card2','children'),
    Output('r_card3','children'),
    Output('r_card4','children'),
    Input('r_district', 'value'),
    Input('r_routes', 'value'), 
    Input('r_routes', 'options'),      
    Input('date-picker-range','start_date'),
    Input('date-picker-range','end_date'),
    Input('asset_dict','data')
)

def route_calculations(district,route,route_options,start_date,end_date,asset_dict):
    
    # Read asset data
    asset_df = DataFrame.from_dict(asset_dict)
    # Read data
    data = metrics(district,start_date,end_date)
    #data['time'] = pd.to_datetime(data['time']).dt.floor('d')

    # Get Routes 
    routes = [i['value'] for i in route_options] if 'all_values' in route else route

    #Filter data by route 
    route_data = data.loc[data.route_name.isin(routes)]
    # Average Metric
    average_metric_rate = round(route_data.metric.mean(),1)
    # Total Metric Sum
    sum_metric = round(route_data.metric.sum(),0)
    # Total Metric Predicted Sum
    sum_predicted_metric = round(route_data.predicted_metric.sum(),0)
    # Anomaly Count
    anomaly_count = route_data.anomaly.loc[route_data.anomaly == True].sum()
    # Anomaly Table Data
    total_group_anomaly = route_data.groupby(['fdcsite_name'])['anomaly'].agg('sum').to_dict()
    total_anomaly_df = pd.DataFrame(list(total_group_anomaly.items()), columns = ['name','value'])
    # Anomaly Map
    df_anomalies_site = route_data.groupby(['fdcsite_name'],as_index = False)['anomaly'].agg('sum')
    df_anomalies_map = df_anomalies_site.merge(asset_df,on = 'fdcsite_name', how='left')
    # Sum
    df_sum_date_range = route_data.groupby(['time'],as_index = False)['metric','predicted_metric','lower_bound','upper_bound'].sum()
    # Variance
    df_variance_by_site = rolling_calc(route_data,'fdcsite_name','metric')

    fig = charts.anomalies_map(df_anomalies_map)

    fig2 = charts.volume_prediction_chart(df_sum_date_range)
    
    fig3= charts.daily_production_char(route_data,'area')

    fig4 = charts.multiple_rolling_calc_chart(df_variance_by_site,"fdcsite_name")  

    return total_anomaly_df.to_dict('records'),\
        data_bars(total_anomaly_df,'value'),\
        fig, fig2, fig3, fig4,\
        average_metric_rate,\
        sum_metric,\
        sum_predicted_metric,\
        anomaly_count
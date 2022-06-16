from dash import dcc, html, dash_table, Input, Output, callback, callback_context
import dash_bootstrap_components as dbc
import pandas as pd
from pandas import DataFrame
from utils.common_functions import metrics, data_bars, rolling_calc
from components import templates, charts

cards = dbc.Row([
        dbc.Col(templates.card("Average Volume Rate", 'd_card1', 'MCF', 'rgb(4, 132, 108)'),width="auto"),
        dbc.Col(templates.card("Total Volume", "d_card2", 'MCF', 'rgb(4, 132, 108)'),width="auto"),
        dbc.Col(templates.card("Total Predicted Volume","d_card3", 'MCF','rgb(227, 123, 4)'),width="auto"),
        dbc.Col(templates.card("Anomaly Count","d_card4", '#', 'rgb(227, 123, 4)'),width="auto"),
       
])

filters  = dbc.Row([
    # District Filter
    dbc.Col(html.Div(children= "District", style={'textAlign': 'center',}),width="auto",align="center"),
    dbc.Col(html.Div(dcc.Dropdown( id = "d_district")), width=2),
])


layout = dbc.Container([

    dbc.Row(dbc.Col(filters), align="center"),

    dbc.Row(dbc.Col(cards), align="center",style={"padding-top":"15px"}),
    dbc.Row(dcc.Graph(id='all_routes',style={"height":"500px","padding-top":"15px"})),

    dbc.Row([
            dbc.Col(dcc.Graph(
                    id='district_anomalies_map',
                    style={"height":"400px","margin-top":"15px",
                    }),
            lg=6,width=12,align="center",   
            ),
            dbc.Col(dash_table.DataTable(
                    id="route_anomaly_count_table",
                    columns=[
                        {'name': 'Routes', 'id': 'name'},
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
    dbc.Row(dcc.Graph(id='district_volume_prediction',style={"height":"350px","padding-top":"15px"})),
    dbc.Row(dcc.Graph(id='district_variance_by_route',style={"height":"500px","padding-top":"15px"}))

    ],
fluid=True,
)

@callback(Output('d_district','options'),
          Output('d_district','value'),
          Input('asset_dict','data'))
def load_district_dropdown(asset_dict):
    asset_df = DataFrame.from_dict(asset_dict)
    options = [{"label": str(i), "value": str(i), "title": str(i)} for i in asset_df.district.drop_duplicates().sort_values().dropna()],
    value =  asset_df.district.drop_duplicates().sort_values().dropna().iloc[0]
    return options[0], value

@callback(
    Output('route_anomaly_count_table','data'),
    Output('route_anomaly_count_table','style_data_conditional'),
    Output('district_anomalies_map','figure'),
    Output('district_volume_prediction','figure'),
    Output('all_routes','figure'),
    Output('district_variance_by_route','figure'),
    Output('d_card1','children'),
    Output('d_card2','children'),
    Output('d_card3','children'),
    Output('d_card4','children'),
    Input('d_district', 'value'),     
    Input('date-picker-range','start_date'),
    Input('date-picker-range','end_date'),
    Input('asset_dict','data')
)
def district_calculations(district,start_date,end_date,asset_dict):
    # Read asset data
    asset_df = DataFrame.from_dict(asset_dict)
    # Read data
    data = metrics(district,start_date, end_date)
    data['time'] = pd.to_datetime(data['time']).dt.floor('d')

    # Average Metric
    average_metric_rate = round(data.metric.mean(),1)
    # Total Metric Sum
    sum_metric = round(data.metric.sum(),0)
    # Total Metric Predicted Sum
    sum_predicted_metric = round(data.predicted_metric.sum(),0)
    # Anomaly Count
    anomaly_count = data.anomaly.loc[data.anomaly == True].sum()
    # Anomaly Table Data
    total_anomaly_route = data.groupby(['route_name'])['anomaly'].agg('sum').to_dict()
    total_anomaly_df = pd.DataFrame(list(total_anomaly_route.items()), columns = ['name','value'])  
    # Anomalies Map
    df_anomalies_site = data.groupby(['fdcsite_name'],as_index = False)['anomaly'].agg('sum')
    df_anomalies_map = df_anomalies_site.merge(asset_df,on = 'fdcsite_name', how='left')

    # Sum
    df_sum_date_range = data.groupby(['time'],as_index = False)['metric','predicted_metric','lower_bound','upper_bound'].sum()
    
    # Variace
    df_variance_by_route = rolling_calc(data,'route_name','metric')
    
    fig = charts.anomalies_map(df_anomalies_map)

    fig2 = charts.volume_prediction_chart(df_sum_date_range)
    
    fig3= charts.daily_production_char(data,'bar')

    fig4 = charts.multiple_rolling_calc_chart(df_variance_by_route,"route_name")  

    

    return  total_anomaly_df.to_dict('records'),\
        data_bars(total_anomaly_df,'value'),\
        fig, fig2, fig3, fig4,\
        average_metric_rate,\
        sum_metric,\
        sum_predicted_metric,\
        anomaly_count
import plotly.graph_objects as go
import plotly.express as px

def volume_prediction_chart(df):
    fig = go.Figure()
    fig.add_trace(go.Scatter(
            name="Upper Bound Volume",
            x=df.time, 
            y=df.upper_bound,
            fill=None,
            mode='lines',
            line=dict(width=0.5, color='rgb(166, 172, 175)')
                ))
    fig.add_trace(go.Scatter(
                name="Lower Bound Volume",
                x=df.time, 
                y=df.lower_bound,
                fill='tonexty', # fill area between trace0 and trace1
                mode='lines',
                line=dict(width=0.5, color='rgb(166, 172, 175)'),
                ))
    fig.add_trace(go.Scatter(
                name="Real Volume",
                x=df.time, 
                y=df.metric,
                line=dict(color='rgb(4, 132, 108)'),
                mode='lines'
                ))
    fig.add_trace(go.Scatter(
                name="Predicted Volume",
                x=df.time, 
                y=df.predicted_metric,
                line=dict(color='rgb(227, 123, 4)'),
                mode='lines'
                ))
    fig.update_layout(
                title={'text': "Volume - Prediction",'x':0.5},
                margin=dict(l=20, r=20, t=30, b=20,pad=0),
                plot_bgcolor="rgb(243, 243, 243)",
                legend=dict(orientation="h",)
                )
    return fig

def daily_production_char(df,mode):
    if mode == 'area':
        fig = px.area(df, x="time", y="metric", color="route_name",markers=False ,line_group ="fdcsite_name")
    elif mode == 'bar':
        fig = px.bar(df, x="time", y="metric", color="route_name")
    else:
        fig = px.bar(df, x="time", y="metric", color="route_name")
    fig.update_layout(
                title={'text': "Daily Production",'x':0.5},
                margin=dict(l=20, r=20, t=30, b=20,pad=0),
                plot_bgcolor="rgb(243, 243, 243)",
                legend=dict(orientation="h",),
                xaxis_title="Volume MCF",
                yaxis_title="",
                legend_title="Sites"
                )
    return fig

def anomalies_map(df):
    fig = go.Figure()

    fig.add_trace(go.Scattermapbox(
        lat=df.latitude,
        lon=df.longitude,
        mode='markers',
        marker=go.scattermapbox.Marker(
            size=15,
            color =df['anomaly'],
            colorscale= [(0, "green"), (0.8, "yellow"), (1, "red")],
            #opacity=0.3,
            symbol = 'circle',
            showscale=True,
        ),
        text=df['fdcsite_name'],
    ))

    fig.update_layout(mapbox=dict(
                    zoom=3,
                    center=dict(
                            lat=38,
                            lon=-94
                            )))

    
    fig.update_layout(mapbox_style="open-street-map")
    fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
    return fig

def multiple_rolling_calc_chart(df,groupby):
    fig = go.Figure()
    for site, group in  df.groupby(groupby):
        fig.add_trace(go.Scatter(x=group["time"] , y=group["seven_days_avg_difference"] , name= site,fill='tozeroy',
            hovertemplate="%s<br>Date=%%{x}<br>Variance=%%{y}<br><extra></extra>"% site,
            hoverinfo ='skip',
            ))
    
    fig.update_layout(title={'text': "Variance Percentaje by Site",'x':0.5},)
    return fig

def single_rolling_calc_chart(df,df_predicted):
    fig = go.Figure()
    fig.add_trace(go.Scatter(
            name="5%",
            x=df.time, 
            y=df["five_percent"],
            mode='lines',
            line=dict(color='rgb(166, 172, 175)')
            ))
    fig.add_trace(go.Scatter(
            name="-5%",
            x=df.time, 
            y=df["minus_five_percent"],
            mode='lines',
            line=dict(color='rgb(166, 172, 175)'),
            ))
    fig.add_trace(go.Scatter(
            name="MCF Variance",
            x=df.time, 
            y=df["seven_days_avg_difference"],
            line=dict(color='rgb(4, 132, 108)'),
            mode='lines',
            fill='tozeroy'
            ))
    
    fig.add_trace(go.Scatter(
            name="MCF Variance Predicted",
            x=df_predicted.time, 
            y=df_predicted["seven_days_avg_difference"],
            line=dict(color='rgb(227, 123, 4)'),
            mode='lines',
            fill='tozeroy'
            ))

    fig.update_layout(
            title={'text': "Volume Variance Percentage",'x':0.5},
            margin=dict(l=20, r=20, t=30, b=20,pad=0),
            plot_bgcolor="rgb(243, 243, 243)",
            legend=dict(orientation="h",)
            )
    return fig
from databricks import sql
from pandas import DataFrame

def data_bars(df, column):
    n_bins = 100
    bounds = [i * (1.0 / n_bins) for i in range(n_bins + 1)]
    ranges = [
        ((df[column].max() - df[column].min()) * i) + df[column].min()
        for i in bounds
    ]
    styles = []
    for i in range(1, len(bounds)):
        min_bound = ranges[i - 1]
        max_bound = ranges[i]
        max_bound_percentage = bounds[i] * 100
        styles.append({
            'if': {
                'filter_query': (
                    '{{{column}}} >= {min_bound}' +
                    (' && {{{column}}} < {max_bound}' if (i < len(bounds) - 1) else '')
                ).format(column=column, min_bound=min_bound, max_bound=max_bound),
                'column_id': column
            },
            'background': (
                """
                    linear-gradient(90deg,
                    #0074D9 0%,
                    #0074D9 {max_bound_percentage}%,
                    white {max_bound_percentage}%,
                    white 100%)
                """.format(max_bound_percentage=max_bound_percentage)
            ),
            'paddingBottom': 2,
            'paddingTop': 2
        })

    return styles

def get_from_adb(adb_sql_params,query):
    with sql.connect(
        adb_sql_params["server_hostname"],
        adb_sql_params["http_path"],
        adb_sql_params["access_token"],
    ) as adb_connection:
        with adb_connection.cursor() as cursor:
            cursor.execute(query)
            column_names = [desc[0] for desc in cursor.description]
            data = cursor.fetchall()
            return DataFrame(data,columns = column_names)


def rolling_calc(data,group,column):
    def func(row):
        if row['x_rolling'] == 0 or row[column] == 0 or row[column] is None or row['x_rolling'] is None:
            return None
        else:
            return ((float(row[column])/row['x_rolling'])-1)*100

    df = data.groupby(['time',group],as_index = False)[column].sum()
    df['x_rolling'] = df.groupby(group)[column].rolling(window=6,closed='both').mean().reset_index(0,drop=True)
    df['seven_days_avg_difference'] = df.apply(func, axis=1)
    return df.sort_values('time')


def assets():
    conn = {"server_hostname":"adb-7333588732851428.8.azuredatabricks.net",
          "http_path": "sql/protocolv1/o/7333588732851428/0524-184652-rygho0mp",
          "access_token":"dapi273c304bae10719c35407c9b8ab9f7ed-3"}
    query = """
        SELECT DISTINCT
            trim(upper(asset.district)) as district, 
            trim(upper(asset.route_name)) as route_name, 
            trim(upper(asset.fdcsite_name)) as fdcsite_name,
            cast(replace(latitude,',','.')as float) as latitude,
            cast(replace(longitude,',','.')as float) as longitude
        FROM dev_dgo_historian.tse_gdv_inference_prophet_by1 asset
        LEFT JOIN dev_dgo_historian.geographical_data geo on asset.fdcsite_name = geo.fdcsite_name    
        WHERE asset.route_name is not null and asset.route_name != 'None' and
            asset.fdcsite_name is not null and asset.fdcsite_name != 'None' 
        ORDER BY district asc
    """
    return get_from_adb(conn,query)  

def metrics(district,start_date,end_date):
    conn = {"server_hostname":"adb-7333588732851428.8.azuredatabricks.net",
          "http_path": "sql/protocolv1/o/7333588732851428/0524-184652-rygho0mp",
          "access_token":"dapi273c304bae10719c35407c9b8ab9f7ed-3"}

    query = """
        SELECT 
            TIME1 as time, 
            previous_day_volume as metric,
            predicted_payload_volume as predicted_metric, 
            lower_bound_volume as lower_bound,
            upper_bound_volume as upper_bound,
            trim(upper(district)) as district, 
            trim(upper(route_name)) as route_name, 
            trim(upper(fdcsite_name)) as fdcsite_name,
            anomaly_volume as anomaly
        FROM dev_dgo_historian.tse_gdv_inference_prophet_by1 
        WHERE trim(district) = '{}' and TIME1 BETWEEN '{}' and '{}' and 
            route_name is not null and route_name != 'None' and
            fdcsite_name is not null and fdcsite_name != 'None' 
        ORDER by time1 asc  
    """.format(district,start_date,end_date)
    return get_from_adb(conn,query)


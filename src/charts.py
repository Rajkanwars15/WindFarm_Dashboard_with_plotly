import dash
from dash import dcc, html
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from dash.dependencies import Input, Output
from itertools import compress

df = pd.DataFrame({
    'Date/Time': pd.date_range(start='1/1/2020', periods=100, freq='M'),
    'LV ActivePower': np.random.rand(100) * 100
})
df['Month'] = df['Date/Time'].dt.month
monthly_data = df.groupby('Month')['LV ActivePower'].sum()
threshold = 1000
next_hundred = 2000
coordinates = [(np.random.uniform(-180, 180), np.random.uniform(-90, 90)) for _ in range(100)]

# Ensure we only calculate cumulative sum on numeric columns
df_numeric = df.select_dtypes(include=[np.number])
df_cumsum = df_numeric.cumsum()

def adjust_color_lightness(color, amount=0.5):
    import colorsys
    try:
        c = to_rgb(color)
        c = colorsys.rgb_to_hls(*c)
        return to_hex(colorsys.hls_to_rgb(c[0], max(0, min(1, amount * c[1])), c[2]))
    except:
        return color

def create_monthly_power_plot():
    fig = go.Figure([go.Bar(x=[f'Month {m}' for m in monthly_data.index], y=monthly_data.values)])
    fig.update_layout(title='Monthly Sum of LV ActivePower', xaxis_title='Month', yaxis_title='LV ActivePower (kW)')
    return fig

def create_noise_difference_plot():
    np.random.seed(42)
    noise = np.random.normal(0, 10000000, size=monthly_data.shape)
    second_year_data = monthly_data + noise
    differences = second_year_data - monthly_data
    fig = go.Figure(data=[go.Bar(x=[f'Month {m}' for m in monthly_data.index], y=differences, marker_color=['green' if x > 0 else 'red' for x in differences])])
    fig.update_layout(title='Difference Between Year 2 and Year 1 (with Noise)', xaxis_title='Month', yaxis_title='Difference in LV ActivePower (kW)')
    return fig

def create_gps_plot():
    n_points = len(coordinates)
    target_colors = ['yellow']
    base_colors = ['green', 'red', 'yellow']
    light_colors = [adjust_color_lightness(color, 1.5) for color in base_colors]
    dark_colors = [adjust_color_lightness(color, 0.6) for color in base_colors]
    np.random.seed(42)
    base_color_indices = np.zeros(n_points).astype(int)
    warning_indices = np.random.choice(n_points, size=int(0.1 * n_points), replace=False)
    red_indices = warning_indices[:3]
    yellow_indices = warning_indices[3:]
    base_color_indices[red_indices] = 1
    base_color_indices[yellow_indices] = 2
    point_colors = [base_colors[bci] for bci in base_color_indices]
    target_indices = [pc in target_colors for pc in point_colors]
    longitudes, latitudes = zip(*coordinates)
    min_lat, max_lat = min(latitudes), max(latitudes)
    min_lon, max_lon = min(longitudes), max(longitudes)
    lat_range = max_lat - min_lat
    lon_range = max_lon - min_lon
    min_lat -= lat_range * 0.1
    max_lat += lat_range * 0.1
    min_lon -= lon_range * 0.1
    max_lon += lon_range * 0.1
    data = [go.Scattergeo(lon=list(compress(longitudes, target_indices)), lat=list(compress(latitudes, target_indices)), mode='markers', marker=dict(size=7, color=[light_colors[base_colors.index(color)] for color in list(compress(point_colors, target_indices))], line=dict(width=1, color=[dark_colors[base_colors.index(color)] for color in list(compress(point_colors, target_indices))])))]
    layout = go.Layout(title='GPS Coordinates Visualization', geo=dict(showland=True, landcolor="rgb(217, 217, 217)", subunitcolor="rgb(255, 255, 255)", countrycolor="rgb(255, 255, 255)", showlakes=True, lakecolor="rgb(255, 255, 255)", showsubunits=True, showcountries=True, resolution=50, projection=dict(type="mercator"), lonaxis=dict(showgrid=True, gridwidth=0.5, range=[min_lon, max_lon], dtick=5), lataxis=dict(showgrid=True, gridwidth=0.5, range=[min_lat, max_lat], dtick=5)))
    fig = go.Figure(data=data, layout=layout)
    return fig

def create_quarterly_summary_plot():
    categories = ["Up time", "Unexpected failures", "Profit/loss"][::-1]
    values = [0.8, 0.6, 1.3][::-1]
    is_good_increase = [True, False, True][::-1]
    log_values = np.log2(values)
    colors = ['green' if (v > 0 and good) or (v < 0 and not good) else 'red' for v, good in zip(log_values, is_good_increase)]
    fig = go.Figure()
    for category, value, color in zip(categories, log_values, colors):
        base = 0
        width = value - base
        fig.add_trace(go.Bar(x=[width], y=[category], orientation='h', marker_color=color, base=base, name=category))
    fig.update_layout(xaxis=dict(tickvals=np.log2([0.5, 1, 2]), ticktext=['Half', 'No Change', 'Double'], range=[np.log2(0.5), np.log2(2)], showline=True, showgrid=True, gridcolor='gray', linecolor='black'), title="Quarterly Summary of Changes", xaxis_title="Change Scale (Log Scale)", yaxis_title="Categories", plot_bgcolor='white', yaxis=dict(showline=True))
    return fig

def create_failure_model_plot():
    models = ['V47-0.66', 'GE1.5-82.5', 'Z50', 'V117-4.3']
    durations = [0.8, 2.3, 2.4, 4.8]
    fig = go.Figure()
    for model, duration in zip(models, durations):
        fig.add_trace(go.Bar(x=[duration], y=[model], orientation='h', marker_color='blue'))
    fig.update_layout(title="Failure Model Durations", xaxis_title="Duration (hours)", yaxis_title="Models", plot_bgcolor='white')
    return fig

def create_time_series_plot(df_cumsum, threshold, next_hundred):
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df['Date/Time'], y=df_cumsum['LV ActivePower'], mode='lines', name='Active Power'))
    fig.add_hline(y=threshold, line_dash='dot', line_color='red', annotation_text='Threshold', annotation_position='bottom right')
    fig.add_hline(y=next_hundred, line_dash='dot', line_color='green', annotation_text='Next Hundred', annotation_position='top right')
    fig.update_layout(title='Cumulative Active Power Over Time', xaxis_title='Date/Time', yaxis_title='Cumulative Active Power (kW)')
    return fig

def create_stacked_bar_plot(df):
    df['year'] = df['Date/Time'].dt.year
    df['month'] = df['Date/Time'].dt.month
    monthly_data = df.groupby(['year', 'month'])['LV ActivePower'].sum().unstack(level=0)
    fig = go.Figure()
    for year in monthly_data.columns:
        fig.add_trace(go.Bar(x=[f'{month:02d}' for month in monthly_data.index], y=monthly_data[year], name=str(year)))
    fig.update_layout(title='Monthly Active Power Comparison', xaxis_title='Month', yaxis_title='Active Power (kW)', barmode='stack')
    return fig

def create_bearing_health_plot(metric):
    fig = go.Figure()
    x = np.arange(10)
    y = np.random.rand(10)
    fig.add_trace(go.Scatter(x=x, y=y, mode='lines+markers', name='Bearing Health'))
    fig.update_layout(title='Bearing Health Prediction', xaxis_title='Time', yaxis_title='Health Metric')
    return fig
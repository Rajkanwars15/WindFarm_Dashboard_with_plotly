import dash
from dash import dcc, html
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
from charts import *

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP, 'style.css'])

# Sample DataFrame for demonstration
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

# Header and footer contents
header = html.Div([
    html.H1("neuralix.ai"),
    html.H3("Windfarm Dashboard"),
])

footer = html.Div([
    html.P("Copyright © 2024 Windfarm"),
])

# Statistics row
statistics_row = dbc.Row([
], className="mb-4")

# Toggle button definition
app.layout = html.Div([
    header,  # Include the header
    dcc.Tabs([
        dcc.Tab(label='Home', children=[
            html.Div(style={'margin-bottom': '20px'}),  # Add margin between tabs and statistics row
            statistics_row,  # Include the statistics row
            html.Div([
                dcc.Graph(id='plot1', figure=create_monthly_power_plot(), className='rounded-graph graph-spacing'),
                dcc.Link('', href='/slide2'),
                dcc.Graph(id='plot2', figure=create_noise_difference_plot(), className='rounded-graph graph-spacing'),
                dcc.Link('', href='/slide3'),
                dcc.Graph(id='plot3', figure=create_gps_plot(), className='rounded-graph graph-spacing'),
                dcc.Link('', href='/slide4'),
                dcc.Graph(id='plot4', figure=create_quarterly_summary_plot(), className='rounded-graph graph-spacing'),
                dcc.Link('', href='/slide5'),
                dcc.Graph(id='plot5', figure=create_failure_model_plot(), className='rounded-graph graph-spacing'),
                dcc.Link('', href='/slide6'),
                dcc.Graph(id='plot6', figure=create_time_series_plot(df_cumsum, threshold, next_hundred), className='rounded-graph graph-spacing'),
                dcc.Link('', href='/slide7'),
                dcc.Graph(id='plot7', figure=create_stacked_bar_plot(df), className='rounded-graph graph-spacing'),
                dcc.Link('', href='/slide8'),
                dcc.Graph(id='plot8', figure=create_bearing_health_plot('pred'), className='rounded-graph graph-spacing'),
            ]),
        ]),
        dcc.Tab(label='Slide 2', children=[
            html.Div([
                dcc.Graph(figure=create_noise_difference_plot(), className='rounded-graph'),
                dbc.Row([
                    dbc.Col(dcc.Graph(figure=create_quarterly_summary_plot(), className='rounded-graph'), width=6),
                    dbc.Col(dcc.Graph(figure=create_gps_plot(), className='rounded-graph'), width=6)
                ])
            ])
        ]),
        dcc.Tab(label='Slide 3', children=[html.Div([dcc.Graph(figure=create_noise_difference_plot())])]),
        dcc.Tab(label='Slide 4', children=[html.Div([dcc.Graph(figure=create_quarterly_summary_plot())])]),
        dcc.Tab(label='Slide 5', children=[html.Div([dcc.Graph(figure=create_failure_model_plot())])]),
        dcc.Tab(label='Slide 6', children=[html.Div([dcc.Graph(figure=create_time_series_plot(df_cumsum, threshold, next_hundred))])]),
        dcc.Tab(label='Slide 7', children=[html.Div([dcc.Graph(figure=create_stacked_bar_plot(df))])]),
        dcc.Tab(label='Slide 8', children=[html.Div([dcc.Graph(figure=create_bearing_health_plot('pred'))])])
    ]),
    footer,  # Include the footer
], className="light-theme")

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)

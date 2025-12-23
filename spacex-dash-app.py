# Import required libraries
import pandas as pd
import dash
from dash import html, dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Read the SpaceX launch data
spacex_df = pd.read_csv("spacex_launch_dash.csv")

# Get min and max payload values
min_payload = spacex_df['Payload Mass (kg)'].min()
max_payload = spacex_df['Payload Mass (kg)'].max()

# Create Dash app
app = dash.Dash(__name__)

# App layout
app.layout = html.Div(children=[

    html.H1(
        'SpaceX Launch Records Dashboard',
        style={'textAlign': 'center', 'color': '#503D36', 'font-size': 40}
    ),

    # Launch site dropdown
    dcc.Dropdown(
        id='site-dropdown',
        options=[
            {'label': 'All Sites', 'value': 'ALL'},
            {'label': 'CCAFS LC-40', 'value': 'CCAFS LC-40'},
            {'label': 'CCAFS SLC-40', 'value': 'CCAFS SLC-40'},
            {'label': 'KSC LC-39A', 'value': 'KSC LC-39A'},
            {'label': 'VAFB SLC-4E', 'value': 'VAFB SLC-4E'}
        ],
        value='ALL',
        placeholder="Select a launch site",
        searchable=True
    ),

    html.Br(),

    # Pie chart
    html.Div(dcc.Graph(id='success-pie-chart')),

    html.Br(),

    html.P("Payload range (Kg):"),

    # Payload range slider
    dcc.RangeSlider(
        id='payload-slider',
        min=min_payload,
        max=max_payload,
        step=1000,
        marks={
            int(min_payload): str(int(min_payload)),
            2500: '2500',
            5000: '5000',
            7500: '7500',
            int(max_payload): str(int(max_payload))
        },
        value=[min_payload, max_payload]
    ),

    html.Br(),

    # Scatter plot
    html.Div(dcc.Graph(id='success-payload-scatter-chart'))
])

# CALLBACK 1: Update pie chart
@app.callback(
    Output('success-pie-chart', 'figure'),
    Input('site-dropdown', 'value')
)
def update_pie_chart(selected_site):

    if selected_site == 'ALL':
        success_df = spacex_df[spacex_df['class'] == 1]
        site_success = success_df['Launch Site'].value_counts().reset_index()
        site_success.columns = ['Launch Site', 'Success Count']

        fig = px.pie(
            site_success,
            values='Success Count',
            names='Launch Site',
            title='Total Successful Launches by Site'
        )

    else:
        site_df = spacex_df[spacex_df['Launch Site'] == selected_site]
        outcome_counts = site_df['class'].value_counts().reset_index()
        outcome_counts.columns = ['class', 'count']

        fig = px.pie(
            outcome_counts,
            values='count',
            names='class',
            title=f'Success vs Failure for {selected_site}'
        )

    return fig

# CALLBACK 2: Update scatter plot
@app.callback(
    Output('success-payload-scatter-chart', 'figure'),
    [
        Input('site-dropdown', 'value'),
        Input('payload-slider', 'value')
    ]
)
def update_scatter_chart(selected_site, payload_range):

    low, high = payload_range

    filtered_df = spacex_df[
        (spacex_df['Payload Mass (kg)'] >= low) &
        (spacex_df['Payload Mass (kg)'] <= high)
    ]

    if selected_site != 'ALL':
        filtered_df = filtered_df[filtered_df['Launch Site'] == selected_site]

    fig = px.scatter(
        filtered_df,
        x='Payload Mass (kg)',
        y='class',
        color='Booster Version Category',
        hover_data=['Launch Site'],
        title='Payload vs Launch Success'
    )

    return fig

# Run the app
if __name__ == '__main__':
    app.run(port=8090)

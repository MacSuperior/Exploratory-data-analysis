import pandas as pd
import plotly.express as px
import dash
import dash_bootstrap_components as dbc
from dash import dcc, html, Input, Output
import folium

# TODO just drop columns not in use before importing
df = pd.read_pickle("data.pkl")
airport_data = pd.read_pickle("airport_data.pkl")

unique_airports = pd.unique(pd.concat([df['Origin'], df['Dest']]))

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.GRID])

def calculate_metric(df, delay_type_key, method):
    if method == "mean":
        return df.groupby('UniqueCarrier')[delay_type_key].mean().reset_index()
    elif method == "total":
        return df.groupby('UniqueCarrier')[delay_type_key].sum().reset_index()

delay_types = {
    "ArrDelay": "Arrival Delay",
    "DepDelay": "Departure Delay",
    "CarrierDelay": "Carrier Delay",
    "WeatherDelay": "Weather Delay",
    "NASDelay": "NAS Delay",
    "SecurityDelay": "Security Delay",
    "LateAircraftDelay": "Late Aircraft Delay"
}

airline_dict = {
    'WN': 'Southwest Airlines',
    'XE': 'ExpressJet Airlines',
    'YV': 'Mesa Airlines',
    'OH': 'Comair',
    'OO': 'SkyWest Airlines',
    'UA': 'United Airlines',
    'US': 'US Airways',
    'DL': 'Delta Air Lines',
    'EV': 'ExpressJet Airlines',
    'F9': 'Frontier Airlines',
    'FL': 'AirTran Airways',
    'HA': 'Hawaiian Airlines',
    'MQ': 'Envoy Air (formerly American Eagle Airlines)',
    'NW': 'Northwest Airlines',
    '9E': 'Endeavor Air',
    'AA': 'American Airlines',
    'AQ': 'Aloha Airlines',
    'AS': 'Alaska Airlines',
    'B6': 'JetBlue Airways',
    'CO': 'Continental Airlines'
}

@app.callback(
    Output('flights-per-carrier', 'figure'),
    [Input('my-date-picker-range', 'start_date'), Input('my-date-picker-range', 'end_date')],
    Input('airline-selector', 'value')
)
def update_graph(start_date, end_date, selected_carriers):
    date_filtered_df = df.loc[(pd.Timestamp(start_date) <= df["Date"]) & (df["Date"] <= pd.Timestamp(end_date))]

    fully_filtered = date_filtered_df[date_filtered_df['UniqueCarrier'].isin(selected_carriers)]

    # Amount of flights for certain airports
    carrier_weight = fully_filtered["UniqueCarrier"].value_counts().reset_index(name="Count")

    # Create the bar chart
    fig = px.bar(carrier_weight, x="UniqueCarrier", y="Count", 
                title="Airline flights Distribution",
                labels={"UniqueCarrier": "Carrier Code", "Count": "Amount of flights"})

    # Show the plot
    return fig

@app.callback(
    Output('graph-output', 'figure'),
    [Input('my-date-picker-range', 'start_date'), Input('my-date-picker-range', 'end_date')],
    Input('calculation-method', 'value'),
    [Input('delay-type', 'value')]
)
def update_graph(start_date, end_date, method, delay_type_key):
    # TODO: make sorting of airports optional in UI
    # TODO: allow for different orientation of chart based on selection
    delay_type_value = delay_types[delay_type_key]
    df_filtered = df.loc[(pd.Timestamp(start_date) <= df["Date"]) & (df["Date"] <= pd.Timestamp(end_date))]

    result_df = calculate_metric(df_filtered, delay_type_key, method)
    result_df = result_df.sort_values(by=delay_type_key, ascending=False)
    
    fig = px.bar(result_df, x='UniqueCarrier', y=delay_type_key,
                title=f'{method.capitalize()} {delay_type_value} by Airline',
                color='UniqueCarrier',
                text=delay_type_key,
                height=600)
    
    fig.update_yaxes(title=f'{method.capitalize()} {delay_type_value} (minutes)')
    fig.update_traces(texttemplate='%{text:.2f}',
                      textposition='inside',
                      textfont=dict(size=14))
    fig.update_xaxes(type='category', title='Airline')
    fig.update_layout(xaxis_categoryorder='total descending',
                      uniformtext_minsize=10,  
                      uniformtext_mode='show')

    return fig

def update_map():
    m_selected = folium.Map(location=[30, -95], tiles="OpenStreetMap", zoom_start=4.5)
    airport_group = folium.FeatureGroup(name="Show Airports", show=True).add_to(m_selected)
    not_in_data_airport = folium.FeatureGroup(name="Show airports not in this data", show=False).add_to(m_selected)

    for index, row in airport_data.iterrows():
        if row['IATA'] in unique_airports:
            custom_marker_icon = folium.CustomIcon(
                icon_image = "data:image/png;base64,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",
                icon_size=(32, 32)
            )

            folium.Marker(
                location=[row['LATITUDE'], row['LONGITUDE']],
                popup=row['IATA'],
                icon=custom_marker_icon
            ).add_to(airport_group)
        else:
            folium.Marker(
                location=[row['LATITUDE'], row['LONGITUDE']],
                popup=row["IATA"]
            ).add_to(not_in_data_airport)

    folium.LayerControl(collapsed=True).add_to(m_selected)

    return m_selected._repr_html_()

app.layout = dbc.Container(
    [
        dbc.Row(
            [
                dbc.Col(
                    html.Iframe(
                        id='airport-map',
                        srcDoc=update_map(),
                        width='100%',
                        height=600),
                width=12),
            ],
        ),
        dbc.Row(
            [
                dbc.Col(
                    dcc.RadioItems(
                        options=[
                            {'label': 'Use the average delay', 'value': 'mean'},
                            {'label': 'Use the total delay', 'value': 'total'}],
                        value='mean',
                        id='calculation-method'),
                ),
            ],
            justify="start",
        ),
        dbc.Row(
            [
                dbc.Col(
                    [
                        dcc.RadioItems(
                            options=[ {"label": label, "value": value} for value, label in delay_types.items()],
                            value='ArrDelay',
                            id='delay-type'),
                        dcc.DatePickerRange(
                            id='my-date-picker-range',
                            min_date_allowed=df['Date'].min(),
                            max_date_allowed=df['Date'].max(),
                            initial_visible_month=df['Date'].min(),
                            start_date=df['Date'].min(),
                            end_date=df['Date'].max()),
                    ],         
                    width=3
                ),
                dbc.Col(
                    dcc.Graph(id='graph-output'),
                    width=9
                ),
            ],
            align="center",
        ),

        dbc.Row(
            [
                dbc.Col(
                    dcc.Checklist(
                        options=[{'label': air_carrier, 'value': air_carrier_code} for air_carrier_code, air_carrier in airline_dict.items()],
                        value=[key for key in airline_dict.keys()],
                        id='airline-selector'
                        ),
                ),
                dbc.Col(
                    dcc.Graph(id='flights-per-carrier')   ,
                    width=9                 
                ),
                html.Br() # Breathing room
            ]
        ),
    ],
    fluid=True,
)

if __name__ == '__main__':
    app.run_server(debug=True)

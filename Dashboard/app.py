import dash
from dash import dcc, html, Input, Output
import pandas as pd
import plotly.express as px

df = pd.read_pickle('data.pkl')

# TODO: Figure out a way to preprocess data before loading (maybe via an install script to pickle)
df.rename(columns={'DayofMonth': 'Day'}, inplace=True) 
df["Date"] = pd.to_datetime(df[["Year", "Month", "Day"]])

app = dash.Dash(__name__)

app.layout = html.Div([
    html.H1("Flight Delay Analysis"),
    html.Div([
        scatter_input_x := dcc.Dropdown(
            options=[{'label': column, 'value': column} for column in df.columns],
            value=df.columns[14],  # Default value
            multi=False
        ),
        
        scatter_input_y := dcc.Dropdown(
            options=[{'label': column, 'value': column} for column in df.columns],
            value=df.columns[15],  # Default value
            multi=False
        )],
    ),
    html.Br(),
    html.Div([
        scatter_plot := dcc.Graph(),
        scatter_slider := dcc.Slider(min=df["Date"].min().timestamp(),
                                     max=df["Date"].max().timestamp(),
                                     value=df["Date"].max().timestamp(),
                                     marks={df["Date"].min().timestamp(): df["Date"].min().strftime('%Y-%m-%d'),
                                            df["Date"].max().timestamp(): df["Date"].max().strftime('%Y-%m-%d')})
    ]),
    html.Br(),
    #TODO: Have a histogram plot of average delay per month, and an accompanying line chart of the month hovered
    html.Div([
        line_radio := dcc.RadioItems(options=["Day", "Month"],
                                     value='Month'),
        line_plot := dcc.Graph()
    ]),
])

@app.callback(
    Output(scatter_plot, 'figure'),
    Input(scatter_input_x, 'value'),
    Input(scatter_input_y, 'value'),
    Input(scatter_slider, 'value')
)
def update_scatter_plot(scatter_input_x, scatter_input_y, scatter_slider):
    filtered_df = df[df["Date"] <= pd.Timestamp(scatter_slider, unit='s')]

    scatter_fig = px.scatter(filtered_df,
                             x=scatter_input_x,
                             y=scatter_input_y,
                             title=f'{scatter_input_x} Versus {scatter_input_y}')

    return scatter_fig

@app.callback(
    Output(line_plot, 'figure'),
    Input(line_radio, 'value')
)
def update_line_plot(line_radio):
    monthly_avg_arrival_delay = df.groupby(line_radio)['ArrDelay'].mean() # Group by input
    monthly_avg_departure_delay = df.groupby(line_radio)['DepDelay'].mean()

    monthly_delay_df = pd.DataFrame({line_radio: monthly_avg_arrival_delay.index,
                                    'AverageArrivalDelay': monthly_avg_arrival_delay.values,
                                    'AverageDepartureDelay': monthly_avg_departure_delay.values})

    line_fig = px.line(monthly_delay_df,
                  x=line_radio,
                  y=['AverageArrivalDelay', 'AverageDepartureDelay'],
                  labels={'value': 'Average Delay (minutes)'},
                  title=f'Trend of Arrival and Departure Delays Throughout the {line_radio}')

    return line_fig
if __name__ == '__main__':
    app.run_server(debug=True)

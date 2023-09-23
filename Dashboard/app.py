# Import necessary libraries
import pandas as pd
import plotly.express as px
from flask import Flask, render_template
import plotly.graph_objs as go

# Load the dataset
df = pd.read_csv("airlinedelaycauses_DelayedFlights.csv")

# Create a Flask app
app = Flask(__name__)

# Define a route for the dashboard
@app.route("/")
def dashboard():
    # Create a scatter plot of departure delay vs. arrival delay
    scatter_plot = go.Figure(data=go.Scatter(
        x=df['DepDelay'],
        y=df['ArrDelay'],
        mode='markers',
        marker=dict(size=5),
        text=df['UniqueCarrier']
    ))

    scatter_plot.update_layout(
        title="Departure Delay vs. Arrival Delay",
        xaxis_title="Departure Delay (minutes)",
        yaxis_title="Arrival Delay (minutes)",
        hovermode='closest'
    )

    # Convert the plot to JSON for embedding in the HTML template
    scatter_plot_json = scatter_plot.to_json()

    # Render the dashboard template with the scatter plot
    return render_template("dashboard.html", scatter_plot_json=scatter_plot_json)

# Run the Flask app
if __name__ == "__main__":
    app.run(debug=True)

import os
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import dash
from dash import dcc, html
from google.cloud import bigquery


# GCP BigQuery details from environment variables (Cloud Run should have these set)
PROJECT_ID = os.getenv("GCP_PROJECT_ID", "plant-454208")
BQ_DATASET = os.getenv("BQ_DATASET", "plant_data")  
BQ_TABLE = os.getenv("BQ_TABLE", "plant_health")  

# Query BigQuery Table
def fetch_data():
    client = bigquery.Client()  # No need for explicit credentials in Cloud Run
    query = f"SELECT * FROM `{PROJECT_ID}.{BQ_DATASET}.{BQ_TABLE}`"
    df = client.query(query).to_dataframe()

    # Convert timestamp and extract week
    df["Timestamp"] = pd.to_datetime(df["Timestamp"])
    df["Week"] = df["Timestamp"].dt.isocalendar().week
    return df

# Load data from BigQuery
data = fetch_data()

# Extract unique weeks and plants
unique_weeks = sorted(data["Week"].unique())
unique_plants = sorted(data["Plant_ID"].unique())

# Dash App
app = dash.Dash(__name__)
app.layout = html.Div([
    html.H1("Plant Health Dashboard"),
    
    # Dropdowns
    html.Div([
        html.Label("Select Week:"),
        dcc.Dropdown(
            id="week-dropdown",
            options=[{"label": f"Week {w}", "value": w} for w in unique_weeks],
            value=unique_weeks[0],
            style={"width": "200px", "display": "inline-block", "margin-right": "10px"}
        ),

        html.Label("Select Plant ID:"),
        dcc.Dropdown(
            id="plant-dropdown",
            options=[{"label": f"Plant {p}", "value": p} for p in unique_plants],
            value=unique_plants[0],
            style={"width": "200px", "display": "inline-block"}
        ),
    ], style={"display": "flex", "align-items": "center", "gap": "10px"}),

    # Graphs
    html.Div([
        html.Div([dcc.Graph(id="plant-health-chart"), html.H3("Plant Health Status", style={"text-align": "center"})], style={"flex": "1"}),
        html.Div([dcc.Graph(id="env-factors-chart"), html.H3("Environmental Factors", style={"text-align": "center"})], style={"flex": "1"}),
    ], style={"display": "flex", "justify-content": "space-between"})
])

# Callback to update graphs
@app.callback(
    [dash.Output("plant-health-chart", "figure"), dash.Output("env-factors-chart", "figure")],
    [dash.Input("week-dropdown", "value"), dash.Input("plant-dropdown", "value")]
)
def update_charts(week, plant):
    filtered_data = data[(data["Week"] == week) & (data["Plant_ID"] == plant)]
    
    # Pie Chart
    pie_data = filtered_data["Plant_Health_Status"].value_counts().reset_index()
    pie_data.columns = ["Plant_Health_Status", "Count"]
    fig1 = go.Figure(data=[go.Pie(labels=pie_data["Plant_Health_Status"], values=pie_data["Count"], hole=0.3)])
    
    # Bar Chart
    env_factors = [
        'Soil_Moisture', 'Ambient_Temperature', 'Soil_Temperature', 'Humidity', 
        'Soil_pH', 'Nitrogen_Level', 'Phosphorus_Level', 'Potassium_Level', 
        'Chlorophyll_Content', 'Electrochemical_Signal'
    ]
    env_data = {factor: filtered_data[factor].mean() for factor in env_factors}
    fig2 = go.Figure(data=[go.Bar(x=list(env_data.keys()), y=list(env_data.values()))])
    
    return fig1, fig2

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))  
    app.run(debug=False, host="0.0.0.0", port=port)  


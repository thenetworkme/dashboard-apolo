import dash
from dash import dcc, html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output
import plotly.graph_objects as go
import json

with open("datos.json", "r") as file:
    data = json.load(file)


app = dash.Dash(__name__, external_stylesheets=[dbc.themes.COSMO])
app.title = "Spectrometer & LiDAR Dashboard"
server = app.server

categories = list(data.keys())


def generar_grafico_espectrometro(categoria, valores):
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=[f"λ{i+1}" for i in range(len(valores))],
            y=valores,
            mode="lines+markers",
            name=categoria,
        )
    )
    fig.update_layout(
        title=f"Categoría: {categoria.replace('_', ' ').capitalize()}",
        xaxis_title="Longitud de Onda (λ)",
        yaxis_title="Intensidad",
        template="plotly_white",
    )
    return fig


def generar_grafico_lidar():
    theta = [i for i in range(0, 360, 5)]

    fig = go.Figure()
    fig.add_trace(
        go.Scatterpolar(
            theta=theta,
            mode="lines+markers",
            name="LiDAR Data",
            line=dict(color="black", dash="dot", width=1),
            marker=dict(size=3, color="black"),
        )
    )

    fig.update_layout(
        title="LiDAR - Visualización Polar (2D)",
        polar=dict(
            angularaxis=dict(
                tickmode="array",
                tickvals=[0, 30, 60, 90, 120, 150, 180, 210, 240, 270, 300, 330],
                ticktext=[
                    "0",
                    "30",
                    "60",
                    "90",
                    "120",
                    "150",
                    "180",
                    "-150",
                    "-120",
                    "-90",
                    "-60",
                    "-30",
                ],
                showline=True,
                linewidth=1,
                linecolor="black",
            ),
            radialaxis=dict(
                tickmode="array",
                tickvals=[0, 0.75, 1.5, 2.25, 3],
                ticktext=["0", "0.75", "1.5", "2.25", "3"],
                range=[0, 3],
                showline=True,
                gridcolor="gray",
                linecolor="black",
            ),
        ),
        template="plotly_white",
    )
    return fig


# Layout principal
app.layout = dbc.Container(
    [
        dbc.Row(
            dbc.Col(
                html.H1(
                    "Dashboard del Espectrómetro y LiDAR", className="text-center mb-4"
                ),
                width=12,
            )
        ),
        dbc.Row(
            [
                dbc.Col(
                    [
                        html.H3("Cámara", className="text-center"),
                        dbc.Card(
                            dbc.CardBody(
                                html.Video(
                                    id="video-feed",
                                    src="http://192.168.1.101:8080/video",
                                    controls=True,
                                    autoPlay=True,
                                    style={
                                        "width": "100%",
                                        "height": "650px",
                                        "borderRadius": "10px",
                                        "boxShadow": "0 4px 8px rgba(0,0,0,0.2)",
                                        "border": "none",
                                    },
                                ),
                            ),
                            style={
                                "backgroundColor": "#f8f9fa",
                                "border": "1px solid #ddd",
                                "borderRadius": "10px",
                                "padding": "10px",
                            },
                        ),
                    ],
                    width=6,
                ),
                dbc.Col(
                    [
                        html.H3("Espectrómetro", className="text-center"),
                        dcc.Graph(id="espectrometro-grafico"),
                        dcc.Interval(
                            id="intervalo-espectrometro",
                            interval=2000,  # Intervalo de actualización (ms)
                            n_intervals=0,
                        ),
                        html.H3("LiDAR - Tarea C", className="text-center mt-4"),
                        dcc.Graph(id="lidar-grafico", figure=generar_grafico_lidar()),
                    ],
                    width=6,
                ),
            ]
        ),
    ],
    fluid=True,
)


# Callback para actualizar el gráfico del espectrómetro
@app.callback(
    Output("espectrometro-grafico", "figure"),
    [Input("intervalo-espectrometro", "n_intervals")],
)
def actualizar_espectrometro(n_intervals):
    # Seleccionar la categoría basada en el número de intervalos
    category_index = n_intervals % len(categories)
    category = categories[category_index]
    values = data[category]
    return generar_grafico_espectrometro(category, values)


# Ejecutar la app
if __name__ == "__main__":
    app.run_server(debug=True)

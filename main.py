import dash
from dash import dcc, html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output
import plotly.graph_objects as go
import json


with open("datos.json", "r") as file:
    espectrometro_data = json.load(file)


with open("Lidar.json", "r") as file:
    lidar_data = json.load(file)

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.COSMO])
app.title = "Spectrometer & LiDAR Dashboard"
server = app.server


categories = list(espectrometro_data.keys())


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


def generar_grafico_lidar(data):
    angles = [entry["angle"] for entry in data]
    distances = [entry["distance"] for entry in data]

    central_angle = angles[0]
    central_distance = distances[0]

    # Crear la figura
    fig = go.Figure()

    # Graficar los datos del LiDAR como scatter polar
    fig.add_trace(
        go.Scatterpolar(
            theta=angles,
            r=distances,
            mode="lines+markers",
            name="LiDAR Data",
            line=dict(color="black", dash="dot", width=1),
            marker=dict(size=3, color="black"),
        )
    )

    fig.add_trace(
        go.Scatterpolar(
            theta=[0, central_angle],
            r=[0, central_distance],
            mode="lines",
            name="Línea Central",
            line=dict(color="red", width=3),
        )
    )

    fig.update_layout(
        title="LiDAR - Visualización Polar (2D)",
        polar=dict(
            angularaxis=dict(
                tickmode="array",
                tickvals=list(range(0, 360, 30)),
                ticktext=list(map(str, range(0, 360, 30))),
                showline=True,
                linewidth=1,
                linecolor="black",
            ),
            radialaxis=dict(
                tickmode="linear",
                tick0=0,
                dtick=0.5,
                range=[0, max(distances)],
                showline=True,
                gridcolor="gray",
                linecolor="black",
            ),
        ),
        template="plotly_white",
    )
    return fig, central_angle, central_distance


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
                            interval=2000,
                            n_intervals=0,
                        ),
                        html.H3("LiDAR - Tarea C", className="text-center mt-4"),
                        dcc.Graph(id="lidar-grafico"),
                        html.Div(
                            id="informacion-lidar",
                            children=[html.P("Ángulo: 0°"), html.P("Distancia: 0 m")],
                            style={"fontSize": "20px", "fontWeight": "bold"},
                        ),
                        dcc.Interval(
                            id="intervalo-lidar",
                            interval=4000,
                            n_intervals=0,
                        ),
                    ],
                    width=6,
                ),
            ]
        ),
    ],
    fluid=True,
)


@app.callback(
    Output("espectrometro-grafico", "figure"),
    [Input("intervalo-espectrometro", "n_intervals")],
)
def actualizar_espectrometro(n_intervals):
    category_index = n_intervals % len(categories)
    category = categories[category_index]
    values = espectrometro_data[category]
    return generar_grafico_espectrometro(category, values)


@app.callback(
    [Output("lidar-grafico", "figure"), Output("informacion-lidar", "children")],
    [Input("intervalo-lidar", "n_intervals")],
)
def actualizar_lidar(n_intervals):

    lidar_index = n_intervals % len(lidar_data["lidar_data"])
    data_segment = lidar_data["lidar_data"][lidar_index : lidar_index + 10]
    fig, central_angle, central_distance = generar_grafico_lidar(data_segment)

    informacion_lidar = [
        html.P(f"Ángulo: {central_angle}°"),
        html.P(f"Distancia: {central_distance} m"),
    ]

    return fig, informacion_lidar


if __name__ == "__main__":
    app.run_server(debug=True)

import dash
from dash import dcc, html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output
import plotly.graph_objects as go
import json
import numpy as np

# Cargar datos del LiDAR desde el archivo data.json (se mantiene esta parte)
with open("data.json", "r") as file:
    lidar_data = json.load(file)

# Inicializar la app con el tema COSMO de Bootstrap
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.COSMO])
app.title = "Spectrometer & LiDAR Dashboard"
server = app.server


# =============================================================================
# Funciones para el espectrómetro (adaptadas del primer código)
# =============================================================================
def generar_espectro(inicio, fin, dynamic_factor=0):
    wavelengths = np.linspace(380, 780, 400)
    intensities = np.exp(
        -0.5 * ((wavelengths - (inicio + fin) / 2 + dynamic_factor) ** 2) / 4000
    )
    colors = [
        f"rgb({int(r)}, {int(g)}, {int(b)})"
        for r, g, b in [wavelength_to_rgb(w) for w in wavelengths]
    ]
    fig = go.Figure()
    fig.add_trace(
        go.Bar(
            x=wavelengths,
            y=intensities,
            marker=dict(color=colors),
            showlegend=False,
        )
    )
    fig.update_layout(
        title="Espectro de Colores",
        xaxis_title="Longitud de Onda (nm)",
        yaxis_title="Intensidad",
        template="plotly_white",
        xaxis=dict(range=[380, 780]),
    )
    return fig


def wavelength_to_rgb(wavelength):
    if wavelength < 380 or wavelength > 780:
        return 0, 0, 0
    if wavelength < 440:
        r, g, b = -(wavelength - 440) / (440 - 380), 0, 1
    elif wavelength < 490:
        r, g, b = 0, (wavelength - 440) / (490 - 440), 1
    elif wavelength < 510:
        r, g, b = 0, 1, -(wavelength - 510) / (510 - 490)
    elif wavelength < 580:
        r, g, b = (wavelength - 510) / (580 - 510), 1, 0
    elif wavelength < 645:
        r, g, b = 1, -(wavelength - 645) / (645 - 580), 0
    else:
        r, g, b = 1, 0, 0
    factor = (
        1
        if wavelength < 420 or wavelength > 645
        else 0.3 + 0.7 * (wavelength - 380) / (780 - 380)
    )
    return (r * factor * 255, g * factor * 255, b * factor * 255)


# =============================================================================
# Función para generar el gráfico LiDAR (se mantiene del segundo código)
# =============================================================================
def generar_grafico_lidar(data):
    angles = data["a"]
    distances = data["d"]

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


# =============================================================================
# Diseño del layout adaptado
# =============================================================================
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
                # Columna de la cámara
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
                # Columna del espectrómetro y LiDAR
                dbc.Col(
                    [
                        html.H3("Espectrómetro", className="text-center"),
                        dbc.Row(
                            [
                                dbc.Col(
                                    [
                                        html.Label("Inicio del espectro (nm):"),
                                        dcc.Slider(
                                            id="inicio-slider",
                                            min=380,
                                            max=780,
                                            step=10,
                                            value=400,
                                            marks={380: "380", 780: "780"},
                                        ),
                                        html.Label("Fin del espectro (nm):"),
                                        dcc.Slider(
                                            id="fin-slider",
                                            min=380,
                                            max=780,
                                            step=10,
                                            value=700,
                                            marks={380: "380", 780: "780"},
                                        ),
                                    ],
                                    width=4,
                                ),
                                dbc.Col(
                                    dcc.Graph(id="espectrometro-grafico"),
                                    width=8,
                                ),
                            ]
                        ),
                        # Intervalo para actualizar el espectrómetro
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


# =============================================================================
# Callbacks
# =============================================================================
# Callback para actualizar el espectrómetro usando los valores de los sliders
@app.callback(
    Output("espectrometro-grafico", "figure"),
    [
        Input("inicio-slider", "value"),
        Input("fin-slider", "value"),
        Input("intervalo-espectrometro", "n_intervals"),
    ],
)
def actualizar_espectrometro(inicio, fin, n_intervals):
    dynamic_factor = 10 * np.sin(n_intervals / 10)
    return generar_espectro(inicio, fin, dynamic_factor)


# Callback para actualizar el LiDAR
@app.callback(
    [Output("lidar-grafico", "figure"), Output("informacion-lidar", "children")],
    [Input("intervalo-lidar", "n_intervals")],
)
def actualizar_lidar(n_intervals):
    fig, central_angle, central_distance = generar_grafico_lidar(lidar_data)
    informacion_lidar = [
        html.P(f"Ángulo: {central_angle}°"),
        html.P(f"Distancia: {central_distance} m"),
    ]
    return fig, informacion_lidar


if __name__ == "__main__":
    app.run_server(debug=True)

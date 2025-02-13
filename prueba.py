import dash
from dash import dcc, html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output
import dash.dash_table  # Asegúrate de tener instalada esta dependencia
import plotly.graph_objects as go
import pandas as pd
import json

# Cargar datos del espectrómetro desde el archivo datos.json
with open("datos.json", "r") as file:
    espectrometro_data = json.load(file)

# Cargar datos del LiDAR y la tabla desde el archivo run_1_data.csv
df_lidar = pd.read_csv("run_1_data.csv")
# Filtrar para tomar solo las filas con angle > 0
df_lidar = df_lidar[df_lidar["angle"] > 0]

spectrometer_keys = list(espectrometro_data.keys())

# Inicializar la app con suppress_callback_exceptions para manejar componentes dinámicos
app = dash.Dash(
    __name__, external_stylesheets=[dbc.themes.COSMO], suppress_callback_exceptions=True
)
app.title = "Spectrometer & LiDAR Dashboard"
server = app.server


# =============================================================================
# Función para generar el gráfico del espectrómetro
# =============================================================================
def generar_grafico_espectrometro(valores):
    fig = go.Figure()
    colors = [
        "red",
        "orange",
        "yellow",
        "green",
        "blue",
        "indigo",
        "violet",
        "purple",
        "pink",
        "brown",
        "gray",
        "cyan",
        "magenta",
        "lime",
        "olive",
        "navy",
        "teal",
        "maroon",
    ]
    num_barras = len(valores)
    fig.add_trace(
        go.Bar(
            x=[f"λ{i+1}" for i in range(num_barras)],
            y=valores,
            marker=dict(color=colors[:num_barras]),
            text=[f"{val:.2f}" for val in valores],
            textposition="outside",
            width=0.8,
        )
    )
    fig.update_layout(
        xaxis_title="Longitud de Onda (λ)",
        yaxis_title="Intensidad",
        template="plotly_white",
        showlegend=False,
        bargap=0,
    )
    return fig


# =============================================================================
# Función para generar el gráfico LiDAR
# =============================================================================
def generar_grafico_lidar(dataframe):
    """
    Genera el gráfico LiDAR a partir de un DataFrame con columnas 'angle' y 'distance'.
    Solo se toman los datos con angle > 0 (ya filtrados en df_lidar).
    """
    if dataframe.empty:
        return go.Figure(), 0, 0

    angles = dataframe["angle"].tolist()
    distances = dataframe["dist"].tolist()

    # Para el texto, usamos el último (más reciente) punto del barrido
    current_angle = angles[-1]
    current_distance = distances[-1]

    # Guardamos el primer y último para dibujar líneas desde el centro
    initial_angle = angles[0]
    initial_distance = distances[0]

    fig = go.Figure()

    # Trazado principal (scatter polar)
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

    # Línea desde el centro al primer punto (opcional)
    fig.add_trace(
        go.Scatterpolar(
            theta=[0, initial_angle],
            r=[0, initial_distance],
            mode="lines",
            name="Línea Inicial",
            line=dict(color="blue", width=2),
        )
    )

    # Línea desde el centro al último punto (más reciente)
    fig.add_trace(
        go.Scatterpolar(
            theta=[0, current_angle],
            r=[0, current_distance],
            mode="lines",
            name="Línea Actual",
            line=dict(color="green", width=2),
        )
    )

    # Área roja entre la línea inicial y la línea actual
    fig.add_trace(
        go.Scatterpolar(
            theta=[0, initial_angle, current_angle, 0],
            r=[0, initial_distance, current_distance, 0],
            mode="lines",
            fill="toself",
            fillcolor="rgba(255, 0, 0, 0.3)",
            line=dict(color="rgba(255, 0, 0, 0)"),
            name="Área Roja",
        )
    )

    fig.update_layout(
        title="LiDAR - Visualización Polar (2D)",
        polar=dict(
            angularaxis=dict(
                tickmode="array",
                tickvals=[0, 45, 90, 135, 180, 225, 270, 315],
                ticktext=["0", "45", "90", "135", "180", "225", "270", "315"],
                showline=True,
                linewidth=1,
                linecolor="black",
            ),
            radialaxis=dict(
                tickmode="linear",
                tick0=0,
                dtick=2,
                range=[0, 14],
                showline=True,
                gridcolor="gray",
                linecolor="black",
            ),
        ),
        template="plotly_white",
    )
    return fig, current_angle, current_distance


# =============================================================================
# Layout de la aplicación
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
            dbc.Col(
                dcc.Tabs(
                    id="tabs",
                    value="tab-1",
                    children=[
                        dcc.Tab(label="Cámara y Espectrómetro", value="tab-1"),
                        dcc.Tab(label="LiDAR y Tabla", value="tab-2"),
                    ],
                ),
                width=12,
            )
        ),
        dbc.Row(
            dbc.Col(
                html.Div(id="tabs-content"),
                width=12,
            )
        ),
    ],
    fluid=True,
)


# =============================================================================
# Callback para cambiar el contenido de las pestañas
# =============================================================================
@app.callback(Output("tabs-content", "children"), [Input("tabs", "value")])
def render_content(tab):
    if tab == "tab-1":
        # Contenido de la pestaña 1: Cámara y Espectrómetro
        return html.Div(
            [
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
                                            src="",
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
                        # Columna del espectrómetro
                        dbc.Col(
                            [
                                html.H3("Espectrómetro", className="text-center"),
                                html.H4(
                                    id="titulo-espectrometro", className="text-center"
                                ),
                                dcc.Graph(id="espectrometro-grafico"),
                                dcc.Interval(
                                    id="intervalo-espectrometro",
                                    interval=2000,  # 2 segundos
                                    n_intervals=0,
                                ),
                            ],
                            width=6,
                        ),
                    ]
                ),
            ]
        )
    elif tab == "tab-2":
        # Contenido de la pestaña 2: LiDAR y Tabla
        return html.Div(
            [
                dbc.Row(
                    [
                        dbc.Col(
                            [
                                html.H3(
                                    "LiDAR - Tarea C", className="text-center mt-4"
                                ),
                                dcc.Graph(id="lidar-grafico"),
                                html.Div(
                                    id="informacion-lidar",
                                    children=[
                                        html.P("Ángulo: 0°"),
                                        html.P("Distancia: 0 m"),
                                    ],
                                    style={"fontSize": "20px", "fontWeight": "bold"},
                                ),
                                dcc.Interval(
                                    id="intervalo-lidar",
                                    interval=500,  # Actualiza cada 0.5 segundos
                                    n_intervals=0,
                                ),
                            ],
                            width=12,
                        ),
                    ]
                ),
                dbc.Row(
                    [
                        dbc.Col(
                            [
                                html.H3("Tabla de Datos", className="text-center mt-4"),
                                dash.dash_table.DataTable(
                                    id="tabla-datos",
                                    columns=[
                                        {"name": col, "id": col}
                                        for col in df_lidar.columns
                                    ],
                                    data=df_lidar.to_dict("records"),
                                    style_table={"overflowX": "auto"},
                                ),
                            ],
                            width=12,
                        ),
                    ]
                ),
            ]
        )


# =============================================================================
# Callback para actualizar el espectrómetro
# =============================================================================
@app.callback(
    [
        Output("espectrometro-grafico", "figure"),
        Output("titulo-espectrometro", "children"),
    ],
    [Input("intervalo-espectrometro", "n_intervals")],
)
def actualizar_espectrometro(n_intervals):
    key_index = n_intervals % len(spectrometer_keys)
    key = spectrometer_keys[key_index]
    valores = espectrometro_data[key]
    fig = generar_grafico_espectrometro(valores)
    titulo = f"Categoría: {key.replace('_', ' ').capitalize()}"
    return fig, titulo


# =============================================================================
# Callback para actualizar el LiDAR
# =============================================================================
@app.callback(
    [Output("lidar-grafico", "figure"), Output("informacion-lidar", "children")],
    [Input("intervalo-lidar", "n_intervals")],
)
def actualizar_lidar(n_intervals):
    num_datos = len(df_lidar)
    # Simula un barrido incremental, avanzando 2 puntos cada intervalo
    indice_final = min((n_intervals + 1) * 2, num_datos)
    lidar_data = df_lidar.iloc[:indice_final].copy()

    fig, current_angle, current_distance = generar_grafico_lidar(lidar_data)
    info = [
        html.P(f"Ángulo: {current_angle}°"),
        html.P(f"Distancia: {current_distance} m"),
    ]
    return fig, info


if __name__ == "__main__":
    app.run_server(debug=True)

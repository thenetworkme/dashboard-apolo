import dash
from dash import dcc, html
import plotly.graph_objects as go
from dash.dependencies import Input, Output
import numpy as np
import dash_bootstrap_components as dbc

# Inicializar la app con un tema Bootstrap
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.COSMO])
app.title = "Dashboard"


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


def generar_datos_lidar():
    angles = np.linspace(0, 360, 360)
    distances = 1 + 2 * np.sin(np.radians(angles)) ** 2
    distances += 0.1 * np.random.uniform(-1, 1, size=360)

    fig = go.Figure()
    fig.add_trace(
        go.Scatterpolar(
            r=distances,
            theta=angles,
            mode="lines+markers",
            name="LIDAR Data",
            line=dict(color="blue", width=2),
            marker=dict(color="black", size=4),
        )
    )
    fig.update_layout(
        title="LIDAR - Patrón de Radiación Simulado",
        polar=dict(
            angularaxis=dict(direction="clockwise", rotation=90, showline=True),
            radialaxis=dict(title="Distancia", range=[0, 3], showline=True),
        ),
        template="plotly_white",
    )
    return fig


app.layout = dbc.Container(
    [
        dcc.Location(id="url", refresh=False),
        dbc.NavbarSimple(
            children=[
                dbc.NavLink("Espectro de Colores", href="/", active="exact"),
                dbc.NavLink("Task C - LIDAR", href="/task-c", active="exact"),
            ],
            brand="Dashboard",
            color="primary",
            dark=True,
        ),
        html.Div(id="page-content"),
    ],
    fluid=True,
)


layout_espectro = dbc.Container(
    [
        dbc.Row(
            dbc.Col(
                html.H1("Espectro de Colores", className="text-center mb-4"),
                width=12,
            )
        ),
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
                dbc.Col(dcc.Graph(id="espectro-grafico"), width=8),
            ]
        ),
        dcc.Interval(
            id="intervalo-actualizacion",
            interval=1000,
            n_intervals=0,
        ),
    ],
    fluid=True,
)


layout_task_c = dbc.Container(
    [
        dbc.Row(
            dbc.Col(
                html.H1("Task C - LIDAR", className="text-center mb-4"),
                width=12,
            )
        ),
        dbc.Row(dbc.Col(dcc.Graph(id="lidar-grafico"), width=12)),
        dcc.Interval(
            id="lidar-intervalo",
            interval=2000,
            n_intervals=0,
        ),
    ],
    fluid=True,
)


@app.callback(
    Output("espectro-grafico", "figure"),
    [
        Input("inicio-slider", "value"),
        Input("fin-slider", "value"),
        Input("intervalo-actualizacion", "n_intervals"),
    ],
)
def actualizar_espectro(inicio, fin, n_intervals):
    dynamic_factor = 10 * np.sin(n_intervals / 10)
    return generar_espectro(inicio, fin, dynamic_factor)


@app.callback(
    Output("lidar-grafico", "figure"),
    [Input("lidar-intervalo", "n_intervals")],
)
def actualizar_lidar(n_intervals):
    return generar_datos_lidar()


@app.callback(
    Output("page-content", "children"),
    [Input("url", "pathname")],
)
def mostrar_pagina(pathname):
    if pathname == "/task-c":
        return layout_task_c
    else:
        return layout_espectro


if __name__ == "__main__":
    app.run_server(debug=True)

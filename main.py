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
    fig = go.Figure()
    fig.add_trace(
        go.Scatter3d(
            x=[1, 2, 3],
            y=[4, 5, 6],
            z=[7, 8, 9],
            mode="markers",
            marker=dict(size=5, color=[7, 8, 9], colorscale="Viridis"),
        )
    )
    fig.update_layout(
        title="LiDAR - Tarea C",
        scene=dict(
            xaxis_title="Eje X",
            yaxis_title="Eje Y",
            zaxis_title="Eje Z",
        ),
        template="plotly_white",
    )
    return fig


layout_espectrometro = dbc.Container(
    [
        dbc.Row(
            dbc.Col(
                html.H1("Dashboard del Espectrómetro", className="text-center mb-4"),
                width=12,
            )
        ),
        dbc.Row(dbc.Col(dcc.Graph(id="espectrometro-grafico"), width=12)),
        dcc.Interval(
            id="intervalo-espectrometro",
            interval=4000,
            n_intervals=0,
        ),
    ],
    fluid=True,
)


layout_lidar = dbc.Container(
    [
        dbc.Row(
            dbc.Col(
                html.H1("Dashboard del LiDAR - Tarea C", className="text-center mb-4"),
                width=12,
            )
        ),
        dbc.Row(
            dbc.Col(
                dcc.Graph(id="lidar-grafico", figure=generar_grafico_lidar()), width=12
            )
        ),
    ],
    fluid=True,
)


app.layout = dbc.Container(
    [
        dcc.Location(id="url", refresh=False),
        dbc.NavbarSimple(
            children=[
                dbc.NavLink("Espectrómetro", href="/", active="exact"),
                dbc.NavLink("LiDAR - Tarea C", href="/lidar", active="exact"),
            ],
            brand="Dashboard",
            color="primary",
            dark=True,
        ),
        html.Div(id="page-content"),
    ],
    fluid=True,
)


@app.callback(
    Output("espectrometro-grafico", "figure"),
    [Input("intervalo-espectrometro", "n_intervals")],
)
def actualizar_espectrometro(n_intervals):
    # Aqui se selecciona la categoría basada en el número de intervalos
    category_index = n_intervals % len(categories)
    category = categories[category_index]
    values = data[category]
    return generar_grafico_espectrometro(category, values)


# Callback para cambiar entre layouts Lidar y espectrometro
@app.callback(
    Output("page-content", "children"),
    [Input("url", "pathname")],
)
def mostrar_pagina(pathname):
    if pathname == "/lidar":
        return layout_lidar
    else:
        return layout_espectrometro


if __name__ == "__main__":
    app.run_server(debug=True)

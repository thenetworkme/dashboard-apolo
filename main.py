import tkinter as tk
from tkinter import ttk
from ttkthemes import ThemedTk
import plotly.graph_objects as go
import numpy as np
import plotly.io as pio
from PIL import Image, ImageTk
import io

# Datos iniciales
task_a_data = np.random.rand(18)  # Intensidades para Task A (1x18)
wavelengths = np.linspace(380, 780, 18)  # Longitudes de onda en nm (380 a 780 nm)
task_c_data = np.random.rand(180)  # Distancias para Task C (1x180)


# Función para actualizar los datos y graficarlos para Task A
def actualizar_task_a():
    global task_a_data
    task_a_data = np.random.rand(18)  # Simulación de datos en tiempo real

    # Crear gráfico interactivo para Task A (Espectro de Intensidades)
    fig_a = go.Figure()

    fig_a.add_trace(
        go.Scatter(
            x=wavelengths,
            y=task_a_data,
            mode="lines+markers",
            line=dict(color=task_a_data, colorscale="Jet", width=4),
            marker=dict(size=10, color=task_a_data, colorscale="Jet", showscale=True),
        )
    )

    fig_a.update_layout(
        title="Espectro de Intensidades (Task A)",
        xaxis_title="Longitud de Onda (nm)",
        yaxis_title="Intensidad",
        template="plotly_dark",
        coloraxis_colorbar=dict(title="Intensidad"),
        showlegend=False,
    )

    # Convertir la figura a una imagen PNG
    img_data = pio.to_image(fig_a, format="png")
    img = Image.open(io.BytesIO(img_data))

    # Mostrar la imagen en Tkinter
    img_tk = ImageTk.PhotoImage(img)
    label_img_a.config(image=img_tk)
    label_img_a.image = img_tk  # Mantener una referencia a la imagen


# Función para actualizar los datos y graficarlos para Task C
def actualizar_task_c():
    global task_c_data
    task_c_data = np.random.rand(180)  # Simulación de datos en tiempo real

    # Crear gráfico interactivo para Task C (Distancias por Ángulo)
    fig_c = go.Figure()

    fig_c.add_trace(
        go.Scatter(
            x=np.arange(0, 180),
            y=task_c_data,
            mode="lines+markers",
            marker=dict(color="green", size=8),
        )
    )

    fig_c.update_layout(
        title="Distancias por Ángulo (Task C)",
        xaxis_title="Ángulo (°)",
        yaxis_title="Distancia",
        template="plotly_dark",
        showlegend=False,
    )

    # Convertir la figura a una imagen PNG
    img_data = pio.to_image(fig_c, format="png")
    img = Image.open(io.BytesIO(img_data))

    # Mostrar la imagen en Tkinter
    img_tk = ImageTk.PhotoImage(img)
    label_img_c.config(image=img_tk)
    label_img_c.image = img_tk  # Mantener una referencia a la imagen


# Función para actualizar todos los gráficos en intervalos
def actualizar_todos():
    actualizar_task_a()
    actualizar_task_c()
    root.after(2000, actualizar_todos)  # Actualizar cada 2 segundos


# Crear la ventana principal con ttkthemes para un diseño más bonito
root = ThemedTk(theme="arc")
root.title("Dashboard - Task A y Task C")
root.geometry("1000x700")

# Pestañas
notebook = ttk.Notebook(root)
notebook.pack(fill="both", expand=True)

# Pestaña Task A
frame_task_a = ttk.Frame(notebook)
notebook.add(frame_task_a, text="Task A")

# Pestaña Task C
frame_task_c = ttk.Frame(notebook)
notebook.add(frame_task_c, text="Task C")

# --- Contenido de Task A ---
title_task_a = ttk.Label(
    frame_task_a,
    text="Espectro de Intensidades (Task A)",
    font=("Helvetica", 16, "bold"),
)
title_task_a.pack(pady=10)

frame_graph_a = ttk.LabelFrame(frame_task_a, text="Gráfico")
frame_graph_a.pack(fill="both", expand=True, padx=10, pady=10)

# --- Contenido de Task C ---
title_task_c = ttk.Label(
    frame_task_c, text="Distancias por Ángulo (Task C)", font=("Helvetica", 16, "bold")
)
title_task_c.pack(pady=10)

frame_graph_c = ttk.LabelFrame(frame_task_c, text="Gráfico")
frame_graph_c.pack(fill="both", expand=True, padx=10, pady=10)

# Labels para mostrar las imágenes generadas
label_img_a = ttk.Label(frame_graph_a)
label_img_a.pack(fill="both", expand=True)

label_img_c = ttk.Label(frame_graph_c)
label_img_c.pack(fill="both", expand=True)

# Iniciar la actualización en tiempo real
root.after(2000, actualizar_todos)  # Actualizar cada 2 segundos

# Iniciar el loop principal
root.mainloop()

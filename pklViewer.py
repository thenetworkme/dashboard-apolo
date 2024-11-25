import pickle
import json
import numpy as np

# Cargar el archivo .pkl
with open("averages.pkl", "rb") as file:
    data = pickle.load(file)

# Convertir los arrays de numpy a listas
converted_data = {}
for key, value in data:
    if isinstance(value, np.ndarray):
        converted_data[key] = value.tolist()
    else:
        converted_data[key] = value

# Guardar los datos en un archivo .json
with open("tu_archivo.json", "w") as file:
    json.dump(converted_data, file, indent=4)

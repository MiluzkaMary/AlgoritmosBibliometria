import json
import matplotlib.pyplot as plt
import os

# Construir la ruta al archivo JSON en la misma carpeta del script
archivo_json = os.path.join(os.getcwd(), "Diagramas.json")

# Leer el archivo JSON
with open(archivo_json, 'r', encoding='utf-8') as f:
    data = json.load(f)

# Crear una gráfica de barras para cada atributo
for atributo, tiempos in data.items():
    # Extraer nombres de algoritmos y sus tiempos
    algoritmos = [item["algoritmo"] for item in tiempos]
    tiempos_ejecucion = [item["tiempo"] for item in tiempos]

    # Crear la gráfica
    plt.figure(figsize=(8, 5))
    bars = plt.bar(algoritmos, tiempos_ejecucion, color='skyblue')

    # Agregar etiquetas con los valores sobre cada barra
    for bar in bars:
        altura = bar.get_height()
        plt.text(bar.get_x() + bar.get_width() / 2, altura, f"{altura:.1f}", 
                 ha="center", va="bottom", fontsize=10, fontweight="bold", color="black")

    # Personalizar la gráfica
    plt.xlabel("Algoritmos de Ordenamiento")
    plt.ylabel("Tiempo de Ejecución (ms)")
    plt.title(f"Tiempos de Ordenamiento - {atributo.capitalize()}")
    plt.xticks(rotation=45)
    plt.grid(axis="y", linestyle="--", alpha=0.7)


    # Personalizar la gráfica
    plt.xlabel("Algoritmos de Ordenamiento")
    plt.ylabel("Tiempo de Ejecución (ms)")
    plt.title(f"Tiempos de Ordenamiento - {atributo.capitalize()}")
    plt.xticks(rotation=45)
    plt.grid(axis="y", linestyle="--", alpha=0.7)

# Ajustar los márgenes automáticamente
    plt.tight_layout()
    # Mostrar la gráfica
    plt.show()
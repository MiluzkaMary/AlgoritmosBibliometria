import pandas as pd
import sqlite3
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import os

# Conectar a la base de datos
db_path = '../bibliometria.db'  
conexion = sqlite3.connect(db_path)

# Cargar la tabla de frecuencias
query = '''
SELECT categoria, variable, SUM(frecuencia) AS total_frecuencia
FROM frecuencia_variables
GROUP BY categoria, variable
ORDER BY categoria, total_frecuencia DESC;
'''
df_frecuencia = pd.read_sql_query(query, conexion)

# Cerrar la conexión
conexion.close()

# Crear una carpeta para guardar las nubes de palabras
output_dir = "nubes_palabras"
os.makedirs(output_dir, exist_ok=True)

# Generar una nube de palabras para todas las categorías combinadas
frecuencias_totales = dict(zip(df_frecuencia['variable'], df_frecuencia['total_frecuencia']))
wordcloud_total = WordCloud(
    width=1920, 
    height=1080,
    background_color='black',
    colormap='Set3',
    scale=2,
    max_words=120,
    margin=0  
).generate_from_frequencies(frecuencias_totales)

# Guardar la nube de palabras para todas las categorías
plt.figure(figsize=(12, 6), facecolor='black')  
plt.imshow(wordcloud_total, interpolation='bilinear')
plt.axis('off')
plt.margins(0, 0) 
plt.gca().set_position([0, 0, 1, 1])  
plt.savefig(
    os.path.join(output_dir, "nube_todas_categorias.png"),
    dpi=200,  
    bbox_inches='tight',  
    pad_inches=0, 
    facecolor='black'  
)

# Generar nubes de palabras por categoría
categorias = df_frecuencia['categoria'].unique()
for categoria in categorias:
    # Filtrar las frecuencias para la categoría actual
    df_categoria = df_frecuencia[df_frecuencia['categoria'] == categoria]
    frecuencias_categoria = dict(zip(df_categoria['variable'], df_categoria['total_frecuencia']))
    
    # Generar la nube de palabras para la categoría
    wordcloud_categoria = WordCloud(
        width=1920,  # Tamaño original
        height=1080,
        background_color='black',
        colormap='Set3',
        scale=2,
        max_words=120,
        margin=0  # Eliminar márgenes internos de la nube
    ).generate_from_frequencies(frecuencias_categoria)
    
    # Guardar la nube de palabras para la categoría
    plt.figure(figsize=(12, 6), facecolor='black') 
    plt.imshow(wordcloud_categoria, interpolation='bilinear')
    plt.axis('off')
    plt.margins(0, 0)  
    plt.gca().set_position([0, 0, 1, 1])  
    plt.savefig(
        os.path.join(output_dir, f"nube_{categoria.replace(' ', '_').lower()}.png"),
        dpi=200,  
        bbox_inches='tight',  
        pad_inches=0,  
        facecolor='black'  
    )
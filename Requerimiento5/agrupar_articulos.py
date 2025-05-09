from sklearn.cluster import DBSCAN # type: ignore
import os
import pandas as pd
import numpy as np

#Obtener la ruta del directorio actual (donde está este script)
current_dir = os.path.dirname(__file__)

# contruir la ruta relativa para losarchivos
agrupar_csv_path = os.path.join(current_dir, "matriz_similitud_coseno.csv")
agrupar_csvAbstracts_path = os.path.join(current_dir, "abstracts.csv")

# Cargar la matriz de similitud desde el archivo CSV
cosine_sim_df = pd.read_csv(agrupar_csv_path, index_col=0)
cosine_sim = cosine_sim_df.values  # Convertir a matriz NumPy

# Convertir la similitud de coseno en una matriz de distancias
distance_matrix = np.maximum(0, 1 - cosine_sim)  # Asegurar que no haya valores negativos

# Cargar los abstracts desde el archivo CSV
abstracts_df = pd.read_csv(agrupar_csvAbstracts_path)
abstracts = abstracts_df['Abstract'].tolist()

# Aplicar DBSCAN para agrupar artículos
dbscan = DBSCAN(metric='precomputed', eps=0.5, min_samples=2)  # Ajusta 'eps' según la similitud deseada
labels = dbscan.fit_predict(distance_matrix)  # 1 - cosine_sim convierte similitud en distancia

# Mostrar los grupos
grouped_articles = pd.DataFrame({'Abstract': abstracts, 'Grupo': labels})
print("\nArtículos agrupados por similitud textual:")
print(grouped_articles)

# Guardar los resultados en un archivo CSV
grouped_articles.to_csv('articulos_agrupados.csv', index=False)
print("\nResultados guardados en 'articulos_agrupados.csv'.")
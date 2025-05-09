import os
import pandas as pd
from sklearn.cluster import DBSCAN # type: ignore

#Obtener la ruta del directorio actual (donde está este script)
current_dir = os.path.dirname(__file__)

# contruir la ruta relativa para losarchivos
clustering_csv_path = os.path.join(current_dir, "embeddings_abstracts.csv")

# Cargar los embeddings y abstracts desde el archivo CSV
embeddings_df = pd.read_csv(clustering_csv_path)
abstracts = embeddings_df['abstract'].tolist()  # Extraer los abstracts
embeddings = embeddings_df.drop(columns=['abstract']).values  # Extraer los embeddings como matriz

# Aplicar DBSCAN para agrupar los embeddings
clustering_model = DBSCAN(eps=0.5, min_samples=2, metric='cosine')  # Ajusta 'eps' según sea necesario
clusters = clustering_model.fit_predict(embeddings)

# Crear un DataFrame para mostrar los resultados
results_df = pd.DataFrame({
    'Abstract': abstracts,
    'Cluster': clusters
})

# Guardar los resultados en un archivo CSV
results_df.to_csv('agrupacion_articulos_embeddings.csv', index=False)

# Mostrar los resultados
print("Agrupación completada. Resultados:")
print(results_df)
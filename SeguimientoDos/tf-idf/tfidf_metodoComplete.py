import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.cluster.hierarchy import linkage, dendrogram
from scipy.spatial.distance import squareform

#Obtener la ruta del directorio actual (donde está este script)
current_dir = os.path.dirname(__file__)

# contruir la ruta relativa para losarchivos
tfidf_csv_path = os.path.join(current_dir, "../../Requerimiento5/matriz_similitud_coseno.csv")
tfidf_csvAbstracts_path = os.path.join(current_dir, "../../Requerimiento5/abstracts.csv")
print(tfidf_csv_path)
print(tfidf_csvAbstracts_path)

# Cargar la matriz de similitud de coseno
cosine_sim_df = pd.read_csv(tfidf_csv_path, index_col=0)
cosine_sim = cosine_sim_df.values

# Convertir similitud a distancia
distance_matrix = np.maximum(0, 1 - cosine_sim)

# Cargar los abstracts
abstracts_df = pd.read_csv(tfidf_csvAbstracts_path)
abstracts = abstracts_df['Abstract'].tolist()

# Usar los primeros 20
short_abstracts = [a[:30] + "..." for a in abstracts[:20]]
distance_short = distance_matrix[:20, :20]

# Asegurar que la diagonal sea cero
np.fill_diagonal(distance_short, 0)

# Convertir a forma condensada
condensed_dist = squareform(distance_short)

# Agrupamiento jerárquico con linkage complete
linked_complete = linkage(condensed_dist, method='complete')

# Crear dendrograma
plt.figure(figsize=(15, 8))
dendrogram(linked_complete, labels=short_abstracts, orientation='top', leaf_rotation=90)
plt.title("Dendrograma - TF-IDF + Linkage 'complete'")
plt.tight_layout()
plt.savefig("dendrograma_tfidf_complete.png")
plt.show()

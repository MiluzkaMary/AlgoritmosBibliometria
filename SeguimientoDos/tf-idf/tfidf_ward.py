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

# Leer matriz de similitud y convertirla en matriz de distancia
cosine_sim_df = pd.read_csv(tfidf_csv_path, index_col=0)
cosine_sim = cosine_sim_df.values
distance_matrix = np.maximum(0, 1 - cosine_sim)

# Leer abstracts
abstracts_df = pd.read_csv(tfidf_csvAbstracts_path)
abstracts = abstracts_df['Abstract'].tolist()

# Usar solo los primeros 20 para visualizar
short_abstracts = [a[:30] + "..." for a in abstracts[:20]]
distance_short = distance_matrix[:20, :20]

# Asegurar que la diagonal sea cero
np.fill_diagonal(distance_short, 0)

# Convertir a forma condensada
condensed_dist = squareform(distance_short)

# Agrupamiento jerárquico con método 'ward'
linked_ward = linkage(condensed_dist, method='ward')

# Graficar dendrograma
plt.figure(figsize=(12, 6))
dendrogram(linked_ward, labels=short_abstracts, orientation='top', leaf_rotation=90)
plt.title("Dendrograma TF-IDF - Linkage 'ward'")
plt.tight_layout()
plt.savefig("dendrograma_tfidf_ward.png")
plt.show()

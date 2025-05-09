import os
import pandas as pd
import matplotlib.pyplot as plt
from scipy.cluster.hierarchy import linkage, dendrogram

#Obtener la ruta del directorio actual (donde está este script)
current_dir = os.path.dirname(__file__)

# contruir la ruta relativa para losarchivos
embeddings_csv_path = os.path.join(current_dir, "../../Requerimiento5/embeddings_abstracts.csv")

# Leer embeddings desde el CSV
df = pd.read_csv(embeddings_csv_path)
abstracts = df['abstract'].tolist()
embeddings = df.drop(columns=['abstract']).values

# Usar solo los primeros 20 abstracts para visualización
short_abstracts = [a[:30] + "..." for a in abstracts[:20]]
subset_embeddings = embeddings[:20]

# Clustering con método 'complete'
linked_complete = linkage(subset_embeddings, method='complete')

# Graficar y guardar dendrograma
plt.figure(figsize=(12, 6))
dendrogram(linked_complete, labels=short_abstracts, orientation='top', leaf_rotation=90)
plt.title("Dendrograma - Linkage 'complete'")
plt.tight_layout()
plt.savefig("dendrograma_complete_labels.png")
plt.show()

import os
import pandas as pd
import matplotlib.pyplot as plt
from scipy.cluster.hierarchy import linkage, dendrogram

#Obtener la ruta del directorio actual (donde está este script)
current_dir = os.path.dirname(__file__)

# contruir la ruta relativa para losarchivos
embeddings_csv_path = os.path.join(current_dir, "../../Requerimiento5/embeddings_abstracts.csv")
print(embeddings_csv_path)

# Leer embeddings desde el CSV
df = pd.read_csv(embeddings_csv_path)
abstracts = df['abstract'].tolist()
embeddings = df.drop(columns=['abstract']).values

# Usamos solo los primeros 20 para una visualización legible
subset_embeddings = embeddings[:20]
subset_abstracts = abstracts[:20]

# Reducir el tamaño de cada abstarct para visualización
short_abstracts = [a[:30] + '...' if len(a) > 30 else a for a in subset_abstracts]

# Generar el linkage usando el método 'ward'
linked_short = linkage(subset_embeddings, method='ward')

# Dendrograma con etiquetas de abstracts resumidas
plt.figure(figsize=(18, 6))
dendrogram(linked_short, labels=short_abstracts, orientation='top', leaf_rotation=90)
plt.title("Dendrograma con abstracts 'ward'")
plt.tight_layout()
plt.savefig("dendrograma_con_abstracts_ward.png", dpi=300)
plt.close()

# Dendrograma con índices númericos
plt.figure(figsize=(18, 6))
dendrogram(linked_short, orientation='top', leaf_rotation=90)
plt.title("Dendrograma con índices 'ward")
plt.tight_layout()
plt.savefig("dendrograma_con_indices_ward.png", dpi=300)
plt.close()

print("Se han guardado correctamente ambos dendrogramas:")

from sentence_transformers import SentenceTransformer, util
import os
import pandas as pd
import sqlite3

#Obtener la ruta del directorio actual (donde está este script)
current_dir = os.path.dirname(__file__)

# contruir la ruta relativa para losarchivos
embeddings_bd_path = os.path.join(current_dir, "../bibliometria.db")
print(embeddings_bd_path)

# Conectar a la base de datos SQLite
db_path = embeddings_bd_path
conn = sqlite3.connect(db_path)

# Consultar los abstracts desde la base de datos
query = "SELECT abstract FROM productos WHERE abstract IS NOT NULL;"
cursor = conn.execute(query)
abstracts = [row[0] for row in cursor.fetchall()] # Extraer los abstracts como una lista

# Cerrar la conexión a la base de datos
conn.close()

# Verificar si hay abstracts disponibles
if not abstracts:
    print("No se encontraron abstracts en la base de datos.")
    exit()

# Modelo preentrenado
model = SentenceTransformer('all-MiniLM-L6-v2')


# Generar embeddings para los abstracts
embeddings = model.encode(abstracts, convert_to_tensor=False)

# Calcular la similitud de coseno
cosine_sim = util.cos_sim(embeddings, embeddings)

# Mostrar la matriz de similitud
cosine_sim_df = pd.DataFrame(cosine_sim.numpy(), columns=[f"Doc{i+1}" for i in range(len(abstracts))], index=[f"Doc{i+1}" for i in range(len(abstracts))])
print(cosine_sim_df)

# Guardar los embeddings y abstracts en un archivo CSV
embeddings_df = pd.DataFrame(embeddings)
embeddings_df['abstract'] = abstracts # Agregar la columna de abstracts
embeddings_df.to_csv('embeddings_abstracts.csv', index=False)
print("Embeddings y abstracts guardados en 'embeddings_abstracts.csv'")
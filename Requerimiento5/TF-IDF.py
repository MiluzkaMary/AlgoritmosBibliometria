from sklearn.feature_extraction.text import TfidfVectorizer # type: ignore
from sklearn.metrics.pairwise import cosine_similarity  # type: ignore
import os
import pandas as pd
import sqlite3

#Obtener la ruta del directorio actual (donde está este script)
current_dir = os.path.dirname(__file__)

# contruir la ruta relativa para losarchivos
tfidf_bd_path = os.path.join(current_dir, "../bibliometria.db")

# Conectar a la base de datos
db_path = tfidf_bd_path
conn = sqlite3.connect(db_path)

# Consultar los abstracts de la base de datos
query = "SELECT abstract FROM productos WHERE abstract IS NOT NULL;"
cursor = conn.execute(query)
abstracts = [row[0] for row in cursor.fetchall()] # #xtraer los abstracts como una lista

# Cerrar la conexión a la base de datos
conn.close()

# Verificar si se obtuvieron abstracts
if not abstracts:
    print("No se encontraron abstracts en la base de datos.")
    exit()

# Convertir los abstracts a vectores TF-IDF
vectorizer = TfidfVectorizer()
tfidf_matrix = vectorizer.fit_transform(abstracts)

# Calcular la similitud de coseno
cosine_sim = cosine_similarity(tfidf_matrix)

# Mostrar la matriz de similitud
cosine_sim_df = pd.DataFrame(cosine_sim, columns=[f"Doc{i+1}" for i in range(len(abstracts))], index=[f"Doc{i+1}" for i in range(len(abstracts))])
cosine_sim_df.to_csv("matriz_similitud_coseno.csv", index=True)  # Guardar la matriz en un archivo CSV
print("Matriz de similitud de coseno (TF-IDF):")
print(cosine_sim_df)

# Guardar los abstracts en un archivo CSV para referencia
abstracts_df = pd.DataFrame({'Abstract': abstracts})
abstracts_df.to_csv("abstracts.csv", index=False)  # Guardar los abstracts en un archivo CSV

print("Matriz de similitud y abstracts guardados en archivos CSV.")
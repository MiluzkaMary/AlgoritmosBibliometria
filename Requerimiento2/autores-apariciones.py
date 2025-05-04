import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Conectar a la base de datos
db_path = '../bibliometria.db'
conn = sqlite3.connect(db_path)

# Consultar los 15 autores más citados por cantidad de artículos, excluyendo "No encontrado"
query = """
SELECT primer_autor, COUNT(*) as cantidad
FROM productos
WHERE primer_autor != 'No encontrado'
GROUP BY primer_autor
ORDER BY cantidad DESC
LIMIT 15;
"""
data = conn.execute(query).fetchall()

# Cerrar conexión
conn.close()

# Convertir los datos a un DataFrame
df = pd.DataFrame(data, columns=['primer_autor', 'cantidad'])

# Generar la gráfica
plt.figure(figsize=(10, 6))
ax = sns.barplot(data=df, x='cantidad', y='primer_autor', palette='flare')

# Agregar los valores encima de las barras
for p in ax.patches:
    width = p.get_width()  # Obtener el ancho de la barra (cantidad)
    if width > 0:  # Solo mostrar valores si la cantidad es mayor a 0
        ax.annotate(f'{int(width)}',  # El valor a mostrar
                    (p.get_x() + width, p.get_y() + p.get_height() / 2),  # Posición del texto
                    ha='left', va='center', fontsize=10, color='black')

# Configurar la gráfica
plt.title("15 Autores Más Citados (por Cantidad de Artículos)")
plt.xlabel("Cantidad de Artículos")
plt.ylabel("Primer Autor")
plt.tight_layout()

# Guardar la gráfica como archivo PNG
plt.savefig("autores_mas_citados.png")
print("Gráfica guardada: autores_mas_citados.png")

# Mostrar la gráfica
plt.show()
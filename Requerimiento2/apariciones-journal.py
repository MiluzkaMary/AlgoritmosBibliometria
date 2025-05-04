import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Conectar a la base de datos
db_path = '../bibliometria.db'  # Ruta a la base de datos
conn = sqlite3.connect(db_path)

# Consultar la cantidad de productos por journal
query = """
SELECT journal, COUNT(*) as cantidad
FROM productos
WHERE journal != 'No encontrado'
GROUP BY journal
ORDER BY cantidad DESC
LIMIT 15;  -- Mostrar solo los 15 journals con más productos
"""
data = conn.execute(query).fetchall()

# Cerrar conexión
conn.close()

# Convertir los datos a un DataFrame
df = pd.DataFrame(data, columns=['journal', 'cantidad'])

# Generar la gráfica
plt.figure(figsize=(10, 6))
ax = sns.barplot(data=df, x='cantidad', y='journal', palette='flare')

# Agregar los valores encima de las barras
for p in ax.patches:
    width = p.get_width()  # Obtener la altura de la barra (cantidad)
    if width > 0:  # Solo mostrar valores si la cantidad es mayor a 0
        ax.annotate(f'{int(width)}',  # El valor a mostrar
                    (p.get_x() + width + 0.1, p.get_y() + p.get_height() / 2),  # Posición del texto
                    ha='left', va='center', fontsize=10, color='black')

# Configurar la gráfica
plt.title("15 Journals con más Apariciones")
plt.xlabel("Cantidad de Productos")
plt.ylabel("Journal")
plt.tight_layout()

# Guardar la gráfica como archivo PNG
plt.savefig("apariciones_por_journal.png")
print("Gráfica guardada: apariciones_por_journal.png")

# Mostrar la gráfica
plt.show()
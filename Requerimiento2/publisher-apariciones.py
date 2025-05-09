import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Conectar a la base de datos
db_path = '../bibliometria.db'  # Ruta a la base de datos
conn = sqlite3.connect(db_path)

# Consultar la cantidad de productos por base de datos
query = """
SELECT base_datos, COUNT(*) as cantidad
FROM productos
GROUP BY base_datos
ORDER BY cantidad DESC;
"""
data = conn.execute(query).fetchall()

# Cerrar conexión
conn.close()

# Convertir los datos a un DataFrame
df = pd.DataFrame(data, columns=['base_datos', 'cantidad'])

# Generar la gráfica
plt.figure(figsize=(8, 6))
ax = sns.barplot(data=df, x='base_datos', y='cantidad', palette='flare')

# Agregar los valores encima de las barras
for p in ax.patches:
    height = p.get_height()  # Obtener la altura de la barra (cantidad)
    if height > 0:  # Solo mostrar valores si la cantidad es mayor a 0
        ax.annotate(f'{int(height)}',  # El valor a mostrar
                    (p.get_x() + p.get_width() / 2., height),  # Posición del texto
                    ha='center', va='bottom', fontsize=10, color='black')

# Configurar la gráfica
plt.title("Cantidad de Productos por Publisher")
plt.xlabel("Publisher")
plt.ylabel("Cantidad de Productos")
plt.tight_layout()

# Guardar la gráfica como archivo PNG
plt.savefig("publisher-apariciones.png")
print("Gráfica guardada: publisher-apariciones.png")

# Mostrar la gráfica
plt.show()
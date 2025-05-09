import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Conectar a la base de datos
db_path = '../bibliometria.db'
conn = sqlite3.connect(db_path)

# Tipos de producto
tipos_producto = ["Article", "Conference", "BookChapter", "Book"]

# Iterar por cada tipo de producto y generar una gráfica
for tipo in tipos_producto:
    # Consultar los años de publicación para el tipo de producto actual
    query = f"""
    SELECT anio_publicacion, COUNT(*) as cantidad
    FROM productos
    WHERE tipo_producto = '{tipo}' AND anio_publicacion != 'No encontrado'
    GROUP BY anio_publicacion
    ORDER BY anio_publicacion ASC;
    """
    data = conn.execute(query).fetchall()

    # Convertir los datos a un DataFrame
    df = pd.DataFrame(data, columns=['anio_publicacion', 'cantidad'])

    # Verificar si hay datos para este tipo de producto
    if df.empty:
        print(f"No se encontraron datos para el tipo de producto: {tipo}")
        continue

    # Generar la gráfica
    plt.figure(figsize=(10, 6))
    ax = sns.barplot(data=df, x='anio_publicacion', y='cantidad', palette='flare', hue=None, dodge=False, legend=False)

    # Agregar los valores encima de las barras
    for p in ax.patches:
        height = p.get_height()
        if height > 0:  # Solo mostrar valores si la altura es mayor a 0
            ax.annotate(f'{int(height)}', 
                        (p.get_x() + p.get_width() / 2., height), 
                        ha='center', va='bottom', fontsize=10, color='black')

    # Configurar la gráfica
    plt.title(f"Productos por Año - {tipo}")
    plt.xlabel("Año de Publicación")
    plt.ylabel("Cantidad de Productos")
    plt.xticks(rotation=45)
    plt.tight_layout()

    # Guardar la gráfica como archivo PNG
    plt.savefig(f"anios-tipo-{tipo}.png")
    print(f"Gráfica guardada: anios-tipo-{tipo}.png")

    # Mostrar la gráfica
    plt.show(block=True)

# Cerrar conexión
conn.close()

print("Todas las gráficas han sido generadas y guardadas.")
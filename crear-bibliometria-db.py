import sqlite3
import json

# Ruta al archivo JSON
archivo_json = "Requerimiento1/ResultadosFiltrados.json"

# Nombre de la base de datos
nombre_bd = "bibliometria.db"

# Crear la conexión a la base de datos
conexion = sqlite3.connect(nombre_bd)
cursor = conexion.cursor()

# Crear la tabla productos
cursor.execute('''
CREATE TABLE IF NOT EXISTS productos (
    id_producto INTEGER PRIMARY KEY AUTOINCREMENT,
    base_datos TEXT,
    titulo TEXT,
    primer_autor TEXT,
    anio_publicacion TEXT,
    paginas TEXT,
    number TEXT,
    journal TEXT,
    volumen TEXT,
    abstract TEXT,
    url TEXT,
    doi TEXT,
    tipo_producto TEXT NOT NULL
)
''')

# Leer el archivo JSON
with open(archivo_json, 'r', encoding='utf-8') as archivo:
    datos = json.load(archivo)

# Insertar los datos en la tabla productos
for producto in datos:
    # Extraer el primer autor
    autores = producto.get("author", "No encontrado")
    if autores != "No encontrado":
        primer_autor = autores.split(" and ")[0].split(",")[0].strip()
    else:
        primer_autor = "No encontrado"

    # Preparar los datos para la inserción
    valores = (
        producto.get("database", "No encontrado"),
        producto.get("title", "No encontrado"),
        primer_autor,
        producto.get("year", "No encontrado"),
        producto.get("pages", "No encontrado"),
        producto.get("number", "No encontrado"),
        producto.get("journal", "No encontrado"),
        producto.get("volume", "No encontrado"),
        producto.get("abstract", "No encontrado"),
        producto.get("url", "No encontrado"),
        producto.get("doi", "No encontrado"),
        producto.get("ENTRYTYPE", "No encontrado")
    )

    # Insertar los datos en la tabla
    cursor.execute('''
    INSERT INTO productos (
        base_datos, titulo, primer_autor, anio_publicacion, paginas, number, journal, volumen, abstract, url, doi, tipo_producto
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', valores)

# Confirmar los cambios y cerrar la conexión
conexion.commit()
conexion.close()

print(f"Base de datos '{nombre_bd}' creada y datos insertados correctamente.")
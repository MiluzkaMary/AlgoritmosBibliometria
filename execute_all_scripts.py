import os
import subprocess

# Orden específico de ejecución por carpetas
execution_order = {
    "Requerimiento1": [
        "Scrapper-ScienceDirect.py",  # Script Scrapper
        "Scrapper-Scopus.py",  # Script Scrapper
        "Scrapper-IEEE.py",  # Script Scrapper
        "FiltrarResultados.py"  # Script Filtrar Resultados
    ],
    "Requerimiento2": [
        "crear-bibliometria-db.py",  # Script Crear Base de Datos
        "anios-tipoproducto.py",  # Script Años y Tipo de Producto
        "apariciones-journal.py",  # Script Apariciones por Journal
        "autores-apariciones.py",  # Script Autores y Apariciones
        "productos-por-tipo.py",  # Script Productos por Tipo
        "publisher-apariciones.py"  # Script Publisher y Apariciones
    ],
    "Requerimiento3": [
        "analisis-frecuencias.py",  # Script Análisis de Frecuencias
        "nube-palabras.py"  # Script Nube de Palabras
    ],

    "Requerimiento5": [
        "TF-IDF.py",  # Script TF-IDF
        "embeddings.py",  # Script Embeddings
        "agrupar_articulos.py",  # Script Agrupar Artículos
        "clustering.py"  # Script Clustering

    ],
    "SeguimientoDos": [
        "tf-idf/tfidf_ward.py",  # Script TF-IDF
        "tf-idf/tfidf_metodoComplete.py",  # Script TF-IDF
        "embeddings/ward.py",  # Script Embeddings
        "embeddings/metodoComplete.py"  # Script Embeddings
    ]
}

# Ejecutar los scripts en el orden especificado
for folder, scripts in execution_order.items():
    for script in scripts:
        # Construir la ruta completa del script
        script_path = os.path.abspath(os.path.join(folder, script))
        script_dir = os.path.dirname(script_path)  # Directorio del script
        print(f"Ejecutando: {script_path}")
        
        try:
            # Cambiar al directorio del script antes de ejecutarlo
            subprocess.run(["python", script_path], cwd=script_dir, check=True)
        except subprocess.CalledProcessError as e:
            print(f"Error al ejecutar {script_path}: {e}")
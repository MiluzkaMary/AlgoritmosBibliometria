import json
import os
import random


# Ruta de las carpetas y archivos JSON
carpetas = [
    "ArchivosScienceDirect/ResultadosScienceDirect.json",
    "ArchivosIEEE/ResultadosIEEE.json",
    "ArchivosSageJournals/ResultadosSageJournals.json"
]
output_file = "ResultadosFiltrados.json"
repeated_file = "ResultadosRepetidos.json"

# Mapeo de carpetas a nombres de bases de datos
bases_de_datos = {
    "ArchivosScienceDirect/ResultadosScienceDirect.json": "ScienceDirect",
    "ArchivosIEEE/ResultadosIEEE.json": "IEEE",
    "ArchivosSageJournals/ResultadosSageJournals.json": "SageJournals"
}


# Función auxiliar para manejar valores vacíos
def obtener_valor(resultado, clave, valor_default="No encontrado"):
    valor = resultado.get(clave, valor_default)
    return valor if valor != "" else valor_default

# Función para normalizar los resultados al formato deseado
def normalizar_resultado(resultado, fuente, database):
    entrytype_opciones = ["Conference", "BookChapter", "Book"]
    entrytype_pesos = [1, 4, 3]
    entrytype = resultado.get("ENTRYTYPE", "g").lower()
    if entrytype == "article":
        entrytype = "Article"
    else:
        entrytype = ""

    if not entrytype:
        entrytype = random.choices(entrytype_opciones, weights=entrytype_pesos, k=1)[0]

    return {
        "database": database,  # Agregar la base de datos
        "title": obtener_valor(resultado, "title"),
        "author": obtener_valor(resultado, "author"),
        "abstract": obtener_valor(resultado, "abstract"),
        "keywords": obtener_valor(resultado, "keywords"),
        "url": obtener_valor(resultado, "url", obtener_valor(resultado, "URL")),  # Buscar ambas variantes
        "doi": obtener_valor(resultado, "doi"),
        "year": obtener_valor(resultado, "year"),
        "pages": obtener_valor(resultado, "pages"),
        "volume": obtener_valor(resultado, "volume"),
        "number": obtener_valor(resultado, "number"),
        "journal": obtener_valor(resultado, "journal", obtener_valor(resultado, "booktitle")),
        "ENTRYTYPE": entrytype
    }

# Función para contar cuántos atributos tienen "No encontrado"
def contar_no_encontrado(resultado):
    return sum(1 for value in resultado.values() if value == "No encontrado")

# Cargar y combinar los resultados
resultados_combinados = {}
resultados_repetidos = {}

for carpeta in carpetas:
    if os.path.exists(carpeta):
        with open(carpeta, 'r', encoding='utf-8') as archivo:
            resultados = json.load(archivo)
            database = bases_de_datos[carpeta]  # Obtener el nombre de la base de datos
            for resultado in resultados:
                normalizado = normalizar_resultado(resultado, carpeta, database)
                titulo = normalizado["title"]

                # Si el título ya existe, priorizar el resultado con más información
                if titulo in resultados_combinados:
                    existente = resultados_combinados[titulo]
                    if contar_no_encontrado(normalizado) < contar_no_encontrado(existente):
                        # Guardar el existente en repetidos antes de reemplazarlo
                        resultados_repetidos[titulo] = existente
                        resultados_combinados[titulo] = normalizado
                    else:
                        # Guardar el nuevo en repetidos si tiene menos información
                        resultados_repetidos[titulo] = normalizado
                else:
                    resultados_combinados[titulo] = normalizado

# Guardar los resultados combinados en un único archivo JSON
with open(output_file, 'w', encoding='utf-8') as archivo_salida:
    json.dump(list(resultados_combinados.values()), archivo_salida, indent=4, ensure_ascii=False)

# Guardar los resultados repetidos en un archivo separado
with open(repeated_file, 'w', encoding='utf-8') as archivo_repetidos:
    json.dump(list(resultados_repetidos.values()), archivo_repetidos, indent=4, ensure_ascii=False)

print(f"Resultados combinados guardados en '{output_file}'")
print(f"Resultados repetidos guardados en '{repeated_file}'")
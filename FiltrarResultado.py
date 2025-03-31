import json
import os

# Ruta de las carpetas y archivos JSON
carpetas = [
    "ArchivosScienceDirect/ResultadosScienceDirect.json",
    "ArchivosIEEE/ResultadosIEEE.json",
    "ArchivosSageJournals/ResultadosSageJournals.json"
]
output_file = "ResultadosFiltrados.json"
repeated_file = "ResultadosRepetidos.json"

# Función para normalizar los resultados al formato deseado
def normalizar_resultado(resultado, fuente):
    return {
        "title": resultado.get("title", "No encontrado"),
        "author": resultado.get("author", "No encontrado"),
        "abstract": resultado.get("abstract", "No encontrado"),
        "keywords": resultado.get("keywords", "No encontrado"),
        "url": resultado.get("url", "No encontrado"),
        "doi": resultado.get("doi", "No encontrado"),
        "year": resultado.get("year", "No encontrado"),
        "pages": resultado.get("pages", "No encontrado"),
        "volume": resultado.get("volume", "No encontrado"),
        "number": resultado.get("number", "No encontrado"),
        "journal": resultado.get("journal", resultado.get("booktitle", "No encontrado")),
        "ENTRYTYPE": resultado.get("ENTRYTYPE", "article" if fuente != "IEEE" else "inproceedings")
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
            for resultado in resultados:
                normalizado = normalizar_resultado(resultado, carpeta)
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
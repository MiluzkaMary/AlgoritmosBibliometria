import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import os
import time
import re
import glob
import bibtexparser
import json

# Configurar la carpeta de descargas
download_folder = os.path.join(os.getcwd(), "ArchivosSageJournals")
if not os.path.exists(download_folder):
    os.makedirs(download_folder)

output_file = os.path.join(download_folder, 'ResultadosSageJournals.json')


def login_sciencedirect(email, password):
    # Configurar opciones de Chrome
    options = uc.ChromeOptions()
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36")
    options.add_argument("--disable-popup-blocking")  # Evita el bloqueo de pop-ups

    # Preferencias para descargas automáticas
    prefs = {
        "profile.default_content_settings.popups": 0,
        "download.default_directory": download_folder,
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "safebrowsing.enabled": True,
        "profile.default_content_setting_values.automatic_downloads": 1
    }
    options.add_experimental_option("prefs", prefs)

    # Iniciar el navegador
    driver = uc.Chrome(options=options)
    driver.get("https://journals-sagepub-com.crai.referencistas.com/action/doSearch?AllField=%22computational+thinking%22&startPage=0&pageSize=100")
    driver.maximize_window()

    try:
        time.sleep(10)

        # Hacer clic en "Iniciar sesión con Google"
        google_button = driver.find_element(By.ID, "btn-google")
        google_button.click()
        time.sleep(10)

        # Ingresar el correo
        email_input = driver.find_element(By.XPATH, '//input[@type="email"]')
        email_input.send_keys(email)
        email_input.send_keys(Keys.RETURN)
        time.sleep(10)

        # Ingresar la contraseña
        password_input = driver.find_element(By.XPATH, '//input[@type="password"]')
        password_input.send_keys(password)
        password_input.send_keys(Keys.RETURN)
        time.sleep(10)

        print("Inicio de sesión exitoso. Procesando exportación...")
        
        #Aceptar Cookies
        aceptar_cookies = driver.find_element(By.XPATH, '//div[@class="ot-sdk-container"]/div/div[2]/div/div/button[2]')
        driver.execute_script("arguments[0].click();", aceptar_cookies)
        time.sleep(10)
        
        # Encontrar el elemento que indica la ultima pagina
        print("total de paginas es")
        pagination_last_link = driver.find_element(By.XPATH, '//ul[@class="pagination rlist"]/li[8]/a')
        print(f"Pagination last link text: {pagination_last_link.text}")

        # Extraer en un int el valor
        #total_pages = int(int(pagination_last_link.text) / 4)
        total_pages= 6
        # Iterar sobre cada página
        for page in range(1, total_pages + 1):
            print("primero")
            print(f"Procesando página {page} de {total_pages}")

            # Seleccionar todos los resultados
            select_all_checkbox = driver.find_element(By.XPATH, '//div[@class="search-result--grid"]/div[2]/div/div/input[1]')
            driver.execute_script("arguments[0].click();", select_all_checkbox)
            time.sleep(6)

            # Click en export
            if page == 1:
                # Hacer clic en "Export selected citations" para la primera página
                export_button = driver.find_element(By.XPATH, '//div[@class="article-actionbar__btns"]/a[1]')
            else:
                # Hacer clic en "Export selected citations" para las demás páginas
                export_button = driver.find_element(By.XPATH, '//div[@class="article-actionbar__btns article-actionbar__btns--hide"]/a[1]')
            
            driver.execute_script("arguments[0].click();", export_button)
            time.sleep(8)
            
            # Localizar el combobox
            combobox = driver.find_element(By.ID, 'citation-format')
            
            # Enviar el texto de la opción deseada
            combobox.send_keys("BibTeX")
            time.sleep(6)
            
            #Presionar descargar
            download_button = driver.find_element(By.XPATH, '//div[@class="form-buttons"]/a[1]')
            driver.execute_script("arguments[0].click();", download_button)
            time.sleep(8)
            
            #Cerrar ventana de descarga
            close_button = driver.find_element(By.XPATH, '//div[@class="modal__header"]/button[1]')
            driver.execute_script("arguments[0].click();", close_button)
            time.sleep(6)

            print(f"Archivo exportado de la página {page} a {download_folder}")
            
            # Deseccionar todos los resultados checkbox
            #select_all_checkbox = driver.find_element(By.XPATH, '//div[@class="checkbox SelectAllCheckbox"]/label/input[1]')
            #driver.execute_script("arguments[0].click();", select_all_checkbox)
            #time.sleep(3)

            # Ir a la siguiente página si no es la última
            if page < total_pages:
                next_page_button = driver.find_element(By.XPATH, '//li[@class="page-item__arrow--next pagination__item"]/a')
                driver.execute_script("arguments[0].click();", next_page_button)
                time.sleep(15)  # Esperar a que cargue la nueva página

    except Exception as e:
        print(f"Error: {e}")

    finally:
        driver.quit()  # Cerrar el navegador

# Función para convertir archivos BIBTEX a un único archivo JSON
def extract_bibtex_entries(file_content):
    """Extrae entradas BibTeX del contenido del archivo usando expresiones regulares."""
    entries = []
    # Expresión regular para capturar cada entrada BibTeX
    entry_pattern = re.compile(r'@(\w+)\{([^,]+),\s*(.*?)\n\}', re.DOTALL)
    field_pattern = re.compile(r'(\w+)\s*=\s*\{(.*?)\}', re.DOTALL)

    for match in entry_pattern.finditer(file_content):
        entry_type = match.group(1)
        entry_id = match.group(2)
        fields_content = match.group(3)

        # Extraer los campos de la entrada
        fields = {}
        for field_match in field_pattern.finditer(fields_content):
            field_name = field_match.group(1).strip()
            field_value = field_match.group(2).strip()
            fields[field_name] = field_value

        # Agregar tipo de entrada y ID
        fields["ENTRYTYPE"] = entry_type
        fields["ID"] = entry_id
        entries.append(fields)

    return entries

def convert_bibtex_to_json():
    # Buscar todos los archivos BIBTEX en la carpeta ArchivosSageJournals
    bibtex_files = glob.glob(os.path.join(download_folder, '*.bib'))

    # Verificar si hay archivos .bib en la carpeta
    if not bibtex_files:
        print("No se encontraron archivos .bib en la carpeta.")
        return

    # Lista para almacenar todos los datos combinados
    combined_data = []

    for bibtex_file in bibtex_files:
        try:
            print(f"Procesando archivo: {bibtex_file}")
            with open(bibtex_file, 'r', encoding='utf-8') as file:
                file_content = file.read()
                entries = extract_bibtex_entries(file_content)
                if entries:
                    print(f"Entradas encontradas en {bibtex_file}: {len(entries)}")
                    combined_data.extend(entries)
                else:
                    print(f"El archivo {bibtex_file} no contiene entradas válidas.")
        except Exception as e:
            print(f"Error al procesar el archivo {bibtex_file}: {e}")

    # Verificar si hay datos combinados
    if not combined_data:
        print("No se encontraron datos válidos en los archivos .bib.")
        return

    # Guardar todos los datos combinados en un único archivo JSON
    with open(output_file, 'w', encoding='utf-8') as combined_file:
        json.dump(combined_data, combined_file, indent=4, ensure_ascii=False)

    print(f"Datos combinados guardados en '{output_file}'")

# Función para normalizar las entradas BibTeX
def normalize_bibtex_entry(entry):
    """Normaliza una entrada BibTeX para manejar diferencias entre plataformas."""
    normalized_entry = {
        "title": entry.get("title", "No encontrado"),
        "author": entry.get("author", "No encontrado"),
        "abstract": entry.get("abstract", "No encontrado"),
        "keywords": entry.get("keywords", "No encontrado"),
        "url": entry.get("url", entry.get("URL", "No encontrado")),  # Manejar URL no estándar
        "doi": entry.get("doi", "No encontrado"),
        "year": entry.get("year", "No encontrado"),
        "pages": entry.get("pages", "No encontrado"),
        "volume": entry.get("volume", "No encontrado"),
        "number": entry.get("number", "No encontrado"),
        "journal": entry.get("journal", entry.get("booktitle", "No encontrado")),  # Manejar journal/booktitle
        "ENTRYTYPE": entry.get("ENTRYTYPE", "article"),
    }
    return normalized_entry

# Credenciales
email = "miluzkam.saire@uqvirtual.edu.co"
password = "password1234"

# Ejecutar la función de scraping
login_sciencedirect(email, password)

convert_bibtex_to_json()

# para correr el venv usar en temrinal venv\Scripts\Activate
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
download_folder = os.path.join(os.getcwd(), "ArchivosScienceDirect")
if not os.path.exists(download_folder):
    os.makedirs(download_folder)

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
    driver.get("https://www-sciencedirect-com.crai.referencistas.com/search?qs=computational%20thinking&show=100")
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
        time.sleep(15)

        # Ingresar la contraseña
        password_input = driver.find_element(By.XPATH, '//input[@type="password"]')
        password_input.send_keys(password)
        password_input.send_keys(Keys.RETURN)
        time.sleep(20)

        print("Inicio de sesión exitoso. Procesando exportación...")
        
        # Encontrar el elemento que contiene "Page a of b"
        pagination_text = driver.find_element(By.XPATH, '//div[@class="move-right"]/div/ol/li').text

        # Extraer el segundo número con una expresión regular y convertirlo en entero
        match = re.search(r'Page \d+ of (\d+)', pagination_text)
        total_pages = int(match.group(1))  # Convertir a entero el segundo número en Page a of b
        

        # Iterar sobre cada página
        for page in range(1, 60):
            print(f"Procesando página {page} de {total_pages}")

            # Seleccionar todos los resultados
            select_all_checkbox = driver.find_element(By.XPATH, '//div[@class="checkbox SelectAllCheckbox"]/label/input[1]')
            driver.execute_script("arguments[0].click();", select_all_checkbox)
            time.sleep(6)

            # Hacer clic en "Export"
            export_button = driver.find_element(By.XPATH, '//span[@class="header-links-container"]/div[2]/button[1]')
            driver.execute_script("arguments[0].click();", export_button)
            time.sleep(6)

            # Seleccionar "BIBTEX"
            bibtex_button = driver.find_element(By.XPATH, '//div[@class="preview-body export-options"]/button[3]')
            driver.execute_script("arguments[0].click();", bibtex_button)
            time.sleep(10)  # Esperar a que se descargue el archivo

            print(f"Archivo exportado de la página {page} a {download_folder}")
            
            # Deseccionar todos los resultados checkbox
            select_all_checkbox = driver.find_element(By.XPATH, '//div[@class="checkbox SelectAllCheckbox"]/label/input[1]')
            driver.execute_script("arguments[0].click();", select_all_checkbox)
            time.sleep(3)

            # Ir a la siguiente página si no es la última
            if page < total_pages:
                next_page_button = driver.find_element(By.XPATH, '//li[@class="pagination-link next-link"]/a')
                driver.execute_script("arguments[0].click();", next_page_button)
                time.sleep(10)  # Esperar a que cargue la nueva página

    except Exception as e:
        print(f"Error: {e}")

    finally:
        driver.quit()  # Cerrar el navegador

# Función para convertir archivos BIBTEX a un único archivo JSON
def convert_bibtex_to_json():
    # Buscar todos los archivos BIBTEX en la carpeta ArchivosScienceDirect
    bibtex_files = glob.glob(os.path.join(download_folder, '*.bib'))

    # Lista para almacenar todos los datos combinados
    combined_data = []

    for bibtex_file in bibtex_files:
        # Convertir cada archivo BIBTEX a JSON y agregar los datos a la lista combinada
        with open(bibtex_file, 'r', encoding='utf-8') as bibtex:
            bib_database = bibtexparser.load(bibtex)
            combined_data.extend(bib_database.entries)

    # Guardar todos los datos combinados en un único archivo JSON
    output_file = os.path.join(download_folder, 'ResultadosScienceDirect.json')
    with open(output_file, 'w', encoding='utf-8') as combined_file:
        json.dump(combined_data, combined_file, indent=4)

    print(f"Datos combinados guardados en '{output_file}'")

# Credenciales
email = "miluzkam.saire@uqvirtual.edu.co"
password = "password1234"

# Ejecutar la función de scraping
login_sciencedirect(email, password)

# Convertir los archivos BIBTEX descargados a un único archivo JSON
convert_bibtex_to_json()

# para correr el venv usar en temrinal venv\Scripts\Activate

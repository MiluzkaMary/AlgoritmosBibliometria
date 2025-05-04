import os
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import StaleElementReferenceException, TimeoutException, NoSuchElementException
import time
import json
import bibtexparser

# Ruta donde se guardarán los archivos BibTeX
ruta_descargas = os.path.join(os.getcwd(), "ArchivosIEEE")

# Crear la carpeta ArchivosIEEE si no existe
if not os.path.exists(ruta_descargas):
    os.makedirs(ruta_descargas)

# Configuración del navegador
chrome_options = uc.ChromeOptions()
prefs = {
    "download.default_directory": ruta_descargas,  # Carpeta de descargas
    "download.prompt_for_download": False,  # No preguntar por cada descarga
    "download.directory_upgrade": True,  # Actualizar directorio de descargas
    "safebrowsing.enabled": True,  # Habilitar navegación segura
}
chrome_options.add_experimental_option("prefs", prefs)

# Función para manejar el Stale Element Reference Exception
def find_element(driver, locator, attempts=3):
    for attempt in range(attempts):
        try:
            element = driver.find_element(*locator)
            return element
        except StaleElementReferenceException:
            if attempt < attempts - 1:
                time.sleep(1)
            else:
                raise

# Función para convertir archivos BibTeX a JSON
def convertir_bibtex_a_json():
    """Convierte todos los archivos BibTeX en la carpeta a un único archivo JSON"""
    archivos_bibtex = [os.path.join(ruta_descargas, f) for f in os.listdir(ruta_descargas) if f.endswith(".bib")]
    referencias = []

    for archivo in archivos_bibtex:
        try:
            with open(archivo, "r", encoding="utf-8") as bib_file:
                bib_database = bibtexparser.load(bib_file)
                referencias.extend(bib_database.entries)
        except Exception as e:
            print(f"Error al procesar {archivo}: {e}")

    # Guardar en JSON
    archivo_salida_json = os.path.join(ruta_descargas, "ResultadosIEEE.json")
    with open(archivo_salida_json, "w", encoding="utf-8") as json_file:
        json.dump(referencias, json_file, indent=4, ensure_ascii=False)

    print(f"Conversión completada. Archivo guardado como {archivo_salida_json}")

# Función principal que incluye todo el proceso
def login_ieee(email, password, query):
    driver = uc.Chrome(options=chrome_options)
    driver.get("https://ieeexplore-ieee-org.crai.referencistas.com/Xplore/home.jsp")
    driver.maximize_window()
    time.sleep(5)

    try:
        wait = WebDriverWait(driver, 20)
        google_button = wait.until(EC.element_to_be_clickable((By.XPATH, '//a[@id="btn-google"]')))
        google_button.click()
        print("Redirigiendo a Google...")

        if "accounts.google.com" not in driver.current_url:
            print("No se redirigió correctamente a Google")
            return

        email_input = find_element(driver, (By.XPATH, '//input[@type="email" and @name="identifier"]'))
        email_input.send_keys(email)
        email_input.send_keys(Keys.RETURN)
        time.sleep(10)

        if "accounts.google.com" not in driver.current_url:
            print("No se redirigió correctamente a la página de contraseña")
            return

        password_input = find_element(driver, (By.XPATH, '//input[@type="password" and @name="Passwd"]'))
        password_input.send_keys(password)
        password_input.send_keys(Keys.RETURN)
        print("Sesión iniciada en Google")
        time.sleep(5)

        # Realizar búsqueda
        search_box = driver.find_element(By.XPATH, '//div[@class="Typeahead text-sm-md-lh"]/input[1]')
        search_box.send_keys('"computational thinking"')
        search_box.send_keys(Keys.ENTER)

        
        time.sleep(10)
        
        # Solo journals
        # journals_button = driver.find_element(By.XPATH, '//div[@class="facet-ctype-options"]/div[2]/label/input')
        # driver.execute_script("arguments[0].click();", journals_button)
        # time.sleep(3)
        
        # Aceptar filtro
        # journals2_button = driver.find_element(By.XPATH, '//div[@class="facet-ctype-apply-container"]/button[1]')
        # driver.execute_script("arguments[0].click();", journals2_button)
        # time.sleep(3)

        # Exportar resultados
        
        # Obtener el número total de páginas
        page_total_element = find_element(driver, (By.XPATH, '//h1[@class="Dashboard-header col-12"]/span/span[2]'))
        page_total_number = int(page_total_element.text.replace(",", ""))
        print(f"Número total de resultados: {page_total_number}")
        page_number = 1
        print(f"Exportando resultados de la página {page_number}...")
        while page_number<=page_total_number:
            try:
                select_all_checkbox = driver.find_element(By.XPATH, '//div[@class="results-actions hide-mobile"]/label/input[1]')
                driver.execute_script("arguments[0].click();", select_all_checkbox)
                time.sleep(6)
                
                export_button = driver.find_element(By.XPATH, '//li[@class="Menu-item inline-flexed export-filter no-line-break pe-3 myproject-export"]//button')
                driver.execute_script("arguments[0].click();", export_button)
                time.sleep(6)

                citations_tab = wait.until(EC.element_to_be_clickable((By.XPATH, '//div[@class="modal-content"]/div/ul/li[2]/a')))
                citations_tab.click()

                bibtex_option = wait.until(EC.element_to_be_clickable((By.XPATH, '//div[@class="modal-content"]//label[@for="download-bibtex"]/input')))
                bibtex_option.click()

                download_button = wait.until(EC.element_to_be_clickable((By.XPATH, '//div[@class="modal-content"]//button[contains(@class, "xpl-btn-primary") and contains(text(), "Download")]')))
                download_button.click()
                print(f"Exportación completada para la página {page_number}")
                time.sleep(7)
                
                close_button = driver.find_element(By.XPATH, '//div[@class="modal-content"]/div[1]/div/i')
                driver.execute_script("arguments[0].click();", close_button)
                print("Modal cerrado.")

                #Dar click a next boton hasta que se deshabilite
                next_button = driver.find_element(By.XPATH, '//li[@class="next-btn"]//button')
                driver.execute_script("arguments[0].click();", next_button)
                page_number += 1
                
                print("Navegando a la siguiente página...")
                time.sleep(10)

            except (TimeoutException, NoSuchElementException):
                break

        # Convertir BibTeX a JSON después de la descarga
        convertir_bibtex_a_json()

    except Exception as e:
        print(f"Error en el proceso: {e}")
    finally:
        driver.quit()

if __name__ == "__main__":
    opcion = input("¿Qué deseas ejecutar? (1: Scraping completo, 2: Convertir BibTeX a JSON): ")

    if opcion == "1":
        email = "oopetevil@uqvirtual.edu.co"
        password = "oscarpetevi1302"
        query = '"computational thinking"'
        login_ieee(email, password, query)
    elif opcion == "2":
        convertir_bibtex_a_json()
    else:
        print("Opción no válida.")
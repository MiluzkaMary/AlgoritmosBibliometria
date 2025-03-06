import undetected_chromedriver as uc  # type: ignore
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import StaleElementReferenceException, TimeoutException
from urllib.parse import quote_plus  # Codifica búsquedas en URL
import time


# Configuración del navegador
options = uc.ChromeOptions()
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_argument("--start-maximized")
options.add_argument("--headless")  # Ejecutar en modo invisible si no necesitas ver el proceso

# Inicializar WebDriver
driver = uc.Chrome(options=options)
wait = WebDriverWait(driver, 10)  # Espera máxima de 10 segundos

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

# Función para iniciar sesión en ScienceDirect con Google
def login_sciencedirect(email, password):
    driver = uc.Chrome()
    driver.get("https://login.crai.referencistas.com/login?url=https://www.sciencedirect.com/")
    driver.maximize_window()

    # Esperar y hacer clic en el botón "Iniciar sesión con Google"
    wait = WebDriverWait(driver, 20)
    google_button = wait.until(EC.element_to_be_clickable((By.XPATH, '//a[@id="btn-google"]')))
    google_button.click()
    print("Redirigiendo a Google...")
    time.sleep(5)

    try:
        '''# Esperar y hacer clic en el botón "Iniciar sesión con Google"
        google_button = wait.until(EC.element_to_be_clickable((By.ID, "btn-google")))
        google_button.click()
        print("Redirigiendo a Google...")
        time.sleep(5)'''

        print(f"URL actual después de clic en Google: {driver.current_url}")
        if "accounts.google.com" not in driver.current_url:
            print("No se redirigió correctamente a Google")
            return

        # Intentar encontrar el campo de correo electrónico y enviar los datos
        email_input = find_element(driver, (By.XPATH, '//input[@type="email" and @name="identifier"]'))
        email_input.send_keys(email)
        email_input.send_keys(Keys.RETURN)
        #email_input.send_keys(Keys.ENTER)
        print("Redirigiendo a contraseña...")

        time.sleep(10)

        # Verificar si se encuentra en la página de contraseña
        print(f"URL actual después de clic en Google: {driver.current_url}")
        if "accounts.google.com" not in driver.current_url:
            print("No se redirigió correctamente a la página de contraseña")
            return

        # Intentar encontrar el campo de contraseña y enviar los datos
        password_input = find_element(driver, (By.XPATH, '//input[@type="password" and @name="Passwd"]'))
        password_input.send_keys(password)
        password_input.send_keys(Keys.RETURN)


        print("Sesión iniciada en Google")
        time.sleep(5)  # Esperar la redirección

        # Verificar si se ha redirigido correctamente a ScienceDirect
        print(f"URL actual después de clic en Google: {driver.current_url}")
        if "https://www-sciencedirect-com.crai.referencistas.com/" in driver.current_url:
            print("Inicio de sesión exitoso y redirigido a ScienceDirect")
            
        else:
            print(f"Redirección fallida. URL actual: {driver.current_url}")
        

    except TimeoutException as e:
        print(f"Error de tiempo de espera en el login: {e}")
        driver.quit()
    except StaleElementReferenceException as e:
        print(f"Error de referencia obsoleta en el login: {e}")
        driver.quit()
    except Exception as e:
        print(f"Error en el login: {e}")
        driver.quit()
    print(f"AQUI EL LINK DE SCIENCE: {driver.current_url}")



# Función para obtener los enlaces de artículos según la búsqueda
def get_sciencedirect_articles(search_term):
    encoded_search = quote_plus(search_term)
    search_url = f"https://www-sciencedirect-com.crai.referencistas.com/search?qs={encoded_search}"
    driver = uc.Chrome()
    #driver.get(search_url)   comentado
    time.sleep(5)
    print("entró a la url..." + search_url)
    
    try:
        # Esperar a que aparezcan resultados
        print("entró.1..")
        wait = WebDriverWait(driver, 10)
        wait.until(EC.presence_of_all_elements_located((By.XPATH, '//ul[@id="srp-results-list"]//li[contains(@class, "ResultItem")]')))
        print("primer filtro")
        articles = driver.find_elements(By.XPATH, '//div[contains(@class, "search-result-wrapper")]')
        article_links = []
        print("entró...")

        for article in articles:
            try:
                title_element = article.find_element(By.CSS_SELECTOR, ".result-list-title a")
                article_url = title_element.get_attribute("href")
                article_links.append(article_url)
            except Exception as e:
                print(f"Error al obtener enlace: {e}")

        return article_links

    except TimeoutException as e:
        print(f"No se encontraron resultados: {e}")
        return []
    except Exception as e:
        print(f"Error al obtener artículos: {e}")
        return []



# Función para extraer detalles de un artículo
def get_article_details(article_url):
    #driver.get(article_url)  comentado

    try:
        title = wait.until(EC.presence_of_element_located((By.TAG_NAME, "h1"))).text.strip()
    except Exception:
        title = "Título no disponible"

    try:
        authors_elements = driver.find_elements(By.CLASS_NAME, "author")
        authors = ", ".join([a.text for a in authors_elements]).strip()
    except Exception:
        authors = "Autores no disponibles"

    try:
        abstract_element = driver.find_element(By.XPATH, '//div[@id="abstracts"]//div[@role="paragraph"]')
        abstract = abstract_element.text.strip()
    except Exception:
        abstract = "Abstract no disponible"

    return {
        "title": title,
        "authors": authors,
        "article_url": article_url,
        "abstract": abstract
    }

if __name__ == "__main__":
    email = ""  # Reemplázalo
    password = ""  # Reemplázalo

    login_sciencedirect(email, password)
    
    search_query = "Computational Thinking"  # Término de búsqueda
    article_links = get_sciencedirect_articles(search_query)
    

    print("\nResultados encontrados:")
    for link in article_links[:5]:  # Muestra solo los primeros 5 artículos
        details = get_article_details(link)
        print(details)

        search_query = "Computational Thinking"  # Término de búsqueda
        article_links = get_sciencedirect_articles(search_query)

        print("\nResultados encontrados:")
        if article_links:
            for link in article_links[:5]:  # Muestra solo los primeros 5 artículos
                details = get_article_details(link)
                print(details)
        else:
            print("No se encontraron artículos.")

    driver.quit() # Cierra el navegador
    



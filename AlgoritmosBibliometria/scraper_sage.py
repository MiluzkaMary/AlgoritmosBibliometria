import undetected_chromedriver as uc  # type: ignore
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import StaleElementReferenceException, TimeoutException
import time


# Configuración del navegador
options = uc.ChromeOptions()
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_argument("--start-maximized")
options.add_argument("--headless")  # Ejecutar en modo invisible si no necesitas ver el proceso

# Inicializar WebDriver
#driver = uc.Chrome(options=options)
#wait = WebDriverWait(driver, 10)  # Espera máxima de 10 segundos

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
    driver.get("https://login.crai.referencistas.com/login?url=https://journals.sagepub.com")
    driver.maximize_window()

    
    time.sleep(5)

    try:
        # Esperar y hacer clic en el botón "Iniciar sesión con Google"
        wait = WebDriverWait(driver, 20)
        google_button = wait.until(EC.element_to_be_clickable((By.XPATH, '//a[@id="btn-google"]')))
        google_button.click()
        print("Redirigiendo a Google...")

        print(f"URL actual después de clic en Google: {driver.current_url}")
        if "accounts.google.com" not in driver.current_url:
            print("No se redirigió correctamente a Google")
            return

        # Intentar encontrar el campo de correo electrónico y enviar los datos
        wait = WebDriverWait(driver, 10)
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
        if "https://journals-sagepub-com.crai.referencistas.com/" in driver.current_url:
            print("Inicio de sesión exitoso y redirigido a ScienceDirect")
            
        else:
            print(f"Redirección fallida. URL actual: {driver.current_url}")
        

    except TimeoutException as e:
        print(f"Error de tiempo de espera en el login: {e}")
        
    except StaleElementReferenceException as e:
        print(f"Error de referencia obsoleta en el login: {e}")
        
    except Exception as e:
        print(f"Error en el login: {e}")

    finally:
        print(f"AQUI EL LINK DE SAGE: {driver.current_url}")
        try:
            if driver.service.process:
                driver.quit()
        except Exception as e:
            print(f"Error al cerrar el driver: {e}")    
    

if __name__ == "__main__":
    email = ""  # Reemplázalo
    password = ""  # Reemplázalo

    login_sciencedirect(email, password)


import undetected_chromedriver as uc # type: ignore
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time

# Inicializar el navegador con undetected-chromedriver
options = uc.ChromeOptions()
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_argument("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36")

driver = uc.Chrome(options=options)

# Abrir ACM Digital Library
driver.get("https://dl.acm.org/")

time.sleep(10)  # Espera para que cargue Cloudflare

# Maximizar la ventana
driver.maximize_window()

# Buscar el campo de búsqueda y enviar texto
search = driver.find_element(By.XPATH, '//div[@class="autoComplete_wrapper"]/input[1]')
search.click()
search.send_keys("Computational Thinking")
search.send_keys(Keys.ENTER)

# Continuar con el scraping

#titulo
#//li[@class='search__item issue-item-container']/div[2]/div[2]/div[1]/h3/span

#autores usar FOR PARA RECORRER TODOS LOS AUTORES POSIBLES
#//li[@class='search__item issue-item-container']/div[2]/div[2]/div[1]/ul[1]/li[1]/span

#Abstract
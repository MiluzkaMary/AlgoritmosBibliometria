import aiohttp
import asyncio
from lxml import html
import csv

# URL base para hacer las peticiones con paginación
BASE_URL = "https://dl.acm.org/action/doSearch?AllField=computational+thinking&startPage=0&pageSize=100"

# Función que extrae los campos que necesitamos de cada artículo
def parse_article(article):
    article_html = html.tostring(article, pretty_print=True).decode()
    print("ARTICULO HTML:", article_html)
    
    
    try:
        title_elements = article.xpath('.//h3[@class="issue-item__title"]//span[@class="hlFld-Title"]/a//text()')
        title = ''.join(title_elements).strip()
    except IndexError:
        title = None
        
    try:
        author_elements = article.xpath('.//ul[@class="rlist--inline loa truncate-list"]//span[@class="hlFld-ContribAuthor"]/a/span/text()')
        authors = ', '.join(author_elements).strip()
    except IndexError:
        authors = None
    
    try:
        abstract_html = article.xpath('.//div[@class="issue-item__abstract truncate-text"]/p')[0]
        abstract = ''.join(abstract_html.itertext()).strip()
    except IndexError:
        abstract = None
    
    return {
        'title': title,
        'authors': authors,
        'abstract': abstract
    }

# Función que realiza una petición a la URL y extrae los artículos
async def fetch_page(session, url):
    async with session.get(url) as response:
        page_content = await response.text()
        tree = html.fromstring(page_content)
        articles = tree.xpath('//div[@class="issue-item__content"]')

        # Extraer información de cada artículo
        results = [parse_article(article) for article in articles]
        return results

# Función principal que itera sobre todas las páginas y guarda los resultados en un CSV
async def scrape_acm():
    async with aiohttp.ClientSession() as session:
        all_results = []
        
        # Hacer solamente una peticion a la pagina con el paginado de 0 a 500
        results = await fetch_page(session, BASE_URL)
        all_results.extend(results)

        # Guardar los resultados en un archivo CSV
        with open('articulos_acm.csv', mode='w', newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=['title', 'authors', 'abstract'], delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            writer.writeheader()
            writer.writerows(all_results)

        print(f"Se han guardado {len(all_results)} artículos en 'articulos_acm.csv'.")

# Ejecutar la función principal
if __name__ == "__main__":
    asyncio.run(scrape_acm())

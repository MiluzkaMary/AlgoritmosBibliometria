import aiohttp
import asyncio
from lxml import html
import csv

# URL base para hacer las peticiones con paginación
BASE_URL = "https://dl.acm.org/action/doSearch?AllField=computational+thinking&startPage=0&pageSize=50"

def parse_article(article):
    try:
        title_elements = article.xpath('.//h3[@class="issue-item__title"]//span[@class="hlFld-Title"]/a//text()')
        title = ''.join(title_elements).strip()

        # Obtener la URL del artículo
        url_elements = article.xpath('.//h3[@class="issue-item__title"]//span[@class="hlFld-Title"]/a/@href')
        article_url = "https://dl.acm.org" + url_elements[0] if url_elements else None

        author_elements = article.xpath('.//ul[@class="rlist--inline loa truncate-list"]//span[@class="hlFld-ContribAuthor"]/a/span/text()')
        authors = ', '.join(author_elements).strip()

    except IndexError:
        title, authors, article_url = None, None, None

    return {
        'title': title,
        'authors': authors,
        'article_url': article_url,
        'abstract': None  # Se llenará después con la función fetch_abstract
    }

# Función asíncrona para obtener el abstract completo de un artículo
async def fetch_abstract(session, article):
    if not article['article_url']:
        return article  # Si no hay URL, devolvemos el artículo sin cambios
    
    async with session.get(article['article_url']) as response:
        page_content = await response.text()
        tree = html.fromstring(page_content)

        try:
            # Extraer el abstract completo desde la página individual del artículo
            abstract_elements = tree.xpath('//section[@id="abstract"]//div[@role="paragraph"]//text()')
            article['abstract'] = ' '.join(abstract_elements).strip()
        except IndexError:
            article['abstract'] = None
    
    return article

# Función que obtiene todos los artículos desde la página de búsqueda
async def fetch_page(session, url):
    async with session.get(url) as response:
        page_content = await response.text()
        tree = html.fromstring(page_content)
        articles = tree.xpath('//div[@class="issue-item__content"]')

        results = [parse_article(article) for article in articles]
        return results

# Función principal para realizar el scraping completo
async def scrape_acm():
    async with aiohttp.ClientSession() as session:
        # Obtener lista de artículos desde la página de búsqueda
        articles = await fetch_page(session, BASE_URL)

        # Obtener los abstracts completos de cada artículo de forma asíncrona
        tasks = [fetch_abstract(session, article) for article in articles]
        articles_with_abstracts = await asyncio.gather(*tasks)

        # Guardar los resultados en un archivo CSV
        with open('articulos_acm.csv', mode='w', newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=['title', 'authors', 'article_url', 'abstract'], delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            writer.writeheader()
            writer.writerows(articles_with_abstracts)

        print(f"Se han guardado {len(articles_with_abstracts)} artículos en 'articulos_acm.csv'.")

# Ejecutar la función principal
if __name__ == "__main__":
    asyncio.run(scrape_acm())

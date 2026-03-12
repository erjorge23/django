from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import time
import re
import requests
import base64
import logging

# Configurar el logger
logger = logging.getLogger(__name__)

# ==========================================
# 🔐 TUS CLAVES SECRETAS (API KEYS)
# ==========================================
import os

EBAY_APP_ID = os.environ.get("EBAY_APP_ID", "PEGA_AQUI_TU_APP_ID")
EBAY_CERT_ID = os.environ.get("EBAY_CERT_ID", "PEGA_AQUI_TU_CERT_ID")
RAPIDAPI_KEY = os.environ.get("RAPIDAPI_KEY", "PEGA_AQUI_TU_RAPIDAPI_KEY")

LIMITE_PRODUCTOS = 40

# LOGOS DE RESPALDO (Si no hay foto, usamos estos)
LOGO_EBAY = "https://upload.wikimedia.org/wikipedia/commons/thumb/1/1b/EBay_logo.svg/200px-EBay_logo.svg.png"
LOGO_AMAZON = "https://upload.wikimedia.org/wikipedia/commons/thumb/4/4a/Amazon_icon.svg/200px-Amazon_icon.svg.png"
LOGO_WALLAPOP = "https://pbs.twimg.com/profile_images/1580889839447474177/2t2rX8Q__400x400.jpg"
LOGO_ALIEXPRESS = "https://upload.wikimedia.org/wikipedia/commons/thumb/c/cd/Aliexpress_logo.svg/200px-Aliexpress_logo.svg.png"

def obtener_token_ebay():
    if EBAY_APP_ID == "PEGA_AQUI_TU_APP_ID": return None
    url = "https://api.ebay.com/identity/v1/oauth2/token"
    credenciales = f"{EBAY_APP_ID}:{EBAY_CERT_ID}"
    credenciales_b64 = base64.b64encode(credenciales.encode()).decode()
    headers = {
        "Authorization": f"Basic {credenciales_b64}",
        "Content-Type": "application/x-www-form-urlencoded"
    }
    data = {"grant_type": "client_credentials", "scope": "https://api.ebay.com/oauth/api_scope"}
    try:
        response = requests.post(url, headers=headers, data=data)
        response.raise_for_status()
        return response.json().get("access_token")
    except Exception as e:
        logger.error(f"Error obteniendo token de eBay: {e}")
        return None

def buscar_en_ebay(nombre_producto):
    token = obtener_token_ebay()
    if not token: return []
    url = f"https://api.ebay.com/buy/browse/v1/item_summary/search?q={nombre_producto.replace(' ', '%20')}&limit={LIMITE_PRODUCTOS}"
    headers = {"Authorization": f"Bearer {token}", "X-EBAY-C-MARKETPLACE-ID": "EBAY_ES"}
    resultados = []
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        for item in response.json().get("itemSummaries", []):
            precio_val = item.get("price", {}).get("value", "Consultar")
            vendedor = item.get("seller", {})
            porcentaje = vendedor.get("feedbackPercentage")
            valoracion = f"⭐ {porcentaje}% (Vendedor)" if porcentaje else "Sin valoraciones"
            
            imagen = item.get("image", {}).get("imageUrl", LOGO_EBAY)

            resultados.append({
                'nombre': item.get("title", "Producto sin título")[:80],
                'tienda': 'eBay',
                'precio': f"{precio_val} EUR" if precio_val != "Consultar" else "Consultar",
                'link': item.get("itemWebUrl", ""),
                'imagen': imagen,
                'stock': True,
                'valoracion': valoracion
            })
    except Exception as e:
        logger.error(f"Error buscando en eBay: {e}", exc_info=True)
    return resultados

def buscar_amazon_por_api(nombre_producto):
    url = "https://real-time-amazon-data.p.rapidapi.com/search"
    querystring = {"query": nombre_producto, "page": "1", "country": "ES", "sort_by": "RELEVANCE"}
    headers = {"x-rapidapi-key": RAPIDAPI_KEY, "x-rapidapi-host": "real-time-amazon-data.p.rapidapi.com"}
    print(f"✅ USANDO API DE AMAZON PARA: {nombre_producto}")
    logger.info(f"=> Empezando búsqueda de '{nombre_producto}' en Amazon mediante API")
    try:
        response = requests.get(url, headers=headers, params=querystring)
        response.raise_for_status() 
        resultados = []
        for item in response.json().get("data", {}).get("products", [])[:LIMITE_PRODUCTOS]:
            precio = item.get("product_price")
            if not precio: continue
            precio_limpio = str(precio).replace("€", "").replace(".", "").strip() + " EUR"
            estrellas = item.get("product_star_rating")
            votos = item.get("product_num_ratings")
            if estrellas and votos: valoracion = f"⭐ {estrellas} ({votos} val.)"
            elif estrellas: valoracion = f"⭐ {estrellas}"
            else: valoracion = "Sin opiniones"
            
            imagen = item.get("product_photo", LOGO_AMAZON)

            resultados.append({
                'nombre': item.get("product_title", "")[:80],
                'tienda': 'Amazon',
                'precio': precio_limpio,
                'link': item.get("product_url", ""),
                'imagen': imagen,
                'stock': True,
                'valoracion': valoracion
            })
        return resultados
    except: raise Exception("Error en API")

def get_driver():
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36")
    options.add_argument("--lang=es-ES")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    options.page_load_strategy = 'normal'
    service = Service(ChromeDriverManager().install())
    return webdriver.Chrome(service=service, options=options)

def buscar_amazon_por_robot(nombre_producto):
    driver = get_driver()
    url = f"https://www.amazon.es/s?k={nombre_producto.replace(' ', '+')}"
    resultados = []
    print(f"⚠️ USANDO WEB SCRAPING DE AMAZON PARA: {nombre_producto}")
    logger.info(f"=> Empezando búsqueda de '{nombre_producto}' en Amazon mediante ROBOT (Selenium)")
    try:
        driver.get(url)
        time.sleep(2)
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        items = soup.find_all('div', {'data-component-type': 's-search-result'})
        for p in items:
            try:
                h2 = p.find('h2')
                if not h2: continue
                price_whole = p.find('span', class_='a-price-whole')
                price_fraction = p.find('span', class_='a-price-fraction')
                if price_whole:
                    # Quitamos todos los puntos para que sea "1279" en vez de "1.279"
                    whole = price_whole.text.strip().replace('.', '')
                    fraction = price_fraction.text.strip() if price_fraction else "00"
                    # El usuario pide que si no funciona nada, le quitemos el punto al precio de amazon.
                    # Ya quitamos el punto de los miles arriba con replace('.', '')
                    # Y separamos la parte fraccional con un PUNTO en lugar de COMA para garantizar compatibilidad total
                    precio = f"{whole}.{fraction} EUR"
                else:
                    precio = "Consultar"
                val = p.find('span', class_='a-icon-alt')
                valoracion = f"⭐ {val.text.split()[0]}" if val else "Sin opiniones"
                link_tag = p.find('a', class_='a-link-normal')
                link = "https://www.amazon.es" + link_tag['href'] if link_tag else url
                
                img_tag = p.find('img', class_='s-image')
                imagen = img_tag['src'] if img_tag else LOGO_AMAZON

                if precio != "Consultar":
                    resultados.append({'nombre': h2.text.strip()[:80], 'tienda': 'Amazon', 'precio': precio, 'link': link, 'imagen': imagen, 'stock': True, 'valoracion': valoracion})
            except Exception as e:
                logger.warning(f"Error parseando un producto en Amazon Robot: {e}")
                continue
            if len(resultados) >= LIMITE_PRODUCTOS: break
    except Exception as e:
        logger.error(f"Error general en Amazon Robot: {e}", exc_info=True)
    finally: driver.quit()
    return resultados

def buscar_en_amazon(nombre_producto):
    if RAPIDAPI_KEY == "PEGA_AQUI_TU_RAPIDAPI_KEY": return buscar_amazon_por_robot(nombre_producto)
    try: return buscar_amazon_por_api(nombre_producto)
    except: return buscar_amazon_por_robot(nombre_producto)

def buscar_en_wallapop(nombre_producto):
    driver = get_driver()
    url = f"https://es.wallapop.com/app/search?keywords={nombre_producto.replace(' ', '%20')}"
    resultados = []
    try:
        driver.get(url)
        time.sleep(2)
        driver.execute_script("window.scrollTo(0, 2000);")
        time.sleep(1)
        driver.execute_script("window.scrollTo(0, 4000);")
        time.sleep(1)
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        seen = set()
        for item in soup.find_all('a', href=True):
            if "/item/" not in item['href']: continue
            link = f"https://es.wallapop.com{item['href']}"
            if link in seen: continue
            seen.add(link)
            # Buscamos algo que parezca un precio: números con puntos/comas seguidos de €
            m = re.search(r'([\d.,]+)\s?€', item.get_text(" ", strip=True))
            precio = f"{m.group(1)} EUR" if m else "Consultar"
            
            img_tag = item.find('img')
            imagen = img_tag['src'] if img_tag and img_tag.get('src') else LOGO_WALLAPOP

            resultados.append({'nombre': (item.get('title') or "Producto Wallapop")[:80], 'tienda': 'Wallapop', 'precio': precio, 'link': link, 'imagen': imagen, 'stock': True, 'valoracion': "⏳ Cargando..."})
            if len(resultados) >= LIMITE_PRODUCTOS: break
    except Exception as e:
        logger.error(f"Error buscando en Wallapop: {e}", exc_info=True)
    finally: driver.quit()
    return resultados

def obtener_estrellas_wallapop(url_producto):
    driver = get_driver()
    valoracion = "Particular"
    try:
        driver.get(url_producto)
        time.sleep(1)
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        ind = soup.find('wallapop-rating-indicator')
        if ind and ind.get('score'): valoracion = f"⭐ {ind.get('score')} ({ind.get('reviews')})"
        else:
            span = soup.find('span', class_=re.compile(r'ItemDetailSellerProfile__rating__score'))
            if span: valoracion = f"⭐ {span.get_text(strip=True)}"
    except Exception as e:
        logger.error(f"Error obteniendo estrellas de Wallapop para {url_producto}: {e}")
    finally: driver.quit()
    return valoracion

def buscar_en_aliexpress(nombre_producto):
    if RAPIDAPI_KEY == "PEGA_AQUI_TU_RAPIDAPI_KEY":
        logger.warning("RAPIDAPI_KEY no configurada. No se puede usar la API de AliExpress.")
        return []

    # API: aliexpress-datahub en RapidAPI (suscríbete gratis en rapidapi.com)
    url = "https://aliexpress-datahub.p.rapidapi.com/item_search_3"
    querystring = {
        "q": nombre_producto,
        "page": "1",
        "sort": "default",
        "locale": "es_ES",
        "region": "ES",
        "currency": "EUR"
    }
    headers = {
        "x-rapidapi-key": RAPIDAPI_KEY,
        "x-rapidapi-host": "aliexpress-datahub.p.rapidapi.com"
    }

    print(f"✅ USANDO API DE ALIEXPRESS PARA: {nombre_producto}")
    logger.info(f"=> Empezando búsqueda de '{nombre_producto}' en AliExpress mediante API")

    resultados = []
    try:
        response = requests.get(url, headers=headers, params=querystring, timeout=15)
        response.raise_for_status()
        data = response.json()

        # La respuesta puede venir en distintos campos según la API y el plan
        items = (
            data.get("result", {}).get("resultList", [])
            or data.get("result", {}).get("items", [])
            or data.get("data", {}).get("products", [])
            or data.get("items", [])
            or []
        )

        for raw in items[:LIMITE_PRODUCTOS]:
            try:
                # Algunas APIs envuelven el producto en un sub-objeto "item"
                info = raw.get("item", raw)

                nombre = (
                    info.get("title") or info.get("product_title") or "Producto AliExpress"
                )[:80]

                # Precio: probamos distintas rutas según la versión de la API
                precio_raw = (
                    info.get("sku", {}).get("def", {}).get("promotionPrice")
                    or info.get("sku", {}).get("def", {}).get("price")
                    or info.get("price", {}).get("minPrice", {}).get("formattedPrice")
                    or info.get("salePrice")
                    or info.get("product_price")
                )
                if not precio_raw:
                    continue
                precio_num = re.sub(r"[^\d.,]", "", str(precio_raw)).strip()
                if not precio_num:
                    continue
                precio = f"{precio_num} EUR"

                imagen = (
                    info.get("image") or info.get("imageUrl") or
                    info.get("mainImageUrl") or info.get("product_photo") or LOGO_ALIEXPRESS
                )
                if imagen.startswith("//"):
                    imagen = "https:" + imagen

                item_id = info.get("itemId") or info.get("productId") or info.get("item_id", "")
                link = (
                    info.get("itemDetailUrl") or info.get("productUrl") or
                    info.get("product_url") or
                    (f"https://es.aliexpress.com/item/{item_id}.html" if item_id else "")
                )
                if not link:
                    continue

                estrellas = (
                    info.get("evaluationInfo", {}).get("averageStar") or
                    info.get("starRating") or info.get("product_star_rating") or ""
                )
                votos = info.get("product_num_ratings", "")
                if estrellas and votos:
                    valoracion = f"⭐ {estrellas} ({votos} val.)"
                elif estrellas:
                    valoracion = f"⭐ {estrellas}"
                else:
                    valoracion = "Sin opiniones"

                resultados.append({
                    'nombre': nombre,
                    'tienda': 'AliExpress',
                    'precio': precio,
                    'link': link,
                    'imagen': imagen,
                    'stock': True,
                    'valoracion': valoracion
                })
            except Exception as e:
                logger.warning(f"Error parseando producto AliExpress: {e}")
                continue

    except Exception as e:
        logger.error(f"Error en API de AliExpress: {e}", exc_info=True)

    return resultados
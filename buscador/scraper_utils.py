import requests
from bs4 import BeautifulSoup
import re

def get_soup(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept-Language": "es-ES,es;q=0.9",
        "Referer": "https://www.google.com/", # Simulamos que venimos de buscar en Google
    }
    
    try:
        # Añadimos un pequeño retraso para no parecer tan bot
        response = requests.get(url, headers=headers, timeout=15)
        if response.status_code == 200:
            return BeautifulSoup(response.text, 'html.parser')
        else:
            print(f"Error de estado: {response.status_code}")
            return None
    except Exception as e:
        print(f"Error de conexión: {e}")
        return None

def extraer_precio(item):
    precio_str = str(item.get('precio', 'Consultar'))
    if 'Consultar' in precio_str:
        return 999999.0
    numeros = re.sub(r'[^\d.,]', '', precio_str)
    if not numeros: return 999999.0
    if '.' in numeros and ',' in numeros:
        if numeros.rfind(',') > numeros.rfind('.'):
            numeros = numeros.replace('.', '').replace(',', '.')
        else:
            numeros = numeros.replace(',', '')
    elif ',' in numeros:
        numeros = numeros.replace(',', '.')
    try: return float(numeros)
    except: return 999999.0
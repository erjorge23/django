from bs4 import BeautifulSoup
import json

with open('carrefour_test.html', 'r', encoding='utf-8') as f:
    soup = BeautifulSoup(f, 'html.parser')
    res = soup.select('.product-card__title, .product-card__price')
    print('Carrefour CSS match:', len(res))
    
    # Alternatively Carrefour might use JSON in scripts
    scripts = soup.find_all('script')
    for s in scripts:
        if s.string and '__NUXT__' in s.string:
            print('Found Nuxt data in Carrefour!')
            
with open('fnac_test.html', 'r', encoding='utf-8') as f2:
    soup2 = BeautifulSoup(f2, 'html.parser')
    res2 = soup2.select('.Article-title, .Article-price')
    print('Fnac CSS match:', len(res2))

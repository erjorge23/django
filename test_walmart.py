import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
import django
django.setup()

from buscador.scrapers import RAPIDAPI_KEY
import requests
import json

def test_walmart():
    print("API KEY starts with:", RAPIDAPI_KEY[:5] if RAPIDAPI_KEY else "None")
    
    url = "https://axesso-walmart-data-service.p.rapidapi.com/wlm/walmart-search-by-keyword"
    querystring = {"keyword": "iphone", "page": "1", "sortBy": "best_match"}
    headers = {
        "x-rapidapi-key": RAPIDAPI_KEY,
        "x-rapidapi-host": "axesso-walmart-data-service.p.rapidapi.com"
    }

    try:
        response = requests.get(url, headers=headers, params=querystring)
        print("Status Code:", response.status_code)
        
        if response.status_code != 200:
            print("Response:", response.text)
        else:
            data = response.json()
            items = data.get("item", {}).get("props", {}).get("pageProps", {}).get("initialData", {}).get("searchResult", {}).get("itemResults", [])
            print("Items length:", len(items))
            if not items:
                print("Fallback items:", len(data.get("data", {}).get("items", []) or data.get("items", [])))
                print("First 200 chars of JSON dict keys:", list(data.keys()))
    except Exception as e:
        print("Error:", e)

if __name__ == "__main__":
    test_walmart()

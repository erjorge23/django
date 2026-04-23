import time
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
import django
django.setup()

from buscador.scrapers import get_driver

def test_sites():
    driver = get_driver()
    try:
        driver.get("https://www.fnac.es/SearchResult/ResultList.aspx?Search=iphone")
        time.sleep(4)
        print("FNAC title:", driver.title)
        with open("fnac_test.html", "w", encoding="utf-8") as f:
            f.write(driver.page_source)

        driver.get("https://www.carrefour.es/?q=iphone")
        time.sleep(4)
        print("Carrefour title:", driver.title)
        with open("carrefour_test.html", "w", encoding="utf-8") as f:
            f.write(driver.page_source)
    except Exception as e:
        print("Error:", e)
    finally:
        driver.quit()

if __name__ == "__main__":
    test_sites()

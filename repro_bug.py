from buscador.scraper_utils import extraer_precio

def test():
    cases = [
        ("1.200,50 EUR", 1200.50),
        ("1.200 EUR", 1200.0),
        ("9,99 EUR", 9.99),
        ("1.200,50 €", 1200.50),
        ("1200.50 EUR", 1200.50),
    ]

    for input_str, expected in cases:
        item = {'precio': input_str}
        result = extraer_precio(item)
        print(f"Input: {input_str} => Result: {result} (Expected: {expected})")
        if result != expected:
            print(f"  ❌ FAILED: {result} != {expected}")
        else:
            print(f"  ✅ PASSED")

if __name__ == "__main__":
    test()

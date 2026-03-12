import re

def extraer_precio(item):
    precio_str = str(item.get('precio', 'Consultar'))
    if 'Consultar' in precio_str:
        return 999999.0
    
    # Quitamos símbolos de moneda y espacios
    numeros = re.sub(r'[^\d.,]', '', precio_str)
    if not numeros: 
        return 999999.0

    # Lógica para detectar miles vs decimales (Heurística europea/española)
    # 1.200,50 -> Si hay ambos, el último es el decimal
    if '.' in numeros and ',' in numeros:
        if numeros.rfind(',') > numeros.rfind('.'):
            # Formato 1.200,50
            numeros = numeros.replace('.', '').replace(',', '.')
        else:
            # Formato 1,200.50
            numeros = numeros.replace(',', '').replace('.', '.')
    
    # 1.200 -> Si solo hay punto, miramos cuántos dígitos siguen
    elif '.' in numeros:
        # Si hay más de un punto, son separadores de miles: 1.000.000
        if numeros.count('.') > 1:
            numeros = numeros.replace('.', '')
        else:
            partes = numeros.split('.')
            # Si después del punto hay exactamente 3 dígitos, es probable que sea miles (ej: 1.200)
            if len(partes[1]) == 3:
                numeros = numeros.replace('.', '')
            else:
                # Caso ej: 12.50 -> decimal
                pass

    # 1,200 -> Si solo hay coma
    elif ',' in numeros:
        # Si hay más de una coma, son miles: 1,000,000
        if numeros.count(',') > 1:
            numeros = numeros.replace(',', '')
        else:
            partes = numeros.split(',')
            # Misma lógica que con el punto para el formato español
            if len(partes[1]) == 3:
                numeros = numeros.replace(',', '')
            else:
                numeros = numeros.replace(',', '.')

    try: 
        return float(numeros)
    except: 
        return 999999.0

def test():
    cases = [
        ("1.279,00 EUR", 1279.0),
        ("1.359,00 EUR", 1359.0),
        ("1.200 EUR", 1200.0),
        ("1.200,50 EUR", 1200.5),
        ("1,200.50 EUR", 1200.5),
        ("9,99 EUR", 9.99),
        ("12.50 EUR", 12.5),
        ("1.200 €", 1200.0),
        ("1200 €", 1200.0),
        ("1.000.000 €", 1000000.0),
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

from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.core.cache import cache
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from .forms import BusquedaProductoForm, RegistroForm
from .models import Producto
from .scrapers import buscar_en_ebay, buscar_en_amazon, buscar_en_wallapop, obtener_estrellas_wallapop, buscar_en_aliexpress
from .scraper_utils import extraer_precio

import re
import concurrent.futures
import hashlib

def signup(request):
    if request.method == 'POST':
        form = RegistroForm(request.POST) 
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
    else:
        form = RegistroForm()
    return render(request, 'registration/signup.html', {'form': form})

@login_required(login_url='login') 
def home(request):
    form = BusquedaProductoForm()
    busqueda = request.GET.get('q', "").strip()
    resultados_finales = []

    if busqueda:
        cache_key = f"search_secure_v2_{busqueda.replace(' ', '_')}"
        resultados_finales = cache.get(cache_key)

        if not resultados_finales:
            with concurrent.futures.ThreadPoolExecutor() as executor:
                f_ebay = executor.submit(buscar_en_ebay, busqueda)
                f_amz = executor.submit(buscar_en_amazon, busqueda)
                f_wa = executor.submit(buscar_en_wallapop, busqueda)
                f_ali = executor.submit(buscar_en_aliexpress, busqueda)
                
                try: res_ebay = f_ebay.result(timeout=25)
                except: res_ebay = []
                
                try: res_amz = f_amz.result(timeout=25)
                except: res_amz = []
                
                try: res_wa = f_wa.result(timeout=25)
                except: res_wa = []

                try: res_ali = f_ali.result(timeout=25)
                except: res_ali = []

            resultados_finales = res_ebay + res_amz + res_wa + res_ali
            
            resultados_finales.sort(key=extraer_precio)
            
            for item in resultados_finales:
                try:
                    if not Producto.objects.filter(link=item['link']).exists():
                        Producto.objects.create(
                            nombre=item['nombre'],
                            tienda=item['tienda'],
                            precio=item['precio'],
                            link=item['link'],
                            imagen=item.get('imagen', ''),
                            valoracion=item['valoracion'],
                            tiene_stock=item['stock']
                        )
                except Exception as e:
                    print(f"Error guardando en BD: {e}")
            
            cache.set(cache_key, resultados_finales, 600)

    paginator = Paginator(resultados_finales, 21)
    page_obj = paginator.get_page(request.GET.get('page'))

    return render(request, 'buscar.html', {'form': form, 'resultados': page_obj, 'busqueda': busqueda})

def api_get_wallapop_stars(request):
    url = request.GET.get('url')
    if not url: return JsonResponse({'stars': 'Error'})
    url_hash = hashlib.md5(url.encode()).hexdigest()
    key = f"star_{url_hash}"
    stars = cache.get(key)
    if not stars:
        stars = obtener_estrellas_wallapop(url)
        cache.set(key, stars, 3600)
    return JsonResponse({'stars': stars})
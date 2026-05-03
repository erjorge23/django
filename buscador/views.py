from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.core.cache import cache
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from .forms import BusquedaProductoForm, RegistroForm
from .models import Producto, Favorito
from .scrapers import buscar_en_ebay, buscar_en_amazon, buscar_en_wallapop, obtener_estrellas_wallapop, buscar_en_aliexpress, buscar_en_walmart
from .scraper_utils import extraer_precio

import re
import json
from django.views.decorators.http import require_POST

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

# Vista principal: gestiona la búsqueda paralela en múltiples tiendas y cachea resultados
@login_required(login_url='login') 
def home(request):
    form = BusquedaProductoForm()
    busqueda = request.GET.get('q', "").strip()
    resultados_finales = []

    if busqueda:
        cache_key = f"search_secure_v2_{busqueda.replace(' ', '_')}"
        resultados_finales = cache.get(cache_key)

        if resultados_finales:
            for item in resultados_finales:
                if 'precio_num' not in item:
                    item['precio_num'] = extraer_precio(item)
            resultados_finales.sort(key=lambda x: x.get('precio_num', 999999.0))

        if not resultados_finales:
            with concurrent.futures.ThreadPoolExecutor() as executor:
                f_ebay = executor.submit(buscar_en_ebay, busqueda)
                f_amz = executor.submit(buscar_en_amazon, busqueda)
                f_wa = executor.submit(buscar_en_wallapop, busqueda)
                f_ali = executor.submit(buscar_en_aliexpress, busqueda)
                f_wal = executor.submit(buscar_en_walmart, busqueda)
                
                try: res_ebay = f_ebay.result(timeout=25)
                except: res_ebay = []
                
                try: res_amz = f_amz.result(timeout=25)
                except: res_amz = []
                
                try: res_wa = f_wa.result(timeout=25)
                except: res_wa = []

                try: res_ali = f_ali.result(timeout=25)
                except: res_ali = []

                try: res_wal = f_wal.result(timeout=25)
                except: res_wal = []

            resultados_finales = res_ebay + res_amz + res_wa + res_ali + res_wal
            
            for item in resultados_finales:
                item['precio_num'] = extraer_precio(item)

            resultados_finales.sort(key=lambda x: x['precio_num'])
            
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
            
        favoritos_links = []
        if request.user.is_authenticated:
            favoritos_links = list(Favorito.objects.filter(user=request.user).values_list('producto__link', flat=True))

    return render(request, 'buscar.html', {
        'form': form,
        'resultados': resultados_finales,
        'busqueda': busqueda,
        'total': len(resultados_finales),
        'favoritos_links': favoritos_links if busqueda else []
    })

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
# API endpoint para marcar o desmarcar un producto de la lista de favoritos del usuario
@login_required(login_url='login')
@require_POST
def toggle_favorito(request):
    try:
        data = json.loads(request.body)
        link = data.get('link')
        if not link:
            return JsonResponse({'status': 'error', 'message': 'Falta el enlace'}, status=400)
            
        producto = Producto.objects.filter(link=link).first()
        if not producto:
            return JsonResponse({'status': 'error', 'message': 'Producto no encontrado'}, status=404)
            
        fav, created = Favorito.objects.get_or_create(user=request.user, producto=producto)
        
        if not created:
            fav.delete()
            return JsonResponse({'status': 'removed'})
        else:
            return JsonResponse({'status': 'added'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

@login_required(login_url='login')
def lista_favoritos(request):
    favoritos = Favorito.objects.filter(user=request.user).select_related('producto').order_by('-fecha_agregado')
    return render(request, 'favoritos.html', {'favoritos': favoritos})

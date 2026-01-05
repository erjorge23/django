from django.contrib import admin
from django.urls import path, include  
from buscador import views

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # 1. Rutas de Autenticación de Django (Login, Logout, Reset password...)
    path('accounts/', include('django.contrib.auth.urls')),
    
    # 2. Ruta para Registrarse (Signup)
    path('signup/', views.signup, name='signup'),

    # 3. Tu buscador (Home) y la API
    path('', views.home, name='home'),
    path('api/get-stars/', views.api_get_wallapop_stars, name='get_stars'),
]
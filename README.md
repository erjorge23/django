# CompaRadar 🛒🔍

CompaRadar es un motor de búsqueda y comparación de precios que te permite buscar productos y ver sus precios simultáneamente en grandes plataformas como eBay, Amazon, AliExpress, Wallapop y Walmart. Todo desde una interfaz unificada.

## 🚀 Requisitos Previos

Asegúrate de tener instalado en tu sistema:
- [Python 3.8 o superior](https://www.python.org/downloads/)
- Pip (Gestor de paquetes de Python)
- Git (Opcional, para clonar el repositorio)

## 🛠️ Instalación y Configuración

Sigue estos pasos para ejecutar el proyecto en tu dispositivo local:

### 1. Obtener el proyecto
Descarga los archivos del proyecto a tu ordenador y abre una terminal (o consola de comandos) en la carpeta principal del proyecto (la carpeta donde se encuentra el archivo `manage.py`).

### 2. Crear un entorno virtual (Recomendado)
Es una muy buena práctica usar un entorno virtual para aislar las dependencias del proyecto:
```bash
python -m venv venv
```

**Activa el entorno virtual:**
- En **Windows**:
  ```bash
  venv\Scripts\activate
  ```
- En **macOS y Linux**:
  ```bash
  source venv/bin/activate
  ```

### 3. Instalar las dependencias
Con el entorno virtual activado, instala todas las librerías necesarias con el siguiente comando:
```bash
pip install -r requirements.txt
```

### 4. Configurar las variables de entorno
El proyecto utiliza APIs que requieren credenciales secretas. En la carpeta raíz (junto a `manage.py`), debes crear un archivo llamado `.env` e introducir tus claves:

```ini
# Credenciales para la API oficial de eBay
EBAY_APP_ID=tu_app_id_aqui
EBAY_CERT_ID=tu_cert_id_aqui

# Credenciales para RapidAPI (Necesario para buscar en Walmart)
RAPIDAPI_KEY=tu_rapidapi_key_aqui

# Clave secreta de Django (puedes inventar cualquier cadena de texto segura)
SECRET_KEY=django-insecure-tu_clave_secreta_aqui
```
*(Nota: Si no configuras las APIs, las búsquedas de eBay y Walmart simplemente no devolverán resultados, pero el resto de los scrapers como Wallapop o AliExpress seguirán funcionando con normalidad).*

### 5. Preparar la Base de Datos
Aplica las migraciones para crear las tablas necesarias en la base de datos local (SQLite):
```bash
python manage.py migrate
```

### 6. Iniciar el servidor
Por último, arranca el servidor web local:
```bash
python manage.py runserver
```

## 💻 Cómo usar la aplicación

1. Abre tu navegador web y ve a `http://127.0.0.1:8000/`.
2. La plataforma requiere autenticación, por lo que debes **Crear una cuenta** e iniciar sesión.
3. Una vez dentro, introduce el nombre del producto que buscas en la barra principal.
4. **Importante:** El sistema realiza peticiones web concurrentes (multithreading). La primera vez que buscas un producto puede tardar entre **10 y 25 segundos** mientras extrae los datos en tiempo real de todas las tiendas.
5. Los resultados se mostrarán ordenados automáticamente por precio y podrás añadirlos a tu lista de **Favoritos** haciendo clic en el icono del corazón. Las búsquedas recientes quedan almacenadas en **caché** durante 10 minutos para que al volver a buscar el mismo producto cargue instantáneamente.
import csv
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options  # ¡NUEVA HERRAMIENTA!
from bs4 import BeautifulSoup
import time


def buscar_desde_archivo(nombre_archivo):
    print(f"Iniciando el robot de forma silenciosa...")

    # --- NUEVA CONFIGURACIÓN PARA OCULTAR CHROME ---
    opciones = Options()
    opciones.add_argument("--headless")  # Esto oculta la ventana gráfica
    opciones.add_argument("--disable-gpu")  # Recomendado en Windows para evitar errores
    opciones.add_argument("--window-size=1920,1080")  # Simula una pantalla normal internamente

    # ¡NUEVAS LÍNEAS! Obligatorias para que Chrome no explote en GitHub Actions
    opciones.add_argument('--no-sandbox')
    opciones.add_argument('--disable-dev-shm-usage')

    # 1. Preparamos el navegador pasándole nuestras opciones ocultas
    servicio = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=servicio, options=opciones)

    # 2. Abrimos y leemos el archivo CSV
    try:
        # (Asegúrate de usar 'utf-8-sig' y el delimitador correcto según lo que descubriste de tu Excel)
        with open(nombre_archivo, mode="r", encoding="utf-8-sig") as archivo:
            lector_csv = csv.DictReader(archivo, delimiter=";")  # Cambia a ',' si es necesario

            # 3. EL BUCLE
            for fila in lector_csv:
                nombre_tienda = fila["Tienda"]
                url_producto = fila["URL"]

                print(f"Consultando en {nombre_tienda}...")

                driver.get(url_producto)
                time.sleep(5)

                sopa = BeautifulSoup(driver.page_source, "html.parser")

                # --- LÓGICA ESPECÍFICA PARA MAKRO ---
                if nombre_tienda == "Makro":
                    try:
                        # 1. El nombre se mantiene igual (es estable)
                        nombre = sopa.find("div", class_="productName").text.strip()

                        # 2. MEJORA: Buscamos específicamente la caja del precio regular
                        caja_precio_regular = sopa.find("div", class_="MakroPrice_Regular")

                        # Extraemos el precio solo de esa caja
                        etiqueta_decimal = caja_precio_regular.find("span", class_="decimal-price")
                        precio = etiqueta_decimal.parent.text.strip()

                        print(f"  -> Éxito: {nombre} | {precio}")
                    except Exception as e:
                        print(f"  -> Error: No se pudo extraer de Makro. Detalles: {e}")

                # --- LÓGICA METRO ---
                elif nombre_tienda == "Metro":
                    try:
                        nombre = sopa.find("span", class_="vtex-store-components-3-x-productBrand").text.strip()
                        entero = sopa.find("span", class_="vtex-product-price-1-x-currencyInteger").text.strip()
                        decimal = sopa.find("span", class_="vtex-product-price-1-x-currencyFraction").text.strip()
                        precio = f"S/ {entero}.{decimal}"
                        print(f"  -> Éxito: {nombre} | {precio}")
                    except Exception:
                        print("  -> Error: No se pudo extraer de Metro.")

                # --- LÓGICA ESPECÍFICA PARA TOTTUS ---
                elif nombre_tienda == "Tottus":
                    try:
                        # 1. Usamos solo la clase estable del título (ignoramos el jsx-)
                        nombre = sopa.find("h1", class_="pdp-basic-info__product-name").text.strip()

                        # 2. Buscamos la lista de precios estable y luego el primer span con clase 'copy12'
                        caja_precios = sopa.find("ol", class_="pdp-prices")
                        etiqueta_precio = caja_precios.find("span", class_="copy12")

                        precio = etiqueta_precio.text.strip()

                        print(f"  -> Éxito: {nombre} | {precio}")
                    except Exception as e:
                        print(
                            f"  -> Error: No se pudo extraer de Tottus. Detalles: {e}"
                        )

                # --- LÓGICA VEGA ---
                elif nombre_tienda == "Vega":
                    try:
                        # 1. Extraemos el nombre usando la clase estándar de VTEX
                        nombre_encontrado = sopa.find("span", class_="vtex-store-components-3-x-productBrand").text.strip()

                        # 2. Apuntamos al 'sellingPriceValue' para evitar el precio tachado
                        etiqueta_precio = sopa.find("span", class_="vtex-product-price-1-x-sellingPriceValue")

                        # VTEX suele inyectar un carácter invisible (&nbsp;) entre el "S/" y el número.
                        # Lo reemplazamos por un espacio normal para que tu Excel quede limpio.
                        precio_encontrado = etiqueta_precio.text.replace("\xa0", " ").strip()

                        print(f"  -> Éxito: {nombre_encontrado} | {precio_encontrado}")
                    except Exception as e:
                        print(f"  -> Error interno en Vega: {e}")

                # --- LÓGICA TAMBO ---
                elif nombre_tienda == "Tambo":
                    try:
                        # 1. El nombre siempre es el título principal de la página (h1)
                        nombre_encontrado = sopa.find("h1").text.strip()

                        # 2. Buscamos la cajita exacta que dice "Agregar"
                        caja_agregar = sopa.find("div", string="Agregar")

                        # 3. Extraemos el texto del 'hermano' que le sigue (el precio)
                        precio_encontrado = caja_agregar.find_next_sibling("div").text.strip()

                        # El ansiado print de éxito para monitorear en la consola negra
                        print(f"  -> Éxito: {nombre_encontrado} | {precio_encontrado}")

                    except Exception as e:
                        print(f"  -> Error interno en Tambo: {e}")

                print("-" * 40)

    except FileNotFoundError:
        print(f"¡Error! No se encontró el archivo.")

    # 4. Cerramos el navegador fantasma
    driver.quit()
    print("\n¡Búsqueda masiva finalizada con éxito!")


# Ejecutamos
buscar_desde_archivo("productos.csv")
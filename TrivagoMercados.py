import csv
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import time
from datetime import datetime

def buscar_y_guardar(archivo_entrada, archivo_salida):
    print("Iniciando el robot rastreador en la nube...")

    # --- CONFIGURACIÓN PARA SERVIDORES EN LA NUBE ---
    opciones = Options()
    opciones.add_argument("--headless")
    opciones.add_argument("--disable-gpu")
    opciones.add_argument("--window-size=1920,1080")
    opciones.add_argument('--no-sandbox')
    opciones.add_argument('--disable-dev-shm-usage')

    servicio = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=servicio, options=opciones)

    # Nuestra caja para guardar las ofertas
    resultados_finales = []

    try:
        with open(archivo_entrada, mode="r", encoding="utf-8-sig") as archivo:
            lector_csv = csv.DictReader(archivo, delimiter=";") 

            for fila in lector_csv:
                nombre_tienda = fila["Tienda"]
                url_producto = fila["URL"]

                print(f"Consultando en {nombre_tienda}...")
                driver.get(url_producto)
                time.sleep(5)

                sopa = BeautifulSoup(driver.page_source, "html.parser")
                
                # Valores por defecto
                nombre_encontrado = "No disponible"
                precio_encontrado = "Agotado/Error"

                # --- LÓGICA MAKRO ---
                if nombre_tienda == "Makro":
                    try:
                        nombre_encontrado = sopa.find("div", class_="productName").text.strip()
                        caja_precio_regular = sopa.find("div", class_="MakroPrice_Regular")
                        etiqueta_decimal = caja_precio_regular.find("span", class_="decimal-price")
                        precio_encontrado = etiqueta_decimal.parent.text.strip()
                    except Exception as e:
                        print(f"  -> Error Makro: {e}")

                # --- LÓGICA METRO ---
                elif nombre_tienda == "Metro":
                    try:
                        nombre_encontrado = sopa.find("span", class_="vtex-store-components-3-x-productBrand").text.strip()
                        entero = sopa.find("span", class_="vtex-product-price-1-x-currencyInteger").text.strip()
                        decimal = sopa.find("span", class_="vtex-product-price-1-x-currencyFraction").text.strip()
                        precio_encontrado = f"S/ {entero}.{decimal}"
                    except Exception as e:
                        print(f"  -> Error Metro: {e}")

                # --- LÓGICA TOTTUS ---
                elif nombre_tienda == "Tottus":
                    try:
                        nombre_encontrado = sopa.find("h1", class_="pdp-basic-info__product-name").text.strip()
                        caja_precios = sopa.find("ol", class_="pdp-prices")
                        etiqueta_precio = caja_precios.find("span", class_="copy12")
                        precio_encontrado = etiqueta_precio.text.strip()
                    except Exception as e:
                        print(f"  -> Error Tottus: {e}")

                # --- LÓGICA VEGA ---
                elif nombre_tienda == "Vega":
                    try:
                        nombre_encontrado = sopa.find("span", class_="vtex-store-components-3-x-productBrand").text.strip()
                        etiqueta_precio = sopa.find("span", class_="vtex-product-price-1-x-sellingPriceValue")
                        precio_encontrado = etiqueta_precio.text.replace("\xa0", " ").strip()
                    except Exception as e:
                        print(f"  -> Error Vega: {e}")

                # --- LÓGICA TAMBO ---
                elif nombre_tienda == "Tambo":
                    try:
                        nombre_encontrado = sopa.find("h1").text.strip()
                        caja_agregar = sopa.find("div", string="Agregar")
                        precio_encontrado = caja_agregar.find_next_sibling("div").text.strip()
                    except Exception as e:
                        print(f"  -> Error Tambo: {e}")

                # Mostramos el éxito en consola y lo guardamos en la lista
                print(f"  -> Éxito: {nombre_encontrado} | {precio_encontrado}")
                print("-" * 40)
                
                resultados_finales.append({
                    "Fecha_Hora": datetime.now().strftime("%Y-%m-%d %H:%M"),
                    "Tienda": nombre_tienda,
                    "Producto": nombre_encontrado,
                    "Precio": precio_encontrado,
                    "Enlace": url_producto
                })

    except FileNotFoundError:
        print(f"¡Error! No se encontró el archivo de enlaces.")

    driver.quit()

    # --- LA MAGIA: EXPORTAR A EXCEL (CSV) ---
    print(f"\nGuardando {len(resultados_finales)} ofertas en tu archivo CSV...")
    
    with open(archivo_salida, mode='w', encoding='utf-8-sig', newline='') as archivo_final:
        campos = ["Fecha_Hora", "Tienda", "Producto", "Precio", "Enlace"]
        escritor = csv.DictWriter(archivo_final, fieldnames=campos, delimiter=';')
        
        escritor.writeheader()
        escritor.writerows(resultados_finales)

    print(f"¡Éxito! Archivo guardado como '{archivo_salida}'.")

# Ejecutamos con la función de guardar
buscar_y_guardar("productos.csv", "resultados_ofertas.csv")

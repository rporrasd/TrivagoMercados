import streamlit as st
import pandas as pd

# 1. Configuración de la página web
st.set_page_config(page_title="Mi Trivago Mercados", page_icon="🛒", layout="wide")

st.title("🛒 Mi Trivago de Supermercados")
st.write("Bienvenido a tu panel de control de precios. El robot actualiza estos datos todos los días a las 6:00 AM.")

# 2. Intentamos leer el archivo que creó el robot
try:
    # Leemos el CSV (pandas entiende automáticamente nuestro delimitador ';')
    df = pd.read_csv("resultados_ofertas.csv", sep=";", encoding="utf-8-sig")
    
    # 3. Panel de Resumen (Métricas)
    st.subheader("📊 Resumen del día")
    
    total_productos = len(df)
    tiendas_unicas = df["Tienda"].nunique()
    ultima_actualizacion = df["Fecha_Hora"].iloc[0] if not df.empty else "Desconocida"
    
    # Creamos 3 columnas visuales
    col1, col2, col3 = st.columns(3)
    col1.metric("Productos Escaneados", total_productos)
    col2.metric("Tiendas Monitoreadas", tiendas_unicas)
    col3.metric("Última Actualización", ultima_actualizacion)
    
    st.markdown("---")
    
    # 4. Buscador y Filtros Interactivos
    st.subheader("🔍 Buscador de Ofertas")
    
    # Filtro múltiple por tienda
    lista_tiendas = df["Tienda"].unique()
    tiendas_seleccionadas = st.multiselect("Filtrar por supermercado:", lista_tiendas, default=lista_tiendas)
    
    # Buscador de texto libre
    busqueda = st.text_input("Buscar producto (ej. Arroz, Gloria, Primor):")
    
    # Aplicamos los filtros a los datos
    df_filtrado = df[df["Tienda"].isin(tiendas_seleccionadas)]
    if busqueda:
        # Filtramos ignorando mayúsculas y minúsculas
        df_filtrado = df_filtrado[df_filtrado["Producto"].str.contains(busqueda, case=False, na=False)]
    
    # 5. Mostramos la tabla final limpia
    # Ocultamos el índice y permitimos que la tabla ocupe todo el ancho
    st.dataframe(df_filtrado[["Tienda", "Producto", "Precio", "Fecha_Hora"]], use_container_width=True, hide_index=True)

except FileNotFoundError:
    st.warning("⚠️ El robot aún no ha generado el archivo de resultados. Espera a que termine su primer ciclo.")
except Exception as e:
    st.error(f"Ocurrió un error al cargar los datos: {e}")
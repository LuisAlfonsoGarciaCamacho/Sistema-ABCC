import streamlit as st
import requests
import pandas as pd
import sqlite3
import os
from datetime import datetime

BASE_URL = "http://localhost:8000"

def main():
    """
    Main function to run the Streamlit application.

    This function sets up the main page structure and handles navigation between different operations.
    """
    st.title("Sistema ABCC de Artículos")

    menu = ["Alta", "Baja", "Cambio", "Consulta", "Generar CSV"]
    choice = st.sidebar.selectbox("Seleccione una opción", menu, key="menu")

    if choice == "Alta":
        alta_articulo()
    elif choice == "Baja":
        baja_articulo()
    elif choice == "Cambio":
        cambio_articulo()
    elif choice == "Consulta":
        consulta_articulo()
    elif choice == "Generar CSV":
        generar_csv()

def get_departamentos():
    """
    Fetches the list of departments from the API.

    Returns:
        list: A list of department dictionaries if successful, empty list otherwise.
    """
    response = requests.get(f"{BASE_URL}/departamentos/")
    if response.status_code == 200:
        return response.json()
    else:
        st.error("Error al obtener departamentos")
        return []

def get_clases(departamento_numero):
    """
    Fetches the list of classes for a given department from the API.

    Args:
        departamento_numero (int): The department number.

    Returns:
        list: A list of class dictionaries if successful, empty list otherwise.
    """
    response = requests.get(f"{BASE_URL}/clases/{departamento_numero}")
    if response.status_code == 200:
        return response.json()
    elif response.status_code == 404:
        st.warning(f"No se encontraron clases para el departamento {departamento_numero}")
        return []
    else:
        st.error(f"Error al obtener clases para el departamento {departamento_numero}")
        return []

def get_familias(departamento_numero, clase_numero):
    """
    Fetches the list of families for a given department and class from the API.

    Args:
        departamento_numero (int): The department number.
        clase_numero (int): The class number.

    Returns:
        list: A list of family dictionaries if successful, empty list otherwise.
    """
    response = requests.get(f"{BASE_URL}/familias/{departamento_numero}/{clase_numero}")
    if response.status_code == 200:
        return response.json()
    elif response.status_code == 404:
        st.warning(f"No se encontraron familias para el departamento {departamento_numero} y clase {clase_numero}")
        return []
    else:
        st.error(f"Error al obtener familias para el departamento {departamento_numero} y clase {clase_numero}")
        return []

def alta_articulo():
    """
    Handles the process of adding a new article to the system.

    This function creates a form for inputting article details and sends the data to the API.
    """
    st.subheader("Alta de Artículo")
    sku = st.text_input("SKU", max_chars=6, key="alta_sku")
    
    if sku:
        response = requests.get(f"{BASE_URL}/articulos/{sku}")
        if response.status_code == 200:
            st.error("El SKU ya existe")
        else:
            articulo = st.text_input("Artículo", max_chars=15, key="alta_articulo")
            marca = st.text_input("Marca", max_chars=15, key="alta_marca")
            modelo = st.text_input("Modelo", max_chars=20, key="alta_modelo")
            
            departamentos = get_departamentos()
            departamento = st.selectbox(
                "Departamento", 
                options=[d['numero'] for d in departamentos], 
                format_func=lambda x: next(d['nombre'] for d in departamentos if d['numero'] == x), 
                key="alta_departamento"
            )
            
            clases = get_clases(departamento) if departamento else []
            clase = st.selectbox(
                "Clase", 
                options=[c['numero'] for c in clases], 
                format_func=lambda x: next(c['nombre'] for c in clases if c['numero'] == x),
                key="alta_clase"
            )
            
            familias = get_familias(departamento, clase) if departamento and clase else []
            familia = st.selectbox(
                "Familia", 
                options=[f['numero'] for f in familias], 
                format_func=lambda x: next(f['nombre'] for f in familias if f['numero'] == x),
                key="alta_familia"
            )
            
            stock = st.number_input("Stock", min_value=0, max_value=999999999, key="alta_stock")
            cantidad = st.number_input("Cantidad", min_value=0, max_value=stock, key="alta_cantidad")

            if st.button("Guardar", key="alta_guardar"):
                # Extract the last two digits of clase
                clase_dos_digitos = str(clase)[-2:] if clase else None
                
                data = {
                    "sku": sku,
                    "articulo": articulo,
                    "marca": marca,
                    "modelo": modelo,
                    "departamento_numero": departamento,
                    "clase_numero": clase_dos_digitos,  # Send only the last two digits
                    "familia_numero": familia,
                    "stock": stock,
                    "cantidad": cantidad
                }
                st.write("Datos a enviar:", data)  # Print data for verification
                response = requests.post(f"{BASE_URL}/articulos/", json=data)
                if response.status_code == 200:
                    st.success("Artículo guardado exitosamente")
                else:
                    st.error("Error al guardar el artículo")
                    st.write("Código de estado:", response.status_code)  # Print status code
                    st.write("Respuesta del servidor:", response.text)  # Print server response

def baja_articulo():
    """
    Handles the process of deleting an article from the system.

    This function allows searching for an article by SKU and confirms deletion.
    """
    st.subheader("Baja de Artículo")
    sku = st.text_input("SKU", max_chars=6, key="baja_sku")
    
    if sku:
        response = requests.get(f"{BASE_URL}/articulos/{sku}")
        if response.status_code == 200:
            articulo = response.json()
            st.write(articulo)
            if st.button("Eliminar", key="baja_eliminar"):
                confirm = st.checkbox("¿Está seguro de eliminar este artículo?", key="baja_confirm")
                if confirm:
                    response = requests.delete(f"{BASE_URL}/articulos/{sku}")
                    if response.status_code == 200:
                        st.success("Artículo eliminado exitosamente")
                    else:
                        st.error("Error al eliminar el artículo")
        else:
            st.error("El SKU no existe")

def cambio_articulo():
    """
    Handles the process of modifying an existing article in the system.

    This function allows searching for an article by SKU and updating its details.
    """
    st.subheader("Cambio de Artículo")
    sku = st.text_input("SKU", max_chars=6, key="cambio_sku")
    
    if sku:
        response = requests.get(f"{BASE_URL}/articulos/{sku}")
        if response.status_code == 200:
            articulo = response.json()
            articulo_update = {}
            
            articulo_update["articulo"] = st.text_input("Artículo", value=articulo["articulo"], max_chars=15, key="cambio_articulo")
            articulo_update["marca"] = st.text_input("Marca", value=articulo["marca"], max_chars=15, key="cambio_marca")
            articulo_update["modelo"] = st.text_input("Modelo", value=articulo["modelo"], max_chars=20, key="cambio_modelo")
            
            departamentos = get_departamentos()
            articulo_update["departamento_numero"] = st.selectbox(
                "Departamento", 
                options=[d['numero'] for d in departamentos], 
                format_func=lambda x: next(d['nombre'] for d in departamentos if d['numero'] == x), 
                index=[d['numero'] for d in departamentos].index(articulo["departamento_numero"]),
                key="cambio_departamento"
            )
            
            clases = get_clases(articulo_update["departamento_numero"])
            clase_actual = articulo["clase_numero"]
            articulo_update["clase_numero"] = st.selectbox(
                "Clase", 
                options=[c['numero'] for c in clases], 
                format_func=lambda x: next(c['nombre'] for c in clases if c['numero'] == x), 
                index=[c['numero'] for c in clases].index(clase_actual) if clase_actual in [c['numero'] for c in clases] else 0,
                key="cambio_clase"
            )
            
            familias = get_familias(articulo_update["departamento_numero"], articulo_update["clase_numero"])
            articulo_update["familia_numero"] = st.selectbox(
                "Familia", 
                options=[f['numero'] for f in familias], 
                format_func=lambda x: next(f['nombre'] for f in familias if f['numero'] == x),
                index=[f['numero'] for f in familias].index(articulo["familia_numero"]) if articulo["familia_numero"] in [f['numero'] for f in familias] else 0,
                key="cambio_familia"
            )
            
            articulo_update["stock"] = st.number_input("Stock", value=articulo["stock"], min_value=0, max_value=999999999, key="cambio_stock")
            articulo_update["cantidad"] = st.number_input("Cantidad", value=articulo["cantidad"], min_value=0, max_value=articulo_update["stock"], key="cambio_cantidad")
            articulo_update["descontinuado"] = st.number_input("Descontinuado", value=articulo["descontinuado"], min_value=0, max_value=1, key="cambio_descontinuado")

            if st.button("Actualizar", key="cambio_actualizar"):
                # Ensure we send only the last two digits of clase_numero
                clase_numero = articulo_update['clase_numero']
                clase_dos_digitos = str(clase_numero)[-2:].zfill(2)
                
                data = {
                    "sku": sku,
                    "articulo": articulo_update["articulo"],
                    "marca": articulo_update["marca"],
                    "modelo": articulo_update["modelo"],
                    "departamento_numero": articulo_update["departamento_numero"],
                    "clase_numero": clase_dos_digitos,
                    "familia_numero": articulo_update["familia_numero"],
                    "stock": articulo_update["stock"],
                    "cantidad": articulo_update["cantidad"],
                    "descontinuado": articulo_update["descontinuado"]
                }
                st.write("Datos a enviar:", data)  # Print data for verification
                response = requests.put(f"{BASE_URL}/articulos/{sku}", json=data)
                if response.status_code == 200:
                    st.success("Artículo actualizado exitosamente")
                else:
                    st.error("Error al actualizar el artículo")
                    st.write("Código de estado:", response.status_code)  # Print status code
                    st.write("Respuesta del servidor:", response.text)  # Print server response
        else:
            st.error("El SKU no existe")
            
def consulta_articulo():
    """
    Handles the process of querying an article's details.

    This function allows searching for an article by SKU and displays its information.
    """
    st.subheader("Consulta de Artículo")
    sku = st.text_input("SKU", max_chars=6, key="consulta_sku")
    
    if sku:
        response = requests.get(f"{BASE_URL}/articulos/{sku}")
        if response.status_code == 200:
            articulo = response.json()
            st.write("Artículo:", articulo["articulo"])
            st.write("Marca:", articulo["marca"])
            st.write("Modelo:", articulo["modelo"])
            st.write("Departamento:", articulo["departamento_numero"])
            st.write("Clase:", articulo["clase_numero"])
            st.write("Familia:", articulo["familia_numero"])
            st.write("Fecha de Alta:", articulo["fecha_alta"])
            st.write("Stock:", articulo["stock"])
            st.write("Cantidad:", articulo["cantidad"])
            st.write("Descontinuado:", articulo["descontinuado"])
        else:
            st.error("El SKU no existe")

def generar_csv():
    """
    Generates CSV files for all tables in the database.

    This function reads all tables from the SQLite database and saves them as CSV files.
    """
    st.subheader("Generar CSV")
    
    # Ensure the csv/ folder exists
    if not os.path.exists('csv'):
        os.makedirs('csv')
    
    # Connect to the database
    conn = sqlite3.connect('sql_app.db')
    
    # Get the list of all tables in the database
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    
    generated_files = []
    
    for table in tables:
        table_name = table[0]
        
        # Read the table into a DataFrame
        df = pd.read_sql_query(f"SELECT * FROM {table_name}", conn)
        
        # Generate the file name
        filename = f"csv/{table_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        
        # Save the DataFrame as CSV
        df.to_csv(filename, index=False)
        
        generated_files.append(filename)
    
    # Close the connection
    conn.close()
    
    if generated_files:
        st.success("Archivos CSV generados exitosamente:")
        for file in generated_files:
            st.write(file)
    else:
        st.error("No se pudo generar ningún archivo CSV")

if __name__ == "__main__":
    main()
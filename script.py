import pandas as pd
import requests
import json
import csv
from datetime import datetime
import matplotlib.pyplot as plt
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog

# Función para cargar el archivo JSON de usuarios
def cargar_usuarios():
    try:
        with open('auth_usuarios.json', 'r') as file:
            return json.load(file)
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo cargar el archivo JSON: {e}")
        return []

# Validar usuario con sus credenciales
def validar_usuario(usuario, password):
    usuarios = cargar_usuarios()
    return any(u["usuario"] == usuario and u["password"] == password for u in usuarios)

# Función de login
def login():
    usuario = simpledialog.askstring("Login", "Usuario:")
    password = simpledialog.askstring("Login", "Contraseña:", show="*")
    if usuario and password and validar_usuario(usuario, password):
        messagebox.showinfo("Login", "Acceso concedido.")
        return True
    messagebox.showerror("Login", "Credenciales inválidas.")
    return False

# Obtener cotización del dólar
def cotizacion_dolar():
    url = 'https://dolarapi.com/v1/dolares/oficial'
    try:
        response = requests.get(url)
        return response.json().get('compra') if response.status_code == 200 else None
    except:
        messagebox.showerror("Error", "No se pudo obtener la cotización del dólar.")
        return None

# Leer precios de un archivo CSV
def leer_precios():
    try:
        return pd.read_csv('productos.csv')
    except FileNotFoundError:
        messagebox.showerror("Error", "No se encontró el archivo 'productos.csv'.")
        return None

# Actualizar precios con la cotización del dólar
def actualizar_precios(productos, cotizacion):
    productos['Precio Actualizado'] = productos['Precio'] * cotizacion
    return productos

# Guardar historial de precios
def guardar_historial(productos):
    with open('historial_precios.csv', 'a', newline='') as file:
        writer = csv.writer(file)
        fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        writer.writerow([fecha] + productos['Precio Actualizado'].round(2).tolist())

# Graficar el historial de precios
def graficar_historial():
    try:
        fechas, precios = [], []
        with open('historial_precios.csv') as file:
            reader = csv.reader(file)
            for row in reader:
                fechas.append(row[0])
                precios.append([float(p) for p in row[1:]])
        
        plt.figure(figsize=(10, 5))
        for i in range(len(precios[0])):
            plt.plot(fechas, [p[i] for p in precios], label=f'Producto {i+1}')
        plt.xlabel('Fecha')
        plt.ylabel('Precio en pesos')
        plt.title('Variación de Precios')
        plt.xticks(rotation=45)
        plt.legend()
        plt.tight_layout()
        plt.show()
    except FileNotFoundError:
        messagebox.showerror("Error", "No se encontró el historial de precios.")

# Función para analizar ventas
def analizar_ventas():
    archivo = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
    
    if archivo:
        datos = pd.read_csv(archivo)
        datos['Fecha'] = pd.to_datetime(datos['Fecha'])

        # Pedir al usuario un rango de fechas
        fecha_inicio = simpledialog.askstring("Fecha Inicio", "Ingresa la fecha de inicio (YYYY-MM-DD):")
        fecha_fin = simpledialog.askstring("Fecha Fin", "Ingresa la fecha de fin (YYYY-MM-DD):")
        
        # Filtrar los datos por el rango de fechas
        datos_filtrados = datos[(datos['Fecha'] >= fecha_inicio) & (datos['Fecha'] <= fecha_fin)]
        datos_filtrados['Ingresos'] = datos_filtrados['Cantidad'] * datos_filtrados['Precio']
        
        # Resumen de ventas dentro del rango de fechas
        resumen = datos_filtrados.groupby('Producto')[['Cantidad', 'Ingresos']].sum()
        messagebox.showinfo("Ventas por Fecha", f"Ventas en el rango seleccionado:\n{resumen.to_string()}")

# Actualizar y mostrar precios
def actualizar_y_mostrar():
    cotizacion = cotizacion_dolar()
    productos = leer_precios()
    if cotizacion and productos is not None:
        productos_actualizados = actualizar_precios(productos, cotizacion)
        guardar_historial(productos_actualizados)
        messagebox.showinfo("Actualización", f"Precios actualizados:\n{productos_actualizados[['Producto', 'Precio Actualizado']].to_string(index=False)}")

# Interfaz gráfica
if __name__ == "__main__":
    app = tk.Tk()
    app.title("Gestión de Precios y Ventas")

    if login():
        tk.Button(app, text="Analizar Ventas", command=analizar_ventas).pack(pady=10)
        tk.Button(app, text="Actualizar Precios", command=actualizar_y_mostrar).pack(pady=10)
        tk.Button(app, text="Mostrar Gráfico de Precios", command=graficar_historial).pack(pady=10)

        app.mainloop()

import requests
import pandas as pd
import json
import csv
from datetime import datetime


def cargar_usuarios():
    try:
        with open('auth_usuarios', 'r') as file:
            return json.load(file)
    except Exception as e:
        f"No se pudo cargar el archivo JSON: {e}"
        return []


def validar_usuario(usuario, password):
    usuarios = cargar_usuarios()
    return any(u["usuario"] == usuario and u["password"] == password for u in usuarios)



def login():
    usuario = ''
    password = ''
    if usuario and password and validar_usuario(usuario, password):
        return True
    return False


def cotizacion_dolar():
    url = 'https://dolarapi.com/v1/dolares'
    try:
        response = requests.get(url)
        return response.json().get('compra') if response.status_code == 200 else None
    except:

        return None


def leer_precios():
    try:
        return pd.read_csv('productos.csv')
    except FileNotFoundError:
        return None


def actualizar_precios(productos, cotizacion):
    productos['Precio Actualizado'] = productos * cotizacion
    return productos


def guardar_historial(productos):
    with open('historial_precios', 'a', newline='') as file:
        writer = csv.writer(file)
        fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        writer.writerow([fecha] + productos['Precio Actualizado'].round(2).tolist())


def actualizar_y_mostrar():
    cotizacion = cotizacion_dolar()
    productos = leer_precios()
    if cotizacion and productos is not None:
        productos_actualizados = actualizar_precios(productos, cotizacion)
        guardar_historial(productos_actualizados)

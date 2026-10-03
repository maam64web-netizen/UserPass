import os
import tkinter as tk
from tkinter import ttk
#
# Corregir las '\' en la ruta
def formatRuta(ruta):
    clean = ""
    for caracter in ruta:
        if caracter == '\\':
            clean = clean + '/'
        else:
            clean = clean + caracter
    return clean
#
# Corregir las '/' en la ruta por '\' para Windows
def formatRutaWindows(ruta):
    clean = ""
    for caracter in ruta:
        if caracter == '/':
            clean = clean + '\\'
        else:
            clean = clean + caracter
    return clean
#
TITULO = "Gestor de Base de Datos de Usuarios"
VERSION = "1.0"
AUTOR = "Miguel Ángel Arellano Medrano"
#
ANCHO = 800
ALTO = 600
#
# Ruta raiz
#
# Ruta archivos en programa ejecutable, fuera de Visual Studio Code
RUTA = os.getcwd()    # Obtiene el directorio actual
RUTA_RAIZ = formatRuta(RUTA)
RUTA_RAIZ += "/"
RUTA_IMAGENES = RUTA_RAIZ + "imagenes/"
RUTA_DB = RUTA_RAIZ + "db/"
DB_NAME = RUTA_DB + "UserPass.db"
#
# Convertir Notación Anglosajona (. = decimal , = miles) a Europea
def formato_europeo(str_numero):
    return str_numero.replace(',','n').replace('.',',').replace('n','.')
#
def mostrar_mensaje(parent,titulo,mensaje,tipo="info",ancho=400,alto=200):
    """
    Muestra un mensaje en una ventana modal centrada
    
    Args:
        parent: Ventana padre
        titulo: Título de la ventana
        mensaje: Mensaje a mostrar
        tipo: Tipo de mensaje ('info', 'error', 'warning', 'question')
        ancho: Ancho de la ventana
        alto: Alto de la ventana
#
    Returns:
        True si el usuario acepta (para tipo 'question'), None en otros casos
    """
    ventana = tk.Toplevel(parent)
    ventana.withdraw()
    ventana.title(titulo)
    ventana.geometry(f"{ancho}x{alto}")
    ventana.resizable(False,False)
    try:
        ventana.iconbitmap(RUTA_IMAGENES + "icono.ico")
    except:
        pass  # Si no existe el icono, continuar sin él
#
    frame = ttk.Frame(ventana,padding="20")
    frame.pack(fill=tk.BOTH,expand=True)
#
    # Icono según el tipo
    iconos = {
        'info': 'ℹ️',
        'error': '❌',
        'warning': '⚠️',
        'question': '❓'
    }
    icono = iconos.get(tipo,'ℹ️')
#
    # Título con icono
    ttk.Label(
        frame,
        text=f"{icono} {titulo}",
        font=('Segoe UI',12,'bold')
    ).pack(pady=(0,20))
#
    # Mensaje
    label_mensaje = ttk.Label(
        frame,
        text=mensaje,
        font=('Segoe UI',9),
        wraplength=ancho-60,
        justify=tk.LEFT
    )
    label_mensaje.pack(pady=10)
#
    # Variable para almacenar la respuesta
    respuesta = [None]
#
    def on_si():
        respuesta[0] = True
        ventana.destroy()
#
    def on_no():
        respuesta[0] = False
        ventana.destroy()
#
    def on_aceptar():
        ventana.destroy()
#
    # Botones según el tipo
    btn_frame = ttk.Frame(frame)
    btn_frame.pack(pady=(20,0))
#
    if tipo == 'question':
        ttk.Button(
            btn_frame,
            text="Sí",
            command=on_si,
            width=10
        ).pack(side=tk.LEFT,padx=5)
        ttk.Button(
            btn_frame,
            text="No",
            command=on_no,
            width=10
        ).pack(side=tk.LEFT,padx=5)
    else:
        ttk.Button(
            btn_frame,
            text="Aceptar",
            command=on_aceptar,
            width=15
        ).pack()
#
    # Centrar ventana respecto a la ventana padre
    ventana.update_idletasks()
    if parent.winfo_viewable():
        x = parent.winfo_x() + (parent.winfo_width() // 2) - (ventana.winfo_width() // 2)
        y = parent.winfo_y() + (parent.winfo_height() // 2) - (ventana.winfo_height() // 2)
        ventana.geometry(f'+{x}+{y}')
#
    # Mostrar ventana ya centrada
    ventana.deiconify()
#
    # Hacer modal
    ventana.transient(parent)
    ventana.grab_set()
    ventana.wait_window()
#
    return respuesta[0]
#
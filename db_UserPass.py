"""
Gestor Gráfico de Base de Datos de Usuarios
Interfaz gráfica para visualizar y gestionar usuarios
"""
import tkinter as tk
from tkinter import ttk,filedialog
import sqlite3 as sql
import csv
from typing import List,Tuple,Optional
from constantes import *
#
class GestorDB:
    """Clase para gestionar las operaciones de la base de datos"""
#
    def __init__(self,db_path: str):
        self.db_path = db_path
        self._crear_tablas()
#
    def _crear_tablas(self):
        """Crea las tablas si no existen"""
        try:
            conn = sql.connect(self.db_path)
            cursor = conn.cursor()
#
            # Tabla UserPass
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS UserPass (
                    Nombre TEXT,
                    Usuario TEXT,
                    Contrasena TEXT
                )
            ''')
#
            # Tabla defecto
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS defecto (
                    Usuario TEXT,
                    Contrasena TEXT
                )
            ''')
#
            conn.commit()
            conn.close()
        except sql.Error as e:
            print(f"Error al crear tablas: {e}")
#
    def obtener_usuarios(self) -> List[Tuple]:
        """Obtiene todos los usuarios de la tabla UserPass"""
        try:
            conn = sql.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT Nombre, Usuario, Contrasena FROM UserPass ORDER BY Nombre")
            usuarios = cursor.fetchall()
            conn.close()
            return usuarios
        except sql.Error as e:
            print(f"Error al obtener usuarios: {e}")
            return []
#
    def existe_nombre(self,nombre: str) -> bool:
        """Verifica si ya existe un usuario con ese nombre"""
        try:
            conn = sql.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM UserPass WHERE Nombre = ?",(nombre,))
            count = cursor.fetchone()[0]
            conn.close()
            return count > 0
        except sql.Error as e:
            print(f"Error al verificar nombre: {e}")
            return False
#
    def agregar_usuario(self,nombre: str,usuario: str,contrasena: str) -> bool:
        """Agrega un nuevo usuario a la tabla UserPass"""
        try:
            conn = sql.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO UserPass (Nombre, Usuario, Contrasena) VALUES (?, ?, ?)",
                (nombre,usuario,contrasena)
            )
            conn.commit()
            conn.close()
            return True
        except sql.Error as e:
            print(f"Error al agregar usuario: {e}")
            return False
#
    def actualizar_usuario(self,nombre_original: str,usuario_original: str,
                           nombre: str,usuario: str,contrasena: str) -> bool:
        """Actualiza un usuario existente"""
        try:
            conn = sql.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute(
                """UPDATE UserPass 
                   SET Nombre = ?, Usuario = ?, Contrasena = ? 
                   WHERE Nombre = ? AND Usuario = ?""",
                   (nombre,usuario,contrasena,nombre_original,usuario_original)
            )
            conn.commit()
            conn.close()
            return True
        except sql.Error as e:
            print(f"Error al actualizar usuario: {e}")
            return False
#
    def eliminar_usuario(self,nombre: str,usuario: str) -> bool:
        """Elimina un usuario de la tabla UserPass"""
        try:
            conn = sql.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute(
                "DELETE FROM UserPass WHERE Nombre = ? AND Usuario = ?",
                (nombre,usuario)
            )
            conn.commit()
            conn.close()
            return True
        except sql.Error as e:
            print(f"Error al eliminar usuario: {e}")
            return False
#
    def buscar_usuarios(self,termino: str) -> List[Tuple]:
        """Busca usuarios por nombre o usuario"""
        try:
            conn = sql.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute(
                """SELECT Nombre, Usuario, Contrasena FROM UserPass 
                   WHERE Nombre LIKE ? OR Usuario LIKE ? ORDER BY Nombre""",
                (f"%{termino}%",f"%{termino}%")
            )
            usuarios = cursor.fetchall()
            conn.close()
            return usuarios
        except sql.Error as e:
            print(f"Error al buscar usuarios: {e}")
            return []
#
    def exportar_a_csv(self,ruta_archivo: str) -> bool:
        """Exporta todos los usuarios a un archivo CSV"""
        try:
            usuarios = self.obtener_usuarios()
            with open(ruta_archivo,'w',newline='',encoding='utf-8') as archivo_csv:
                escritor = csv.writer(archivo_csv)
                # Escribir encabezados
                escritor.writerow(['Nombre','Usuario','Contraseña'])
                # Escribir datos
                escritor.writerows(usuarios)
            return True
        except Exception as e:
            print(f"Error al exportar a CSV: {e}")
            return False
#
    def guardar_default(self,usuario: str,contrasena: str) -> bool:
        """Guarda o actualiza el usuario y contraseña por defecto"""
        try:
            conn = sql.connect(self.db_path)
            cursor = conn.cursor()
            # Primero eliminar cualquier registro existente
            cursor.execute("DELETE FROM defecto")
            # Insertar el nuevo registro por defecto
            cursor.execute(
                "INSERT INTO defecto (Usuario, Contrasena) VALUES (?, ?)",
                (usuario,contrasena)
            )
            conn.commit()
            conn.close()
            return True
        except sql.Error as e:
            print(f"Error al guardar default: {e}")
            return False
#
    def obtener_default(self) -> Optional[Tuple]:
        """Obtiene el usuario por defecto"""
        try:
            conn = sql.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT Usuario, Contrasena FROM defecto LIMIT 1")
            default = cursor.fetchone()
            conn.close()
            return default
        except sql.Error as e:
            print(f"Error al obtener default: {e}")
            return None
#
class VentanaGestorDB:
    """Ventana principal del gestor de base de datos"""
    def __init__(self,root: tk.Tk):
        self.root = root
        self.root.title(TITULO)
        self.root.geometry(f"{ANCHO}x{ALTO}")
        self.root.resizable(False,False)
        self.root.iconbitmap(RUTA_IMAGENES + "icono.ico")
#
        # Inicializar gestor de BD
        self.gestor = GestorDB(DB_NAME)
#
        # Variables para edición
        self.editando = False
        self.usuario_original = None
#
        # Crear menú
        self.crear_menu()
#
        # Crear interfaz
        self.crear_widgets()
#
        # Cargar datos
        self.cargar_usuarios()
#
        # Centrar ventana (al final para que tenga las dimensiones correctas)
        self.centrar_ventana()
#
    def centrar_ventana(self):
        """Centra la ventana en la pantalla"""
        self.root.update_idletasks()
        ancho_pantalla = self.root.winfo_screenwidth()
        alto_pantalla = self.root.winfo_screenheight()
        x = (ancho_pantalla // 2) - (ANCHO // 2)
        y = (alto_pantalla // 2) - (ALTO // 2)
        self.root.geometry(f"{ANCHO}x{ALTO}+{x}+{y}")
#
    def crear_menu(self):
        """Crea la barra de menú"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
#
        # Menú Archivo
        menu_archivo = tk.Menu(menubar,tearoff=0)
        menubar.add_cascade(label="Archivo",menu=menu_archivo)
        menu_archivo.add_command(label="Nuevo",
                                 command=self.preparar_nuevo,accelerator="Ctrl+N")
        menu_archivo.add_command(label="Agregar",
                                 command=self.agregar_usuario,accelerator="Ctrl+A")
        menu_archivo.add_command(label="Actualizar",
                                 command=self.actualizar_usuario,accelerator="Ctrl+U")
        menu_archivo.add_separator()
        menu_archivo.add_command(label="Exportar a CSV",
                                 command=self.convertir_a_csv,accelerator="Ctrl+E")
        menu_archivo.add_separator()
        menu_archivo.add_command(label="Salir",
                                 command=self.root.quit,accelerator="Alt+F4")
#
        # Menú Edición
        menu_edicion = tk.Menu(menubar,tearoff=0)
        menubar.add_cascade(label="Edición",menu=menu_edicion)
        menu_edicion.add_command(label="Limpiar Formulario",
                                 command=self.limpiar_formulario,accelerator="Ctrl+L")
        menu_edicion.add_command(label="Eliminar Seleccionado",
                                 command=self.eliminar_usuario,accelerator="Del")
        menu_edicion.add_separator()
        menu_edicion.add_command(label="Guardar como Defecto",
                                 command=self.guardar_defecto,accelerator="Ctrl+D")
#
        # Menú Ver
        menu_ver = tk.Menu(menubar,tearoff=0)
        menubar.add_cascade(label="Ver",menu=menu_ver)
        menu_ver.add_command(label="Mostrar Todos",
                             command=self.cargar_usuarios,accelerator="F5")
        menu_ver.add_command(label="Buscar",
                             command=lambda: self.entry_buscar.focus_set(),accelerator="Ctrl+F")
#
        # Menú Ayuda
        menu_ayuda = tk.Menu(menubar,tearoff=0)
        menubar.add_cascade(label="Ayuda",menu=menu_ayuda)
        menu_ayuda.add_command(label="Acerca de...",
                               command=self.acerca_de,accelerator="F1")
#
        # Atajos de teclado
        self.root.bind('<Control-n>',lambda e: self.preparar_nuevo())
        self.root.bind('<Control-N>',lambda e: self.preparar_nuevo())
        self.root.bind('<Control-a>',lambda e: self.agregar_usuario())
        self.root.bind('<Control-A>',lambda e: self.agregar_usuario())
        self.root.bind('<Control-u>',lambda e: self.actualizar_usuario())
        self.root.bind('<Control-U>',lambda e: self.actualizar_usuario())
        self.root.bind('<Control-e>',lambda e: self.convertir_a_csv())
        self.root.bind('<Control-E>',lambda e: self.convertir_a_csv())
        self.root.bind('<Control-l>',lambda e: self.limpiar_formulario())
        self.root.bind('<Control-L>',lambda e: self.limpiar_formulario())
        self.root.bind('<Delete>',lambda e: self.eliminar_usuario())
        self.root.bind('<Control-d>',lambda e: self.guardar_defecto())
        self.root.bind('<Control-D>',lambda e: self.guardar_defecto())
        self.root.bind('<F5>',lambda e: self.cargar_usuarios())
        self.root.bind('<Control-f>',lambda e: self.entry_buscar.focus_set())
        self.root.bind('<Control-F>',lambda e: self.entry_buscar.focus_set())
        self.root.bind('<F1>',lambda e: self.acerca_de())
#
    def crear_widgets(self):
        """Crea todos los widgets de la interfaz"""
#
        # Frame principal
        main_frame = ttk.Frame(self.root,padding="10")
        main_frame.grid(row=0,column=0,sticky=(tk.W,tk.E,tk.N,tk.S))
#
        # Configurar grid
        self.root.columnconfigure(0,weight=1)
        self.root.rowconfigure(0,weight=1)
        main_frame.columnconfigure(0,weight=1)
        main_frame.rowconfigure(2,weight=1)
#
        # === SECCIÓN DE BÚSQUEDA ===
        search_frame = ttk.LabelFrame(main_frame,text="Búsqueda",padding="5")
        search_frame.grid(row=0,column=0,sticky=(tk.W,tk.E),pady=(0,10))
        search_frame.columnconfigure(1,weight=1)
#
        ttk.Label(search_frame,text="Buscar:").grid(row=0,column=0,padx=5)
        self.entry_buscar = ttk.Entry(search_frame)
        self.entry_buscar.grid(row=0,column=1,sticky=(tk.W,tk.E),padx=5)
        self.entry_buscar.bind('<KeyRelease>',lambda e: self.buscar_usuarios())
#
        ttk.Button(search_frame,text="Mostrar Todos",
                   command=self.cargar_usuarios).grid(row=0,column=2,padx=5)
#
        # Label para mostrar total de usuarios
        self.lbl_total = ttk.Label(search_frame,text="Total: 0",font=("Arial",9))
        self.lbl_total.grid(row=0,column=3,padx=10)
#
        # === SECCIÓN DE FORMULARIO ===
        form_frame = ttk.LabelFrame(main_frame,text="Datos del Usuario",padding="5")
        form_frame.grid(row=1,column=0,sticky=(tk.W,tk.E),pady=(0,10))
#
        # Configurar columnas para centrar todo el contenido
        form_frame.columnconfigure(0,weight=1)
        for i in range(1,16):  # Columnas para labels,entries y botones
            form_frame.columnconfigure(i,weight=0)
        form_frame.columnconfigure(16,weight=1)
#
        # Fila 0: Nombre (alineado con los botones)
        ttk.Label(form_frame,text="Nombre:").grid(row=0,column=1,sticky=tk.W,padx=5,pady=5)
        self.entry_nombre = ttk.Entry(form_frame)
        self.entry_nombre.grid(row=0,column=2,columnspan=14,sticky=(tk.W,tk.E),padx=5,pady=5)
#
        # Fila 1: Usuario (alineado con los botones)
        ttk.Label(form_frame,text="Usuario:").grid(row=1,column=1,sticky=tk.W,padx=5,pady=5)
        self.entry_usuario = ttk.Entry(form_frame)
        self.entry_usuario.grid(row=1,column=2,columnspan=14,sticky=(tk.W,tk.E),padx=5,pady=5)
#
        # Fila 2: Contraseña (alineado con los botones)
        ttk.Label(form_frame,text="Contraseña:").grid(row=2,column=1,sticky=tk.W,padx=5,pady=5)
        self.entry_contrasena = ttk.Entry(form_frame)
        self.entry_contrasena.grid(row=2,column=2,columnspan=14,sticky=(tk.W,tk.E),padx=5,pady=5)
#
        # Fila 3: Botones (alineados desde el principio hasta el final)
        ttk.Button(form_frame,text="Nuevo",command=self.preparar_nuevo).grid(
                   row=3,column=1,columnspan=2,sticky=(tk.W,tk.E),padx=3,pady=10)
#
        self.btn_agregar = ttk.Button(form_frame,text="Agregar",command=self.agregar_usuario)
        self.btn_agregar.grid(row=3,column=3,columnspan=2,sticky=(tk.W,tk.E),padx=3,pady=10)
#
        self.btn_actualizar = ttk.Button(form_frame,text="Actualizar",
                                         command=self.actualizar_usuario,state=tk.DISABLED)
        self.btn_actualizar.grid(row=3,column=5,columnspan=2,sticky=(tk.W,tk.E),padx=3,pady=10)
#
        ttk.Button(form_frame,text="Limpiar",command=self.limpiar_formulario).grid(
                   row=3,column=7,columnspan=2,sticky=(tk.W,tk.E),padx=3,pady=10)
#
        ttk.Button(form_frame,text="Eliminar Seleccionado",command=self.eliminar_usuario).grid(
                   row=3,column=9,columnspan=2,sticky=(tk.W,tk.E),padx=3,pady=10)
#
        ttk.Button(form_frame,text="Defecto",command=self.guardar_defecto).grid(
                   row=3,column=11,columnspan=2,sticky=(tk.W,tk.E),padx=3,pady=10)
#
        ttk.Button(form_frame,text="Exportar a CSV",command=self.convertir_a_csv).grid(
                   row=3,column=13,columnspan=3,sticky=(tk.W,tk.E),padx=3,pady=10)
#
        # === SECCIÓN DE TABLA ===
        table_frame = ttk.LabelFrame(main_frame,text="Lista de Usuarios",padding="5")
        table_frame.grid(row=2,column=0,sticky=(tk.W,tk.E,tk.N,tk.S))
        table_frame.columnconfigure(0,weight=1)
        table_frame.rowconfigure(0,weight=1)
#
        # Crear Treeview
        columns = ("Nombre","Usuario","Contraseña")
        self.tree = ttk.Treeview(table_frame,columns=columns,show="headings",height=15)
#
        # Configurar columnas
        self.tree.heading("Nombre",text="Nombre")
        self.tree.heading("Usuario",text="Usuario")
        self.tree.heading("Contraseña",text="Contraseña")
#
        self.tree.column("Nombre",width=200)
        self.tree.column("Usuario",width=200)
        self.tree.column("Contraseña",width=200)
#
        # Scrollbar
        scrollbar = ttk.Scrollbar(table_frame,orient=tk.VERTICAL,command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
#
        self.tree.grid(row=0,column=0,sticky=(tk.W,tk.E,tk.N,tk.S))
        scrollbar.grid(row=0,column=1,sticky=(tk.N,tk.S))
#
        # Evento de selección
        self.tree.bind('<<TreeviewSelect>>',self.on_select)
#
    def cargar_usuarios(self):
        """Carga todos los usuarios en la tabla"""
        # Limpiar tabla
        for item in self.tree.get_children():
            self.tree.delete(item)
#
        # Limpiar entry de búsqueda
        self.entry_buscar.delete(0,tk.END)
#
       # Cargar usuarios
        usuarios = self.gestor.obtener_usuarios()
        for usuario in usuarios:
            self.tree.insert("",tk.END,values=usuario)
#
        total = f"{len(usuarios):,.0f}"
        total = formato_europeo(total)
        self.lbl_total.config(text=f"Total: {total}")
#
    def buscar_usuarios(self):
        """Busca usuarios según el término de búsqueda"""
        termino = self.entry_buscar.get()
#
        # Limpiar tabla
        for item in self.tree.get_children():
            self.tree.delete(item)
#
        if termino.strip() == "":
            self.cargar_usuarios()
            return
#
        # Buscar usuarios
        usuarios = self.gestor.buscar_usuarios(termino)
        for usuario in usuarios:
            self.tree.insert("",tk.END,values=usuario)
#
        total = f"{len(usuarios):,.0f}"
        total = formato_europeo(total)
        self.lbl_total.config(text=f"Encontrados: {total}")
#
    def agregar_usuario(self):
        """Agrega un nuevo usuario"""
        nombre = self.entry_nombre.get().strip()
        usuario = self.entry_usuario.get().strip()
        contrasena = self.entry_contrasena.get().strip()
#
        if not nombre or not usuario or not contrasena:
            mostrar_mensaje(self.root,"Advertencia",
                            "Todos los campos son obligatorios","warning")
            return
#
        # Verificar si ya existe el nombre
        if self.gestor.existe_nombre(nombre):
            mostrar_mensaje(self.root,"Advertencia",
                                 f"Ya existe un usuario con el nombre '{nombre}'","warning")
            return
#
        if self.gestor.agregar_usuario(nombre,usuario,contrasena):
            mostrar_mensaje(self.root,"Éxito","Usuario agregado correctamente","info")
            self.cargar_usuarios()
            # Preparar para nuevo usuario con valores por defecto
            self.preparar_nuevo()
        else:
            mostrar_mensaje(self.root,"Error","No se pudo agregar el usuario","error")
#
    def actualizar_usuario(self):
        """Actualiza el usuario seleccionado"""
        if not self.editando or not self.usuario_original:
            return
#
        nombre = self.entry_nombre.get().strip()
        usuario = self.entry_usuario.get().strip()
        contrasena = self.entry_contrasena.get().strip()
#
        if not nombre or not usuario or not contrasena:
            mostrar_mensaje(self.root,"Advertencia",
                            "Todos los campos son obligatorios","warning")
            return
#
        nombre_orig,usuario_orig = self.usuario_original
#
        if self.gestor.actualizar_usuario(nombre_orig,usuario_orig,
                                          nombre,usuario,contrasena):
            mostrar_mensaje(self.root,"Éxito","Usuario actualizado correctamente","info")
            self.limpiar_formulario()
            self.cargar_usuarios()
        else:
            mostrar_mensaje(self.root,"Error","No se pudo actualizar el usuario","error")
#
    def eliminar_usuario(self):
        """Elimina el usuario seleccionado"""
        seleccion = self.tree.selection()
        if not seleccion:
            mostrar_mensaje(self.root,"Advertencia",
                            "Seleccione un usuario para eliminar","warning")
            return
#
        item = self.tree.item(seleccion[0])
        valores = item['values']
        nombre,usuario = valores[0],valores[1]
#
        respuesta = mostrar_mensaje(self.root,"Confirmar",
                                    f"¿Está seguro de eliminar el usuario '{nombre}'?",
                                    "question")
        if respuesta:
            if self.gestor.eliminar_usuario(nombre,usuario):
                mostrar_mensaje(self.root,"Éxito","Usuario eliminado correctamente","info")
                self.limpiar_formulario()
                self.cargar_usuarios()
            else:
                mostrar_mensaje(self.root,"Error","No se pudo eliminar el usuario","error")
#
    def on_select(self,event):
        """Maneja la selección de un usuario en la tabla"""
        seleccion = self.tree.selection()
        if seleccion:
            item = self.tree.item(seleccion[0])
            valores = item['values']
#
            # Llenar formulario
            self.entry_nombre.delete(0,tk.END)
            self.entry_nombre.insert(0,valores[0])
#
            self.entry_usuario.delete(0,tk.END)
            self.entry_usuario.insert(0,valores[1])
#
            self.entry_contrasena.delete(0,tk.END)
            self.entry_contrasena.insert(0,valores[2])
#
            # Activar modo edición
            self.editando = True
            self.usuario_original = (valores[0],valores[1])
            self.btn_actualizar.config(state=tk.NORMAL)
            self.btn_agregar.config(state=tk.DISABLED)
#
    def preparar_nuevo(self):
        """Prepara el formulario para agregar un nuevo usuario con valores por defecto"""
        # Limpiar campos
        self.entry_nombre.delete(0,tk.END)
        self.entry_usuario.delete(0,tk.END)
        self.entry_contrasena.delete(0,tk.END)
#
        # Obtener valores por defecto
        default = self.gestor.obtener_default()
        if default:
            usuario_def,contrasena_def = default
            self.entry_usuario.insert(0,usuario_def)
            self.entry_contrasena.insert(0,contrasena_def)
#
        # Desactivar modo edición
        self.editando = False
        self.usuario_original = None
        self.btn_actualizar.config(state=tk.DISABLED)
        self.btn_agregar.config(state=tk.NORMAL)
#
        # Deseleccionar en la tabla
        for item in self.tree.selection():
            self.tree.selection_remove(item)
#
        # Posicionar cursor en el campo nombre
        self.entry_nombre.focus_set()
#
    def convertir_a_csv(self):
        """Exporta la base de datos a un archivo CSV"""
        # Abrir diálogo para seleccionar ubicación y nombre del archivo
        ruta_archivo = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("Archivos CSV", "*.csv"),("Todos los archivos", "*.*")],
            title="Guardar como CSV",
            initialfile="usuarios.csv"
        )
#
        if not ruta_archivo:
            return  # El usuario canceló
#
        if self.gestor.exportar_a_csv(ruta_archivo):
            mensaje = "Datos exportados correctamente a:\n"
            mensaje += f"{formatRutaWindows(ruta_archivo)}"
            mostrar_mensaje(self.root,"Éxito",mensaje,"info")
        else:
            mostrar_mensaje(self.root,"Error",
                            "No se pudo exportar los datos a CSV","error")
#
    def guardar_defecto(self):
        """Guarda el usuario y contraseña actuales como valores por defecto"""
        usuario = self.entry_usuario.get().strip()
        contrasena = self.entry_contrasena.get().strip()
#
        if not usuario or not contrasena:
            mostrar_mensaje(self.root,"Advertencia",
                            "Debe ingresar usuario y contraseña para guardar como defecto",
                            "warning")
            return
#
        mensaje = "¿Desea guardar estos valores como usuario y contraseña por defecto?"
        respuesta = mostrar_mensaje(self.root,"Confirmar",mensaje,"question")
        if respuesta:
            if self.gestor.guardar_default(usuario,contrasena):
                mostrar_mensaje(self.root,"Éxito",
                                "Usuario y contraseña guardados como valores por defecto","info")
            else:
                mostrar_mensaje(self.root,"Error",
                                "No se pudo guardar los valores por defecto","error")
#
    def limpiar_formulario(self):
        """Limpia el formulario y desactiva el modo edición"""
        self.entry_nombre.delete(0,tk.END)
        self.entry_usuario.delete(0,tk.END)
        self.entry_contrasena.delete(0,tk.END)
        self.entry_buscar.delete(0,tk.END)
#
        self.editando = False
        self.usuario_original = None
        self.btn_actualizar.config(state=tk.DISABLED)
        self.btn_agregar.config(state=tk.NORMAL)
#
        # Deseleccionar en la tabla
        for item in self.tree.selection():
            self.tree.selection_remove(item)
#
    def acerca_de(self):
        """Muestra información sobre la aplicación"""
        # Crear ventana Acerca de
        ventana = tk.Toplevel(self.root)
        ventana.withdraw()  # Ocultar temporalmente
        ventana.title("Acerca de")
        ventana.geometry("500x300")
        ventana.resizable(False,False)
        ventana.iconbitmap(RUTA_IMAGENES + "icono.ico")
#
        # Frame principal
        frame = ttk.Frame(ventana,padding="30")
        frame.pack(fill=tk.BOTH,expand=True)
#
        # Título
        ttk.Label(
            frame,
            text=f"🔑 {TITULO}",
            font=('Segoe UI',14,'bold')
        ).pack(pady=(0,20))
#
        # Información
        info_text = [
            f"Versión {VERSION}",
            "",
            "Desarrollado con Python y Tkinter",
            "",
            "Base de datos: SQLite",
            f"Archivo: {formatRutaWindows(DB_NAME)}",
            "",
            f"{AUTOR} © 2026"
        ]
#
        for linea in info_text:
            ttk.Label(
                frame,
                text=linea,
                font=('Segoe UI',9)
            ).pack(pady=2)
#
        # Botón cerrar
        ttk.Button(
            frame,
            text="Cerrar",
            command=ventana.destroy,
            width=15
        ).pack(pady=(20,0))
#
        # Centrar ventana respecto a la ventana padre
        ventana.update_idletasks()
        x = self.root.winfo_x() + (self.root.winfo_width() // 2) - (ventana.winfo_width() // 2)
        y = self.root.winfo_y() + (self.root.winfo_height() // 2) - (ventana.winfo_height() // 2)
        ventana.geometry(f'+{x}+{y}')
#
        # Mostrar ventana ya centrada
        ventana.deiconify()
#
        # Hacer modal
        ventana.transient(self.root)
        ventana.grab_set()
#
def main():
    """Función principal"""
    root = tk.Tk()
    app = VentanaGestorDB(root)
    root.mainloop()
#
if __name__ == "__main__":
    main()
#
import customtkinter as ctk
import cv2
from PIL import Image
import threading
import json
import os
from tkinter import filedialog

class OperationView(ctk.CTkFrame):
    def __init__(self, master, ros_manager, logger_func, **kwargs):
        super().__init__(master, **kwargs)

        self.ros_manager = ros_manager
        self.log = logger_func

        # Variables de estado
        self.cap = None
        self.ruta_imagen_actual = ""
        self.rutas_json_actual = ""
        self.matriz_json_actual = ""

        # Configuracion del layout principal
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(1, weight=1) # Las imagenes se expanden
        self.grid_rowconfigure(3, weight=1) # La caja de formulas se expande

        # --- TITULO ---
        self.titulo = ctk.CTkLabel(self, text="Operacion y Calculo Matematico", font=ctk.CTkFont(size=20, weight="bold"))
        self.titulo.grid(row=0, column=0, columnspan=2, pady=10, padx=20, sticky="w")

        # --- PANEL DE IMAGENES ---
        self.lbl_img_original = ctk.CTkLabel(self, text="[ Camara / Original ]", bg_color="gray20")
        self.lbl_img_original.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")

        self.lbl_img_procesada = ctk.CTkLabel(self, text="[ Imagen Procesada ]\n(Requiere actualizar el servicio ROS para devolver imagen)", bg_color="gray20")
        self.lbl_img_procesada.grid(row=1, column=1, padx=10, pady=10, sticky="nsew")

        # --- CONTROLES DE ENTRADA (Camara o Archivo) ---
        self.frame_input = ctk.CTkFrame(self)
        self.frame_input.grid(row=2, column=0, padx=10, pady=10, sticky="ew")

        self.btn_abrir_archivo = ctk.CTkButton(self.frame_input, text="Cargar Imagen", command=self.cargar_archivo)
        self.btn_abrir_archivo.grid(row=0, column=0, padx=5, pady=5)

        self.btn_camara = ctk.CTkButton(self.frame_input, text="Iniciar Camara", command=self.toggle_camara)
        self.btn_camara.grid(row=0, column=1, padx=5, pady=5)

        self.btn_capturar = ctk.CTkButton(self.frame_input, text="Tomar Foto", state="disabled", command=self.capturar_foto)
        self.btn_capturar.grid(row=0, column=2, padx=5, pady=5)

        # --- CONTROLES DE PROCESAMIENTO (ROS 2) ---
        self.frame_ros = ctk.CTkFrame(self)
        self.frame_ros.grid(row=2, column=1, padx=10, pady=10, sticky="ew")

        self.script_var = ctk.StringVar(value="1")
        self.combo_script = ctk.CTkOptionMenu(self.frame_ros, values=["1", "2", "3"], variable=self.script_var, width=60)
        self.combo_script.grid(row=0, column=0, padx=5, pady=5)

        self.btn_procesar_vision = ctk.CTkButton(self.frame_ros, text="1. Extraer Rutas", command=self.llamar_vision)
        self.btn_procesar_vision.grid(row=0, column=1, padx=5, pady=5)

        self.btn_calcular = ctk.CTkButton(self.frame_ros, text="2. Generar Matematicas", command=self.llamar_calculo)
        self.btn_calcular.grid(row=0, column=2, padx=5, pady=5)

        # --- PANEL DE FORMULAS ---
        self.textbox_formulas = ctk.CTkTextbox(self, font=ctk.CTkFont(family="monospace", size=12))
        self.textbox_formulas.grid(row=3, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")
        self.textbox_formulas.insert("end", "Esperando generacion de formulas parametricas...\n")

    # ==========================================
    # LOGICA DE ENTRADA (OPENCV Y ARCHIVOS)
    # ==========================================
    def cargar_archivo(self):
        ruta = filedialog.askopenfilename(filetypes=[("Imagenes", "*.jpg *.png *.jpeg")])
        if ruta:
            self.ruta_imagen_actual = ruta
            self.log(f"Imagen cargada: {ruta}")
            self.mostrar_imagen_ctk(ruta, self.lbl_img_original)

    def toggle_camara(self):
        if self.cap is None:
            self.cap = cv2.VideoCapture(0)
            if not self.cap.isOpened():
                self.log("Error: No se pudo acceder a la camara.")
                self.cap = None
                return
            
            self.btn_camara.configure(text="Detener Camara")
            self.btn_capturar.configure(state="normal")
            self.log("Camara iniciada.")
            self.actualizar_frame_camara()
        else:
            self.apagar_camara()

    def actualizar_frame_camara(self):
        if self.cap is not None and self.cap.isOpened():
            ret, frame = self.cap.read()
            if ret:
                # Convertir de BGR (OpenCV) a RGB (PIL/CTK)
                cv2image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                img = Image.fromarray(cv2image)
                ctk_img = ctk.CTkImage(light_image=img, dark_image=img, size=(320, 240))
                self.lbl_img_original.configure(image=ctk_img, text="")
                self.lbl_img_original.image = ctk_img
            
            # Loop de actualizacion (15 ms) sin bloquear la UI
            self.after(15, self.actualizar_frame_camara)

    def capturar_foto(self):
        if self.cap is not None and self.cap.isOpened():
            ret, frame = self.cap.read()
            if ret:
                ruta_temp = "/tmp/lynx_vision_input.jpg"
                cv2.imwrite(ruta_temp, frame)
                self.ruta_imagen_actual = ruta_temp
                self.log(f"Foto capturada y guardada en {ruta_temp}")
                self.apagar_camara()
                self.mostrar_imagen_ctk(ruta_temp, self.lbl_img_original)

    def apagar_camara(self):
        if self.cap is not None:
            self.cap.release()
            self.cap = None
            self.btn_camara.configure(text="Iniciar Camara")
            self.btn_capturar.configure(state="disabled")
            self.log("Camara detenida.")

    def mostrar_imagen_ctk(self, ruta, label):
        try:
            img = Image.open(ruta)
            img.thumbnail((400, 300)) # Redimensionar para la UI
            ctk_img = ctk.CTkImage(light_image=img, dark_image=img, size=img.size)
            label.configure(image=ctk_img, text="")
            label.image = ctk_img
        except Exception as e:
            self.log(f"Error cargando imagen en UI: {e}")

    # ==========================================
    # LOGICA DE COMUNICACION (ROS 2)
    # ==========================================
    def llamar_vision(self):
        if not self.ruta_imagen_actual or not os.path.exists(self.ruta_imagen_actual):
            self.log("Error: No hay una imagen valida para procesar.")
            return

        script_id = self.script_var.get()
        self.log(f"Enviando peticion a Vision_Service (Script {script_id})...")
        
        self.btn_procesar_vision.configure(state="disabled")
        
        def callback_vision(respuesta):
            self.btn_procesar_vision.configure(state="normal")
            if respuesta.success:
                self.rutas_json_actual = respuesta.trajectories_json
                self.log(f"Vision exitosa. Rutas extraidas.")
            else:
                self.log(f"Fallo en vision: {respuesta.error_message}")
                
        self.ros_manager.solicitar_vision(self.ruta_imagen_actual, script_id, callback_vision)

    def llamar_calculo(self):
        if not self.rutas_json_actual:
            self.log("Error: Primero debes procesar la vision para obtener rutas.")
            return

        self.log("Enviando peticion a Calculus_Service...")
        self.btn_calcular.configure(state="disabled")

        # Dimensiones estaticas de la hoja para esta prueba (luego lo conectaremos a la config)
        config_espacio = json.dumps({
            'X_MIN': -100.0, 'X_MAX': 100.0,
            'Y_MIN': 50.0, 'Y_MAX': 250.0,
            'Z_DIBUJO': 0.0, 'Z_TRANSITO': 20.0
        })

        def callback_calculo(respuesta):
            self.btn_calcular.configure(state="normal")
            if respuesta.success:
                self.matriz_json_actual = respuesta.matriz_espacial_json
                formulas_raw = json.loads(respuesta.formulas_matematicas_json)
                
                self.log("Calculo exitoso. Ecuaciones parametricas generadas.")
                self.textbox_formulas.delete("1.0", "end")
                for f in formulas_raw:
                    self.textbox_formulas.insert("end", f + "\n")
            else:
                self.log(f"Fallo en calculo: {respuesta.error_message}")

        # Se envian 640 y 480 como w_img y h_img estandar de camara.
        self.ros_manager.solicitar_calculo(self.rutas_json_actual, config_espacio, 640, 480, 5.0, callback_calculo)

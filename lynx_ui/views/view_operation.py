import customtkinter as ctk
import cv2
from PIL import Image
import json
import os
import numpy as np
import traceback
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

        # Layout
        self.grid_columnconfigure((0, 1), weight=1)
        self.grid_rowconfigure(1, weight=1)   
        self.grid_rowconfigure(3, weight=1)   

        # --- HEADER ---
        self.titulo = ctk.CTkLabel(self, text="SYSTEM CONTROL: SIG-LYNX", 
                                   font=ctk.CTkFont(size=22, weight="bold", family="monospace"))
        self.titulo.grid(row=0, column=0, columnspan=2, pady=15, padx=20, sticky="w")

        # --- MONITORES VISUALES ---
        self.lbl_img_original = ctk.CTkLabel(self, text="[ RAW_INPUT ]", bg_color="#0a0a0a", corner_radius=5)
        self.lbl_img_original.grid(row=1, column=0, padx=10, pady=5, sticky="nsew")

        self.lbl_img_procesada = ctk.CTkLabel(self, text="[ VECTOR_MAP ]", bg_color="#0a0a0a", corner_radius=5)
        self.lbl_img_procesada.grid(row=1, column=1, padx=10, pady=5, sticky="nsew")

        # --- PANEL DE ACCIONES ---
        self.frame_actions = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_actions.grid(row=2, column=0, columnspan=2, padx=10, pady=10, sticky="ew")

        # Botones de Cámara
        ctk.CTkButton(self.frame_actions, text="CAM ON", command=self.toggle_camara, width=90).pack(side="left", padx=5)
        self.btn_capturar = ctk.CTkButton(self.frame_actions, text="SNAP", state="disabled", command=self.capturar_foto, width=90)
        self.btn_capturar.pack(side="left", padx=5)

        # Botones de Ejecución
        self.btn_dibujar = ctk.CTkButton(self.frame_actions, text="RUN ROBOT", fg_color="#1f612d", hover_color="#2ecc71", command=self.llamar_movimiento)
        self.btn_dibujar.pack(side="right", padx=5)

        # NUEVO BOTÓN: SIMULAR 3D
        self.btn_simular = ctk.CTkButton(self.frame_actions, text="SIMULAR 3D", fg_color="#8e44ad", hover_color="#9b59b6", command=self.abrir_simulador)
        self.btn_simular.pack(side="right", padx=5)

        self.btn_calcular = ctk.CTkButton(self.frame_actions, text="CALC", command=self.llamar_calculo, width=90)
        self.btn_calcular.pack(side="right", padx=5)

        self.btn_vision = ctk.CTkButton(self.frame_actions, text="VISION", command=self.llamar_vision, width=90)
        self.btn_vision.pack(side="right", padx=5)

        self.script_var = ctk.StringVar(value="1")
        ctk.CTkOptionMenu(self.frame_actions, values=["1", "2", "3"], variable=self.script_var, width=60).pack(side="right", padx=5)

        # --- TERMINAL DE ECUACIONES (EL DASHBOARD) ---
        self.textbox_formulas = ctk.CTkTextbox(self, font=("Consolas", 13), fg_color="#050505", text_color="#00ffcc", border_width=1, border_color="#333")
        self.textbox_formulas.grid(row=3, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")
        self.textbox_formulas.insert("0.0", ">> SYSTEM READY. AWAITING DATA...\n")

    # ==========================================
    # CONTROL DE CÁMARA
    # ==========================================
    def toggle_camara(self):
        if self.cap is None:
            self.cap = cv2.VideoCapture(0)
            if self.cap.isOpened():
                self.btn_capturar.configure(state="normal")
                self.actualizar_frame()
        else: self.apagar_camara()

    def actualizar_frame(self):
        if self.cap:
            ret, frame = self.cap.read()
            if ret:
                img = Image.fromarray(cv2.cvtColor(cv2.flip(frame, 1), cv2.COLOR_BGR2RGB))
                ctk_img = ctk.CTkImage(img, size=(400, 300))
                self.lbl_img_original.configure(image=ctk_img, text="")
                self.lbl_img_original.image = ctk_img
                self.after(15, self.actualizar_frame)

    def capturar_foto(self):
        if self.cap:
            ret, frame = self.cap.read()
            if ret:
                ruta = "/tmp/lynx_input.jpg"
                cv2.imwrite(ruta, frame)
                self.ruta_imagen_actual = ruta
                self.apagar_camara()
                self.mostrar_img(ruta, self.lbl_img_original)

    def apagar_camara(self):
        if self.cap: self.cap.release(); self.cap = None
        self.btn_capturar.configure(state="disabled")

    def mostrar_img(self, ruta, label):
        img = Image.open(ruta)
        img.thumbnail((450, 350))
        ctk_img = ctk.CTkImage(img, size=img.size)
        label.configure(image=ctk_img, text="")
        label.image = ctk_img

    # ==========================================
    # COMUNICACIÓN ROS 2 (THROUGHPUT SEGURO)
    # ==========================================
    def llamar_vision(self):
        if not self.ruta_imagen_actual: return
        self.log("Procesando visión...", nivel="INFO")
        self.ros_manager.solicitar_vision(self.ruta_imagen_actual, self.script_var.get(), self.callback_vision)

    def callback_vision(self, resp):
        self.after(0, lambda: self._ui_callback_vision(resp))

    def _ui_callback_vision(self, resp):
        if resp and resp.success:
            self.rutas_json_actual = resp.trajectories_json
            rutas = json.loads(resp.trajectories_json)
            self.log(f"Visión exitosa: {len(rutas)} trazos.", nivel="INFO")
            
            canvas = np.ones((480, 640, 3), dtype=np.uint8) * 255
            for r in rutas:
                if len(r) > 1:
                    pts = np.array(r, np.int32).reshape((-1,1,2))
                    cv2.polylines(canvas, [pts], False, (15,15,15), 2, cv2.LINE_AA)
            cv2.imwrite("/tmp/lynx_vision_output.jpg", canvas)
            self.mostrar_img("/tmp/lynx_vision_output.jpg", self.lbl_img_procesada)
        else: self.log("Error en Visión", nivel="ERROR")

    def llamar_calculo(self):
        if not self.rutas_json_actual: return
        self.log("Iniciando cálculo cinemático...", nivel="INFO")
        conf = json.dumps({'X_MIN': -100.0, 'X_MAX': 100.0, 'Y_MIN': 160.0, 'Y_MAX': 300.0, 'Z_DIBUJO': 0.0, 'Z_TRANSITO': 15.0})
        self.ros_manager.solicitar_calculo(self.rutas_json_actual, conf, 640, 480, 5.0, self.callback_calculo)

    def callback_calculo(self, resp):
        self.after(0, lambda: self._ui_callback_calculo(resp))

    def _ui_callback_calculo(self, resp):
        if resp and resp.success:
            self.matriz_json_actual = resp.matriz_espacial_json
            formulas = json.loads(resp.formulas_matematicas_json)
            
            self.textbox_formulas.delete("1.0", "end")
            self.textbox_formulas.insert("end", ">> ANALYSIS COMPLETED. KINEMATIC REPORT GENERATED.\n")
            self.textbox_formulas.insert("end", "═"*65 + "\n")

            for i, f in enumerate(formulas):
                f_math = f.replace("para 0 <= t <= 1", " ➜  t ∈ [0, 1]")
                f_math = f_math.replace("[", "⎧ ").replace("]", "").replace(",", "\n⎨")
                self.textbox_formulas.insert("end", f"SEG_{i+1:03d} {f_math}\n")
                self.textbox_formulas.insert("end", "─"*65 + "\n")
            
            self.log(f"Cálculo completado: {len(formulas)} segmentos.", nivel="INFO")
        else: self.log("Error en Cálculo", nivel="ERROR")

    # --- SIMULACIÓN Y MOVIMIENTO ---
    def abrir_simulador(self):
        """Dispara los datos al nodo animador de RViz"""
        if not self.matriz_json_actual:
            self.log("Error: Genera el cálculo cinemático primero.", nivel="WARN")
            return

        self.log("Transmitiendo coordenadas a RViz...", nivel="INFO")
        
        # Usamos el callback para confirmar que se mandó sin congelar la UI
        self.ros_manager.enviar_a_simulacion_rviz(
            self.matriz_json_actual, 
            lambda r: self.after(0, lambda: self.log("¡Simulación 3D en curso en RViz!", nivel="INFO"))
        )

    def llamar_movimiento(self):
        if not self.matriz_json_actual: return
        self.log("EJECUTANDO TRAYECTORIA EN ROBOT...", nivel="INFO")
        self.ros_manager.solicitar_movimiento(self.matriz_json_actual, lambda r: self.after(0, lambda: self.log("FIN DE TRAYECTORIA", nivel="INFO")))

    def cargar_archivo(self):
        ruta = filedialog.askopenfilename()
        if ruta: self.ruta_imagen_actual = ruta; self.mostrar_img(ruta, self.lbl_img_original)

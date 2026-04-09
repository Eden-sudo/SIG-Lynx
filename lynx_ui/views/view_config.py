import customtkinter as ctk
import serial.tools.list_ports
import threading

class ConfigView(ctk.CTkScrollableFrame):
    def __init__(self, master, config_manager, logger_func, **kwargs):
        super().__init__(master, **kwargs)

        self.config_manager = config_manager
        self.log = logger_func

        # Título principal
        self.titulo = ctk.CTkLabel(
            self, 
            text="⚙️ Panel de Calibración Maestra", 
            font=ctk.CTkFont(size=20, weight="bold")
        )
        self.titulo.grid(row=0, column=0, columnspan=2, pady=(20, 10), padx=20, sticky="w")

        # Variables de control
        self.entries_dim = {}
        self.entries_offset = {}
        self.puerto_seleccionado = ctk.StringVar(value="Buscando...")

        # Construcción de la interfaz
        self.crear_seccion_conexion(row=1)
        self.crear_seccion_dimensiones(row=2)
        self.crear_seccion_offsets(row=3)

        # Botón de guardado
        self.btn_guardar = ctk.CTkButton(
            self, 
            text="💾 GUARDAR CONFIGURACIÓN", 
            fg_color="#1f612d", 
            hover_color="#2ecc71", 
            command=self.guardar_configuracion
        )
        self.btn_guardar.grid(row=4, column=0, columnspan=2, pady=30, padx=20)

        # 1. Cargar datos del YAML inmediatamente
        self.cargar_configuracion()
        
        # 2. ESCANEO SEGURO: Esperamos 500ms a que la UI esté viva antes de tocar el hardware
        # Esto evita el Segmentation Fault en Arch Linux / Distrobox
        self.after(500, self.actualizar_puertos)

    def crear_seccion_conexion(self, row):
        frame = ctk.CTkFrame(self)
        frame.grid(row=row, column=0, columnspan=2, pady=10, padx=20, sticky="ew")
        
        ctk.CTkLabel(frame, text="🔌 Comunicación Serial", font=ctk.CTkFont(weight="bold")).grid(row=0, column=0, pady=10, padx=10, sticky="w")
        
        self.combo_puertos = ctk.CTkOptionMenu(
            frame, 
            variable=self.puerto_seleccionado, 
            values=["Escaneando..."]
        )
        self.combo_puertos.grid(row=1, column=0, pady=10, padx=20, sticky="w")
        
        btn_refresh = ctk.CTkButton(
            frame, 
            text="🔄 REFRESCAR", 
            width=100, 
            command=self.actualizar_puertos
        )
        btn_refresh.grid(row=1, column=1, pady=10, padx=10)

    def actualizar_puertos(self):
        """Escaneo de hardware con manejo de errores para evitar crasheos de memoria"""
        try:
            puertos_raw = serial.tools.list_ports.comports()
            ports = [str(port.device) for port in puertos_raw]
            
            if not ports:
                self.combo_puertos.configure(values=["No se detectan USB"])
                self.puerto_seleccionado.set("No se detectan USB")
            else:
                self.combo_puertos.configure(values=ports)
                # Mantener el puerto actual si sigue conectado, si no, poner el primero
                actual = self.puerto_seleccionado.get()
                if actual not in ports:
                    self.puerto_seleccionado.set(ports[0])
            
            self.log("Puertos USB actualizados con éxito.")
        except Exception as e:
            self.log(f"Fallo al escanear hardware: {e}", nivel="WARN")
            self.puerto_seleccionado.set("/dev/ttyUSB0")

    def crear_seccion_dimensiones(self, row):
        frame = ctk.CTkFrame(self)
        frame.grid(row=row, column=0, columnspan=2, pady=10, padx=20, sticky="ew")
        
        ctk.CTkLabel(frame, text="📏 Geometría del Brazo (mm)", font=ctk.CTkFont(weight="bold")).grid(row=0, column=0, pady=10, padx=10, sticky="w")

        # Incluimos L4 para la punta del efector
        dimensiones = [
            ("Base (L1)", "altura_base"), 
            ("Hombro (L2)", "brazo_superior"), 
            ("Codo (L3)", "antebrazo"), 
            ("Efector (L4)", "efector_final")
        ]
        for i, (label, key) in enumerate(dimensiones):
            ctk.CTkLabel(frame, text=f"{label}:").grid(row=i+1, column=0, pady=5, padx=(20, 5), sticky="e")
            entry = ctk.CTkEntry(frame, width=150)
            entry.grid(row=i+1, column=1, pady=5, padx=5, sticky="w")
            self.entries_dim[key] = entry

    def crear_seccion_offsets(self, row):
        frame = ctk.CTkFrame(self)
        frame.grid(row=row, column=0, columnspan=2, pady=10, padx=20, sticky="ew")
        
        ctk.CTkLabel(frame, text="⚖️ Calibración de Servos (Offsets)", font=ctk.CTkFont(weight="bold")).grid(row=0, column=0, pady=10, padx=10, sticky="w")

        articulaciones = [
            "joint_base_rotate", "joint_shoulder", "joint_elbow", 
            "joint_wrist", "joint_gripper_rotate", "joint_gripper_finger"
        ]
        for i, art in enumerate(articulaciones):
            ctk.CTkLabel(frame, text=f"{art}:").grid(row=i+1, column=0, pady=5, padx=(20, 5), sticky="e")
            entry = ctk.CTkEntry(frame, width=150)
            entry.grid(row=i+1, column=1, pady=5, padx=5, sticky="w")
            self.entries_offset[art] = entry

    def cargar_configuracion(self):
        config = self.config_manager.cargar()
        if not config: return

        # Cargar puerto guardado
        self.puerto_seleccionado.set(config.get("puerto_serial", "/dev/ttyUSB0"))

        # Cargar dimensiones
        dims = config.get("dimensiones_brazo", {})
        for key, entry in self.entries_dim.items():
            entry.delete(0, "end")
            entry.insert(0, str(dims.get(key, 0.0)))

        # Cargar offsets
        arts = config.get("articulaciones", {})
        for key, entry in self.entries_offset.items():
            entry.delete(0, "end")
            datos_art = arts.get(key, {})
            entry.insert(0, str(datos_art.get("offset_grados", 0)))
            
        self.log("Parámetros de hardware sincronizados.")

    def guardar_configuracion(self):
        # Cargamos el estado actual para no perder campos extra (canales, etc)
        config = self.config_manager.cargar() or {"dimensiones_brazo": {}, "articulaciones": {}}

        try:
            config["puerto_serial"] = self.puerto_seleccionado.get()
            
            # Actualizar dimensiones
            for key, entry in self.entries_dim.items():
                config["dimensiones_brazo"][key] = float(entry.get())

            # Actualizar articulaciones
            for key, entry in self.entries_offset.items():
                if key not in config["articulaciones"]:
                    config["articulaciones"][key] = {"canal": 0, "offset_grados": 0}
                config["articulaciones"][key]["offset_grados"] = float(entry.get())

            if self.config_manager.guardar(config):
                self.log(f"Éxito: Configuración aplicada en {config['puerto_serial']}")
            else:
                self.log("Error crítico: No se pudo escribir en config_motores.yaml", nivel="ERROR")

        except ValueError:
            self.log("Error: Formato numérico inválido en dimensiones u offsets.", nivel="WARN")

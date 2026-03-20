import customtkinter as ctk

class ConfigView(ctk.CTkScrollableFrame):
    def __init__(self, master, config_manager, logger_func, **kwargs):
        super().__init__(master, **kwargs)

        self.config_manager = config_manager
        self.log = logger_func

        self.titulo = ctk.CTkLabel(self, text="Configuración de Hardware (YAML)", font=ctk.CTkFont(size=20, weight="bold"))
        self.titulo.grid(row=0, column=0, columnspan=2, pady=(20, 10), padx=20, sticky="w")

        # Diccionarios para guardar las referencias a las cajas de texto (Entradas)
        self.entries_dim = {}
        self.entries_offset = {}

        # Construcción visual de las secciones
        self.crear_seccion_dimensiones(row=1)
        self.crear_seccion_offsets(row=2)

        self.btn_guardar = ctk.CTkButton(self, text="💾 Guardar Configuración", command=self.guardar_configuracion)
        self.btn_guardar.grid(row=3, column=0, columnspan=2, pady=30, padx=20)

        # Cargar los datos automáticamente al instanciar la vista
        self.cargar_configuracion()

    def crear_seccion_dimensiones(self, row):
        frame = ctk.CTkFrame(self)
        frame.grid(row=row, column=0, columnspan=2, pady=10, padx=20, sticky="ew")
        
        lbl_titulo = ctk.CTkLabel(frame, text="Dimensiones Físicas (mm)", font=ctk.CTkFont(weight="bold"))
        lbl_titulo.grid(row=0, column=0, pady=10, padx=10, sticky="w")

        dimensiones = ["L1", "L2", "L3"]
        for i, dim in enumerate(dimensiones):
            lbl = ctk.CTkLabel(frame, text=f"{dim}:")
            lbl.grid(row=i+1, column=0, pady=5, padx=(20, 5), sticky="e")
            
            entry = ctk.CTkEntry(frame, width=150)
            entry.grid(row=i+1, column=1, pady=5, padx=5, sticky="w")
            self.entries_dim[dim] = entry

    def crear_seccion_offsets(self, row):
        frame = ctk.CTkFrame(self)
        frame.grid(row=row, column=0, columnspan=2, pady=10, padx=20, sticky="ew")
        
        lbl_titulo = ctk.CTkLabel(frame, text="Offsets de Articulaciones (Grados)", font=ctk.CTkFont(weight="bold"))
        lbl_titulo.grid(row=0, column=0, pady=10, padx=10, sticky="w")

        articulaciones = [
            "joint_base_rotate", "joint_shoulder", "joint_elbow", 
            "joint_wrist", "joint_gripper_rotate", "joint_gripper_finger"
        ]
        
        for i, art in enumerate(articulaciones):
            lbl = ctk.CTkLabel(frame, text=f"{art}:")
            lbl.grid(row=i+1, column=0, pady=5, padx=(20, 5), sticky="e")
            
            entry = ctk.CTkEntry(frame, width=150)
            entry.grid(row=i+1, column=1, pady=5, padx=5, sticky="w")
            self.entries_offset[art] = entry

    def cargar_configuracion(self):
        """Lee el YAML a través del manager y rellena los campos."""
        config = self.config_manager.cargar()
        if not config:
            self.log("Advertencia: No se pudo cargar el YAML o está vacío.")
            return

        # Rellenar Dimensiones
        dims = config.get("dimensiones_brazo", {})
        for key, entry in self.entries_dim.items():
            entry.delete(0, "end")
            entry.insert(0, str(dims.get(key, 0.0)))

        # Rellenar Offsets
        arts = config.get("articulaciones", {})
        for key, entry in self.entries_offset.items():
            entry.delete(0, "end")
            datos_art = arts.get(key, {})
            entry.insert(0, str(datos_art.get("offset_grados", 0)))
            
        self.log("Configuración de motores cargada en la interfaz.")

    def guardar_configuracion(self):
        """Recopila los datos de los campos, actualiza el diccionario y guarda en YAML."""
        # Se carga el YAML original primero para no borrar los datos de "canal" ni "invertido"
        config = self.config_manager.cargar()
        if not config:
            config = {"dimensiones_brazo": {}, "articulaciones": {}}

        if "dimensiones_brazo" not in config: config["dimensiones_brazo"] = {}
        if "articulaciones" not in config: config["articulaciones"] = {}

        try:
            # Extraer y validar Dimensiones
            for key, entry in self.entries_dim.items():
                config["dimensiones_brazo"][key] = float(entry.get())

            # Extraer y validar Offsets
            for key, entry in self.entries_offset.items():
                if key not in config["articulaciones"]:
                    config["articulaciones"][key] = {"canal": 0, "offset_grados": 0, "invertido": False}
                
                config["articulaciones"][key]["offset_grados"] = float(entry.get())

            # Enviar a disco
            exito = self.config_manager.guardar(config)
            if exito:
                self.log("Configuración YAML guardada. Los cambios aplicarán en el siguiente movimiento.")
            else:
                self.log("Error al intentar guardar el archivo YAML.")

        except ValueError:
            self.log("Error de formato: Por favor, ingresa solo números (usa '.' para decimales).")

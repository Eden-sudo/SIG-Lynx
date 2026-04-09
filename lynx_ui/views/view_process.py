import customtkinter as ctk

class ProcessView(ctk.CTkFrame):
    def __init__(self, master, process_manager, logger_func, **kwargs):
        super().__init__(master, **kwargs)
        
        self.process_manager = process_manager
        self.log = logger_func # Función para escribir en la consola principal

        self.titulo = ctk.CTkLabel(self, text="Gestión de Nodos ROS 2", font=ctk.CTkFont(size=20, weight="bold"))
        self.titulo.grid(row=0, column=0, pady=20, padx=20, sticky="w")

        # Variables de estado
        self.var_sim3d = ctk.BooleanVar(value=False)
        self.var_vision = ctk.BooleanVar(value=False)
        self.var_calculo = ctk.BooleanVar(value=False)
        self.var_hardware = ctk.BooleanVar(value=False)
        self.var_server = ctk.BooleanVar(value=False)

        # 1. Simulación (RViz)
        self.crear_fila_proceso("Simulación 3D (ROS 2 + RViz)", self.var_sim3d, "simulacion_3d", row=1)
        
        # 2. Visión Artificial
        self.crear_fila_proceso("Servicio de Visión Artificial", self.var_vision, "vision", row=2)
        
        # 3. Cálculo Cinemático
        self.crear_fila_proceso("Servicio de Cálculo Cinemático", self.var_calculo, "calculo", row=3)

        # 4. Hardware Real (SSC-32U) - NUEVO
        self.crear_fila_proceso("Controlador de Hardware (AL5D)", self.var_hardware, "hardware", row=4)

        # 5. Servidor Web Backend
        self.crear_fila_proceso("Servidor Web Backend", self.var_server, "servidor", row=5)

        self.grid_columnconfigure(0, weight=1)

    def crear_fila_proceso(self, texto_etiqueta, variable_control, nombre_id, row):
        """Metodo unificado para crear filas de procesos de manera limpia"""
        frame = ctk.CTkFrame(self, fg_color="#2b2b2b", corner_radius=8)
        frame.grid(row=row, column=0, pady=5, padx=20, sticky="ew")
        
        frame.grid_columnconfigure(0, weight=1)

        lbl = ctk.CTkLabel(frame, text=texto_etiqueta, font=ctk.CTkFont(size=14))
        lbl.grid(row=0, column=0, padx=15, pady=10, sticky="w")
        
        # Al hacer clic, se llama a on_switch_toggle con el ID correspondiente
        sw = ctk.CTkSwitch(
            frame, 
            text="", 
            variable=variable_control, 
            command=lambda id=nombre_id, var=variable_control: self.on_switch_toggle(id, var.get())
        )
        sw.grid(row=0, column=1, padx=15, pady=10, sticky="e")

    def on_switch_toggle(self, nombre_id, estado_encendido):
        """Centraliza la orden hacia el RosManager para TODOS los procesos"""
        self.process_manager.alternar_proceso(nombre_id, estado_encendido, self.log)

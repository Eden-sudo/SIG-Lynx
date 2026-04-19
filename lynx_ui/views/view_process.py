import customtkinter as ctk

class ProcessView(ctk.CTkFrame):
    def __init__(self, master, process_manager, logger_func, **kwargs):
        super().__init__(master, **kwargs)
        
        self.process_manager = process_manager
        self.log = logger_func # Function to write to the main console log

        self.titulo = ctk.CTkLabel(self, text="ROS 2 Node Management", font=ctk.CTkFont(size=20, weight="bold"))
        self.titulo.grid(row=0, column=0, pady=20, padx=20, sticky="w")

        # State Variables
        self.var_sim3d = ctk.BooleanVar(value=False)
        self.var_vision = ctk.BooleanVar(value=False)
        self.var_calculo = ctk.BooleanVar(value=False)
        self.var_hardware = ctk.BooleanVar(value=False)
        self.var_server = ctk.BooleanVar(value=False)

        # 1. 3D Simulation (RViz)
        self.crear_fila_proceso("3D Simulation (ROS 2 + RViz)", self.var_sim3d, "simulacion_3d", row=1)
        
        # 2. Computer Vision
        self.crear_fila_proceso("Computer Vision Service", self.var_vision, "vision", row=2)
        
        # 3. Kinematic Calculus
        self.crear_fila_proceso("Kinematic Calculus Service", self.var_calculo, "calculo", row=3)

        # 4. Real Hardware (SSC-32U)
        self.crear_fila_proceso("Hardware Controller (AL5D)", self.var_hardware, "hardware", row=4)

        # 5. Web Backend Server
        self.crear_fila_proceso("Web Backend Server", self.var_server, "servidor", row=5)

        self.grid_columnconfigure(0, weight=1)

    def crear_fila_proceso(self, texto_etiqueta, variable_control, nombre_id, row):
        """Unified method to cleanly create process rows"""
        frame = ctk.CTkFrame(self, fg_color="#2b2b2b", corner_radius=8)
        frame.grid(row=row, column=0, pady=5, padx=20, sticky="ew")
        
        frame.grid_columnconfigure(0, weight=1)

        lbl = ctk.CTkLabel(frame, text=texto_etiqueta, font=ctk.CTkFont(size=14))
        lbl.grid(row=0, column=0, padx=15, pady=10, sticky="w")
        
        # Triggers on_switch_toggle with the corresponding ID on click
        sw = ctk.CTkSwitch(
            frame,  
            text="",  
            variable=variable_control,  
            command=lambda id=nombre_id, var=variable_control: self.on_switch_toggle(id, var.get())
        )
        sw.grid(row=0, column=1, padx=15, pady=10, sticky="e")

    def on_switch_toggle(self, nombre_id, estado_encendido):
        """Centralizes commands to the ProcessManager for ALL processes"""
        self.process_manager.alternar_proceso(nombre_id, estado_encendido, self.log)

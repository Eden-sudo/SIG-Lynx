import customtkinter as ctk

class ProcessView(ctk.CTkFrame):
    def __init__(self, master, process_manager, logger_func, **kwargs):
        super().__init__(master, **kwargs)
        
        self.process_manager = process_manager
        self.log = logger_func # Función para escribir en la consola principal

        self.titulo = ctk.CTkLabel(self, text="Gestión de Procesos Externos", font=ctk.CTkFont(size=20, weight="bold"))
        self.titulo.grid(row=0, column=0, pady=20, padx=20, sticky="w")

        # --- SIMULACIÓN (RViz) ---
        self.frame_sim = ctk.CTkFrame(self)
        self.frame_sim.grid(row=1, column=0, pady=10, padx=20, sticky="ew")
        
        self.lbl_sim = ctk.CTkLabel(self.frame_sim, text="Simulación 3D (ROS 2 + RViz)")
        self.lbl_sim.grid(row=0, column=0, padx=15, pady=10, sticky="w")
        
        self.switch_sim = ctk.CTkSwitch(self.frame_sim, text="", command=self.toggle_simulacion)
        self.switch_sim.grid(row=0, column=1, padx=15, pady=10, sticky="e")

        # --- SERVIDOR WEB ---
        self.frame_server = ctk.CTkFrame(self)
        self.frame_server.grid(row=2, column=0, pady=10, padx=20, sticky="ew")
        
        self.lbl_server = ctk.CTkLabel(self.frame_server, text="Servidor Backend Web")
        self.lbl_server.grid(row=0, column=0, padx=15, pady=10, sticky="w")
        
        self.switch_server = ctk.CTkSwitch(self.frame_server, text="", command=self.toggle_servidor)
        self.switch_server.grid(row=0, column=1, padx=15, pady=10, sticky="e")

        # Configurar expansión de columnas
        self.grid_columnconfigure(0, weight=1)
        self.frame_sim.grid_columnconfigure(0, weight=1)
        self.frame_server.grid_columnconfigure(0, weight=1)

    def toggle_simulacion(self):
        if self.switch_sim.get() == 1:
            self.log("Levantando entorno RViz...")
            if not self.process_manager.iniciar_simulacion():
                self.log("Error al iniciar RViz.")
                self.switch_sim.deselect()
        else:
            self.log("Deteniendo RViz...")
            self.process_manager.detener_simulacion()

    def toggle_servidor(self):
        if self.switch_server.get() == 1:
            self.log("Iniciando servidor web...")
            if not self.process_manager.iniciar_servidor():
                self.log("Error al iniciar el servidor.")
                self.switch_server.deselect()
        else:
            self.log("Deteniendo servidor web...")
            self.process_manager.detener_servidor()

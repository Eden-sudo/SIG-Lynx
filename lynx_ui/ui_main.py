import customtkinter as ctk
import time

# Importar Gestores
from process_manager import ProcessManager
from config_manager import ConfigManager
from ros_client_manager import RosManager

# Importar Vistas
from views.view_config import ConfigView
from views.view_process import ProcessView
from views.view_operation import OperationView

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class LynxApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("SIG-Lynx Control Panel")
        self.geometry("1100x700")

        # 1. Inicializar Gestores
        self.process_manager = ProcessManager()
        self.config_manager = ConfigManager()
        self.ros_manager = RosManager()

        # 2. Configurar Grid Principal (1 fila, 2 columnas)
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # 3. Panel Lateral (Menú de navegación)
        self.frame_sidebar = ctk.CTkFrame(self, width=200, corner_radius=0)
        self.frame_sidebar.grid(row=0, column=0, sticky="nsew")
        
        self.logo_label = ctk.CTkLabel(self.frame_sidebar, text="SIG-Lynx", font=ctk.CTkFont(size=24, weight="bold"))
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 30))

        self.btn_nav_config = ctk.CTkButton(self.frame_sidebar, text="⚙ Configuración", fg_color="transparent", border_width=2, text_color=("gray10", "#DCE4EE"), command=lambda: self.seleccionar_frame("config"))
        self.btn_nav_config.grid(row=1, column=0, padx=20, pady=10, sticky="ew")

        self.btn_nav_process = ctk.CTkButton(self.frame_sidebar, text="Procesos", fg_color="transparent", border_width=2, text_color=("gray10", "#DCE4EE"), command=lambda: self.seleccionar_frame("process"))
        self.btn_nav_process.grid(row=2, column=0, padx=20, pady=10, sticky="ew")

        self.btn_nav_operacion = ctk.CTkButton(self.frame_sidebar, text="Operacion", fg_color="transparent", border_width=2, text_color=("gray10", "#DCE4EE"), command=lambda: self.seleccionar_frame("operacion"))
        self.btn_nav_operacion.grid(row=3, column=0, padx=20, pady=10, sticky="ew")

        # 4. Consola Global
        self.textbox_log = ctk.CTkTextbox(self.frame_sidebar, font=ctk.CTkFont(family="monospace", size=11), height=200)
        self.textbox_log.grid(row=5, column=0, padx=10, pady=20, sticky="s")
        self.frame_sidebar.grid_rowconfigure(4, weight=1)

        # 5. Instanciar las Vistas (Frames)
        self.frame_config = ConfigView(self, self.config_manager, self.log, corner_radius=0, fg_color="transparent")
        
        # CORRECCIÓN: Le pasamos ros_manager a ProcessView para que controle los nodos de ROS
        self.frame_process = ProcessView(self, self.ros_manager, self.log, corner_radius=0, fg_color="transparent")
        
        self.frame_operacion = OperationView(self, self.ros_manager, self.log, corner_radius=0, fg_color="transparent")

        # Seleccionar vista por defecto
        self.seleccionar_frame("process")
        self.log("Sistema iniciado. Interfaz cargada.")

    def log(self, mensaje, nivel="INFO", detalle=None):
        hora = time.strftime("%H:%M:%S")

        if nivel == "ERROR":
            prefijo = "[ERROR]"
            color = "\033[91m"  # Rojo
        elif nivel == "WARN":
            prefijo = "[WARN] "
            color = "\033[93m"  # Amarillo
        else:
            prefijo = "[INFO] "
            color = "\033[94m"  # Azul claro

        reset_color = "\033[0m"

        mensaje_base = f"[{hora}] {prefijo} {mensaje}"

        if detalle:
            mensaje_ui = f"{mensaje_base}\n{detalle}\n"
            mensaje_terminal = f"{color}{mensaje_base}\n{detalle}{reset_color}"
        else:
            mensaje_ui = f"{mensaje_base}\n"
            mensaje_terminal = f"{color}{mensaje_base}{reset_color}"

        self.textbox_log.insert("end", mensaje_ui)
        self.textbox_log.see("end")
        print(mensaje_terminal)

    def seleccionar_frame(self, nombre_frame):
        self.frame_config.grid_forget()
        self.frame_process.grid_forget()
        self.frame_operacion.grid_forget()

        self.btn_nav_config.configure(fg_color="transparent")
        self.btn_nav_process.configure(fg_color="transparent")
        self.btn_nav_operacion.configure(fg_color="transparent")

        if nombre_frame == "config":
            self.frame_config.grid(row=0, column=1, sticky="nsew")
            self.btn_nav_config.configure(fg_color=("gray75", "gray25"))
        elif nombre_frame == "process":
            self.frame_process.grid(row=0, column=1, sticky="nsew")
            self.btn_nav_process.configure(fg_color=("gray75", "gray25"))
        elif nombre_frame == "operacion":
            self.frame_operacion.grid(row=0, column=1, sticky="nsew")
            self.btn_nav_operacion.configure(fg_color=("gray75", "gray25"))

    def destroy(self):
        """Sobrescribir el cierre de ventana para apagar procesos de forma segura."""
        self.log("Apagando sistema...")
        if hasattr(self, 'process_manager'):
            self.process_manager.limpiar_todo()
            
        # CORRECCIÓN VITAL: Descomentado para matar los procesos hijos (RViz, Nodos ROS)
        if hasattr(self, 'ros_manager'):
            self.ros_manager.detener()
            
        super().destroy()

if __name__ == "__main__":
    app = LynxApp()
    app.mainloop()

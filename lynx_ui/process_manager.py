import subprocess
import os
import signal

class ProcessManager:
    """Gestiona la ejecucion y terminacion de procesos externos a la UI."""
    def __init__(self):
        self.proceso_simulacion = None
        self.proceso_servidor = None

        # Calcula la ruta absoluta al script del servidor web
        directorio_actual = os.path.dirname(os.path.abspath(__file__))
        self.ruta_servidor = os.path.abspath(os.path.join(
            directorio_actual, '..', 'lynx_server', 'main.py' # Ajusta 'main.py' al nombre real de tu script
        ))

    def iniciar_simulacion(self):
        if self.proceso_simulacion is None:
            comando = ["ros2", "launch", "lynx_motion_core", "simulacion.launch.py"]
            
            # preexec_fn=os.setsid agrupa RViz y el publicador de estados para cerrarlos juntos
            self.proceso_simulacion = subprocess.Popen(
                comando,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                preexec_fn=os.setsid
            )
            return True
        return False

    def detener_simulacion(self):
        if self.proceso_simulacion is not None:
            try:
                os.killpg(os.getpgid(self.proceso_simulacion.pid), signal.SIGTERM)
                self.proceso_simulacion.wait(timeout=3)
            except Exception as e:
                print(f"[ProcessManager] Error deteniendo simulacion: {e}")
            finally:
                self.proceso_simulacion = None
            return True
        return False

    def iniciar_servidor(self):
        if self.proceso_servidor is None:
            if not os.path.exists(self.ruta_servidor):
                print(f"[ProcessManager] Archivo del servidor no encontrado: {self.ruta_servidor}")
                return False
                
            comando = ["python", self.ruta_servidor]
            
            self.proceso_servidor = subprocess.Popen(
                comando,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                preexec_fn=os.setsid
            )
            return True
        return False

    def detener_servidor(self):
        if self.proceso_servidor is not None:
            try:
                os.killpg(os.getpgid(self.proceso_servidor.pid), signal.SIGTERM)
                self.proceso_servidor.wait(timeout=3)
            except Exception as e:
                print(f"[ProcessManager] Error deteniendo servidor: {e}")
            finally:
                self.proceso_servidor = None
            return True
        return False

    def limpiar_todo(self):
        """Metodo de seguridad llamado al cerrar la ventana principal de la UI."""
        self.detener_simulacion()
        self.detener_servidor()

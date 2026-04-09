import subprocess
import os
import signal
import time

class ProcessManager:
    """Gestiona la ejecucion y terminacion de procesos externos (ROS 2) desde la UI."""
    def __init__(self):
        self.proceso_simulacion = None
        self.proceso_servidor = None
        self.proceso_vision = None
        self.proceso_calculo = None

        # Rutas dinamicas
        self.directorio_actual = os.path.dirname(os.path.abspath(__file__))
        self.ruta_raiz_proyecto = os.path.abspath(os.path.join(self.directorio_actual, '..'))
        self.ruta_setup_ros = os.path.join(self.ruta_raiz_proyecto, 'install', 'setup.bash')
        self.ruta_servidor = os.path.join(self.ruta_raiz_proyecto, 'lynx_server', 'main.py')

    def iniciar_simulacion(self):
        if self.proceso_simulacion is None:
            comando = f"source {self.ruta_setup_ros} && ros2 launch lynx_motion_core simulacion.launch.py"
            self.proceso_simulacion = self._lanzar(comando)
            return True
        return False

    def iniciar_vision(self):
        if self.proceso_vision is None:
            comando = f"source {self.ruta_setup_ros} && ros2 run lynx_motion_core vision_service"
            self.proceso_vision = self._lanzar(comando)
            return True
        return False

    def iniciar_calculo_service(self):
        if self.proceso_calculo is None:
            comando = f"source {self.ruta_setup_ros} && ros2 run lynx_motion_core calculus_service"
            self.proceso_calculo = self._lanzar(comando)
            return True
        return False

    def _lanzar(self, comando):
        return subprocess.Popen(
            comando, shell=True, executable='/bin/bash',
            stdout=subprocess.DEVNULL, stderr=None, preexec_fn=os.setsid
        )

    def detener_simulacion(self):
        if self.proceso_simulacion: self._matar(self.proceso_simulacion); self.proceso_simulacion = None
        
    def detener_vision(self):
        if self.proceso_vision: self._matar(self.proceso_vision); self.proceso_vision = None

    def detener_calculo_service(self):
        if self.proceso_calculo: self._matar(self.proceso_calculo); self.proceso_calculo = None

    def _matar(self, proceso):
        try: os.killpg(os.getpgid(proceso.pid), signal.SIGTERM)
        except: pass

    def limpiar_todo(self):
        self.detener_simulacion()
        self.detener_vision()
        self.detener_calculo_service()

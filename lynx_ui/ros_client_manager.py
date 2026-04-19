import rclpy
from rclpy.node import Node
import threading
import time
import subprocess
import os
import signal  

from lynx_interfaces.srv import ProcesarVision, ProcesarCalculo, EjecutarMovimiento

class RosClientNode(Node):
    """Container for ROS 2 clients"""
    def __init__(self):
        super().__init__('ui_ros_client')
        self.cli_vision = self.create_client(ProcesarVision, 'procesar_imagen_vision')
        self.cli_calculo = self.create_client(ProcesarCalculo, 'procesar_calculo_trayectoria')
        self.cli_movimiento = self.create_client(EjecutarMovimiento, 'ejecutar_movimiento_robot')

class RosManager:
    """Manager for background services, threads, and asynchronous requests"""
    def __init__(self):
        # Dictionary to store live processes controlled by switches
        self.procesos_activos = {}
        
        # Initialize ROS 2 and Client Node
        rclpy.init(args=None)
        self.node = RosClientNode()
        
        # Thread to keep ROS alive without blocking the UI
        self.spin_thread = threading.Thread(target=self._spin, daemon=True)
        self.spin_thread.start()

    # ==========================================
    # DYNAMIC PROCESS MANAGEMENT (For Switches)
    # ==========================================
    
    def alternar_proceso(self, nombre_proceso, encender, logger_func):
        """Turns a ROS 2 service on or off based on switch state"""
        
        comandos = {
            "vision": "ros2 run lynx_motion_core vision_service",
            "calculo": "ros2 run lynx_motion_core calculus_service",
            "hardware": "ros2 run lynx_motion_core motion_service",
            "simulacion_3d": "unset QT_QPA_PLATFORM_PLUGIN_PATH && ros2 launch lynx_al5d_ros2_description display.launch.py gui:=false & sleep 4 && ros2 run lynx_motion_core rviz_animator",
            "servidor": "cd /home/Eden/Desktop/lynx_calculus_project/lynx_server && python launch_server.py"
        }

        if encender:
            if nombre_proceso not in self.procesos_activos and nombre_proceso in comandos:
                logger_func(f"[{nombre_proceso.upper()}] Starting service...")
                
                # CRITICAL FIX: Removed DEVNULL.  
                # Now it inherits the main terminal, allowing ROS 2 errors to be visible.
                p = subprocess.Popen(
                    ["bash", "-c", comandos[nombre_proceso]],  
                    preexec_fn=os.setsid
                )
                self.procesos_activos[nombre_proceso] = p
                logger_func(f"[{nombre_proceso.upper()}] ONLINE (PID: {p.pid}).")
        else:
            if nombre_proceso in self.procesos_activos:
                logger_func(f"[{nombre_proceso.upper()}] Shutting down service...")
                p = self.procesos_activos.pop(nombre_proceso)
                try:
                    os.killpg(os.getpgid(p.pid), signal.SIGTERM)
                except ProcessLookupError:
                    pass
                logger_func(f"[{nombre_proceso.upper()}] OFFLINE.")

    def _spin(self):
        rclpy.spin(self.node)

    def detener(self):
        """Shuts down live services and closes ROS cleanly on exit"""
        print("[ROS Manager] Closing services and cleaning up processes...")
        for nombre in list(self.procesos_activos.keys()):
            self.alternar_proceso(nombre, False, print)
        self.node.destroy_node()
        rclpy.shutdown()

    # ==========================================
    # CALL METHODS (To be used by the UI)
    # ==========================================
    
    def solicitar_vision(self, ruta_imagen, script_id, callback):
        def _task():
            if not self.node.cli_vision.wait_for_service(timeout_sec=5.0):
                print("[ROS Manager] Error: Vision service is not responding.")
                callback(None)
                return

            req = ProcesarVision.Request()
            req.image_path = ruta_imagen
            req.script_id = int(script_id)
            
            future = self.node.cli_vision.call_async(req)
            while not future.done():
                time.sleep(0.1)
            callback(future.result())
            
        threading.Thread(target=_task, daemon=True).start()

    def solicitar_calculo(self, rutas_json, config_espacio_json, w_img, h_img, delta_paso, callback):
        def _task():
            if not self.node.cli_calculo.wait_for_service(timeout_sec=5.0):
                print("[ROS Manager] Error: Calculus service is not responding.")
                callback(None)
                return

            req = ProcesarCalculo.Request()
            req.rutas_json = rutas_json
            req.config_espacio_json = config_espacio_json
            req.w_img = int(w_img)
            req.h_img = int(h_img)
            req.delta_paso = float(delta_paso)
            
            future = self.node.cli_calculo.call_async(req)
            while not future.done():
                time.sleep(0.1)
            callback(future.result())
            
        threading.Thread(target=_task, daemon=True).start()

    def solicitar_movimiento(self, matriz_json, callback):
        def _task():
            if not self.node.cli_movimiento.wait_for_service(timeout_sec=5.0):
                print("[ROS Manager] Critical Error: AL5D hardware is not responding.")
                callback(None)
                return

            req = EjecutarMovimiento.Request()
            req.matriz_espacial_json = matriz_json
            
            future = self.node.cli_movimiento.call_async(req)
            
            while not future.done():
                time.sleep(0.2)
                
            callback(future.result())
                
        threading.Thread(target=_task, daemon=True).start()

    def enviar_a_simulacion_rviz(self, matriz_json, callback):
        def _task():
            from std_msgs.msg import String
            if not hasattr(self, 'sim_pub'):
                self.sim_pub = self.node.create_publisher(String, '/simular_trayectoria', 10)
            
            msg = String()
            msg.data = matriz_json
            self.sim_pub.publish(msg)
            
            time.sleep(0.5)  
            callback({"success": True})
            
        threading.Thread(target=_task, daemon=True).start()

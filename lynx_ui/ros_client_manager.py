import rclpy
from rclpy.node import Node
import threading

from lynx_interfaces.srv import ProcesarVision, ProcesarCalculo, EjecutarMovimiento

class RosClientNode(Node):
    """Contenedor de los clientes de ROS 2"""
    def __init__(self):
        super().__init__('ui_ros_client')
        self.cli_vision = self.create_client(ProcesarVision, 'procesar_imagen_vision')
        self.cli_calculo = self.create_client(ProcesarCalculo, 'procesar_calculo_trayectoria')
        self.cli_movimiento = self.create_client(EjecutarMovimiento, 'ejecutar_trayectoria')

class RosManager:
    """Gestor de hilos y peticiones para evitar bloqueos en la UI"""
    def __init__(self):
        rclpy.init(args=None)
        self.node = RosClientNode()
        
        # Mantiene las comunicaciones de ROS vivas en segundo plano
        self.spin_thread = threading.Thread(target=self._spin, daemon=True)
        self.spin_thread.start()

    def _spin(self):
        rclpy.spin(self.node)

    def detener(self):
        self.node.destroy_node()
        rclpy.shutdown()

    # ==========================================
    # METODOS DE LLAMADA (Usados por la UI)
    # ==========================================
    
    def solicitar_vision(self, ruta_imagen, script_id, callback):
        def _task():
            if not self.node.cli_vision.wait_for_service(timeout_sec=3.0):
                print("[ROS Manager] Error: El nodo vision_service no esta corriendo.")
                class RespuestaFallida:
                    success = False
                    error_message = "vision_service no disponible o apagado."
                callback(RespuestaFallida())
                return

            req = ProcesarVision.Request()
            req.image_path = ruta_imagen
            req.script_id = int(script_id)
            
            future = self.node.cli_vision.call_async(req)
            response = future.result() 
            callback(response)
            
        threading.Thread(target=_task, daemon=True).start()

    def solicitar_calculo(self, rutas_json, config_espacio_json, w_img, h_img, delta_paso, callback):
        def _task():
            self.node.cli_calculo.wait_for_service()
            req = ProcesarCalculo.Request()
            req.rutas_json = rutas_json
            req.config_espacio_json = config_espacio_json
            req.w_img = int(w_img)
            req.h_img = int(h_img)
            req.delta_paso = float(delta_paso)
            
            future = self.node.cli_calculo.call_async(req)
            response = future.result()
            callback(response)
            
        threading.Thread(target=_task, daemon=True).start()

    def solicitar_movimiento(self, matriz_espacial_json, callback):
        def _task():
            self.node.cli_movimiento.wait_for_service()
            req = EjecutarMovimiento.Request()
            req.matriz_espacial_json = matriz_espacial_json
            
            future = self.node.cli_movimiento.call_async(req)
            response = future.result()
            callback(response)
            
        threading.Thread(target=_task, daemon=True).start()

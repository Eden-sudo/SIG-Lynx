import rclpy
from rclpy.node import Node
import cv2
import json
import os

from lynx_interfaces.srv import ProcesarVision
from lynx_motion_core.vision import vision_01, vision_02, vision_03

class VisionWrapperService(Node):
    def __init__(self):
        super().__init__('vision_wrapper_service')
        self.srv = self.create_service(ProcesarVision, 'procesar_imagen_vision', self.procesar_callback)
        self.get_logger().info('>>> SERVICIO DE VISIÓN LYNX INICIADO (MODO UNIVERSAL) <<<')

    def procesar_callback(self, request, response):
        ruta = request.image_path
        sid = request.script_id

        if not os.path.exists(ruta):
            response.success = False
            response.error_message = f"Ruta inválida: {ruta}"
            return response

        frame = cv2.imread(ruta)
        try:
            # LLAMADA DINÁMICA
            if sid == 1:   res = vision_01.procesar_frame(frame)
            elif sid == 2: res = vision_02.procesar_frame(frame)
            elif sid == 3: res = vision_03.procesar_frame(frame)
            else: raise ValueError(f"Script ID {sid} no implementado")

            # EXTRACCIÓN SEGURA: Siempre tomamos el primer elemento [0]
            # Esto funciona si el script devuelve (rutas, img) o (rutas, img, mas_cosas)
            if isinstance(res, (tuple, list)):
                rutas_extraidas = res[0]
            else:
                rutas_extraidas = res

            response.trajectories_json = json.dumps(rutas_extraidas)
            response.success = True
            self.get_logger().info(f'Script {sid} OK | Trazos: {len(rutas_extraidas)}')

        except Exception as e:
            response.success = False
            response.error_message = f"Error en procesamiento: {str(e)}"
            self.get_logger().error(f"Fallo crítico: {traceback.format_exc() if 'traceback' in globals() else e}")
            
        return response

def main(args=None):
    rclpy.init(args=args)
    node = VisionWrapperService()
    try: rclpy.spin(node)
    except KeyboardInterrupt: pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

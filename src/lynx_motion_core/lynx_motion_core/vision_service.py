import rclpy
from rclpy.node import Node
import cv2
import json
import os

from lynx_interfaces.srv import ProcesarVision

from lynx_motion_core.vision import vision_01
from lynx_motion_core.vision import vision_02
from lynx_motion_core.vision import vision_03

class VisionWrapperService(Node):
    """
    Nodo servidor de ROS 2 para procesamiento de visión.
    Expone un servicio que recibe la ruta de una imagen en disco y un ID de script.
    Aplica la lógica matemática correspondiente y retorna las rutas extraídas en formato JSON.
    """
    def __init__(self):
        super().__init__('vision_wrapper_service')
        self.srv = self.create_service(ProcesarVision, 'procesar_imagen_vision', self.procesar_callback)
        self.get_logger().info('Servicio de Vision iniciado. Esperando imagenes...')

    def procesar_callback(self, request, response):
        """
        Procesa la petición entrante de la UI o del orquestador.
        """
        ruta_imagen = request.image_path
        script_id = request.script_id

        if not os.path.exists(ruta_imagen):
            response.success = False
            response.error_message = f"Archivo no encontrado: {ruta_imagen}"
            self.get_logger().error(response.error_message)
            return response

        frame = cv2.imread(ruta_imagen)
        if frame is None:
            response.success = False
            response.error_message = f"OpenCV no pudo decodificar la imagen: {ruta_imagen}"
            self.get_logger().error(response.error_message)
            return response

        rutas_extraidas = []
        
        try:
            if script_id == 1:
                rutas_extraidas, _, _, _ = vision_01.procesar_frame(frame)
            elif script_id == 2:
                rutas_extraidas, _, _ = vision_02.procesar_frame(frame)
            elif script_id == 3:
                rutas_extraidas, _ = vision_03.procesar_frame(frame)
            else:
                response.success = False
                response.error_message = f"ID de script desconocido: {script_id}"
                self.get_logger().error(response.error_message)
                return response

            response.trajectories_json = json.dumps(rutas_extraidas)
            response.success = True
            response.error_message = ""
            
            self.get_logger().info(f'Proceso exitoso. Script: {script_id} | Trazos: {len(rutas_extraidas)}')

        except Exception as e:
            response.success = False
            response.error_message = str(e)
            self.get_logger().error(f'Error interno procesando la imagen: {e}')
            
        return response

def main(args=None):
    """
    Inicializa el middleware de ROS 2 y mantiene el nodo en ejecucion.
    """
    rclpy.init(args=args)
    vision_service = VisionWrapperService()
    
    try:
        rclpy.spin(vision_service)
    except KeyboardInterrupt:
        pass
    finally:
        vision_service.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()

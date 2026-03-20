import rclpy
from rclpy.node import Node
import json

from lynx_interfaces.srv import ProcesarCalculo
from lynx_motion_core.calculus import calculus_trayectory

class CalculusWrapperService(Node):
    """
    Nodo servidor de ROS 2 para transformar rutas de píxeles a espacio cartesiano (mm).
    Recibe la configuración del espacio de trabajo dinámicamente desde la UI.
    """
    def __init__(self):
        super().__init__('calculus_wrapper_service')
        self.srv = self.create_service(ProcesarCalculo, 'procesar_calculo_trayectoria', self.procesar_callback)
        self.get_logger().info('Servicio de Calculo de Trayectorias iniciado.')

    def procesar_callback(self, request, response):
        try:
            # 1. Deserializar los datos de entrada
            rutas_pixeles = json.loads(request.rutas_json)
            config_espacio = json.loads(request.config_espacio_json)
            
            w_img = request.w_img
            h_img = request.h_img
            delta_paso = request.delta_paso

            # 2. Llamar a la lógica matemática pura
            matriz, formulas = calculus_trayectory.generar_matriz_trayectoria(
                rutas_pixeles, 
                w_img, 
                h_img, 
                config_espacio, 
                delta_paso
            )

            # 3. Empaquetar y responder
            response.matriz_espacial_json = json.dumps(matriz)
            response.formulas_matematicas_json = json.dumps(formulas)
            response.success = True
            response.error_message = ""
            
            self.get_logger().info(f'Calculo exitoso. Puntos 3D generados: {len(matriz)}')

        except Exception as e:
            response.success = False
            response.error_message = str(e)
            self.get_logger().error(f'Error en el calculo de trayectoria: {e}')
            
        return response

def main(args=None):
    rclpy.init(args=args)
    calculus_service = CalculusWrapperService()
    
    try:
        rclpy.spin(calculus_service)
    except KeyboardInterrupt:
        pass
    finally:
        calculus_service.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()

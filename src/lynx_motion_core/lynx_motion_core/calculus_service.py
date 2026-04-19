"""
Analytical Middleware - SIG-Lynx

This node receives discrete vision vectors and applies linear transformations
to scale the spatial domain to the robot's useful operational area.
It generates continuous parametric functions from discrete data points,
acting as the bridge between pixel coordinates and Cartesian space (mm).

Input: Discrete vectors (Pixels) and dynamic workspace configuration.
Output: 3D spatial matrix (mm) and mathematical parametric formulas.
"""

import rclpy
from rclpy.node import Node
import json

from lynx_interfaces.srv import ProcesarCalculo
from lynx_motion_core.calculus import calculus_trayectory

class CalculusWrapperService(Node):
    def __init__(self):
        super().__init__('calculus_wrapper_service')
        self.srv = self.create_service(ProcesarCalculo, 'procesar_calculo_trayectoria', self.procesar_callback)
        self.get_logger().info('>>> LYNX CALCULUS SERVICE STARTED <<<')

    def procesar_callback(self, request, response):
        try:
            # Data deserialization
            rutas_pixeles = json.loads(request.rutas_json)
            config_espacio = json.loads(request.config_espacio_json)
            
            w_img = request.w_img
            h_img = request.h_img
            delta_paso = request.delta_paso

            # Core math logic execution
            matriz, formulas = calculus_trayectory.generar_matriz_trayectoria(
                rutas_pixeles,  
                w_img,  
                h_img,  
                config_espacio,  
                delta_paso
            )

            # Response packaging
            response.matriz_espacial_json = json.dumps(matriz)
            response.formulas_matematicas_json = json.dumps(formulas)
            response.success = True
            response.error_message = ""
            
            self.get_logger().info(f'Calculation successful. 3D points generated: {len(matriz)}')

        except Exception as e:
            response.success = False
            response.error_message = str(e)
            self.get_logger().error(f'Trajectory calculation error: {e}')
            
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

import rclpy
from rclpy.node import Node
import json
import time
import os

from lynx_interfaces.srv import EjecutarMovimiento
from lynx_motion_core.motion.kinematics import calcular_ik
from lynx_motion_core.motion.ssc32u_controller import ControladorSSC32U

class MotionExecutionService(Node):
    def __init__(self):
        super().__init__('motion_execution_service')
        
        # Inicializar controlador serial
        # Asegúrate de que la ruta al YAML sea correcta desde donde lanzas el nodo
        self.hardware = ControladorSSC32U(archivo_config="src/lynx_motion_core/lynx_motion_core/config_motores.yaml")
        
        # Cargar dimensiones del brazo desde el YAML
        dims = self.hardware.config_completa.get("dimensiones_brazo", {})
        self.L1 = dims.get("altura_base", 115.0)
        self.L2 = dims.get("brazo_superior", 155.0)
        self.L3 = dims.get("antebrazo", 185.0)
        self.L4 = dims.get("efector_final", 115.0)

        self.srv = self.create_service(EjecutarMovimiento, 'ejecutar_movimiento_robot', self.ejecutar_callback)
        self.get_logger().info('Servicio de Movimiento AL5D listo (90=Vertical).')

    def ejecutar_callback(self, request, response):
        self.get_logger().info('Iniciando ejecucion de trayectoria...')
        try:
            puntos_3d = json.loads(request.matriz_espacial_json)
            
            for i, punto in enumerate(puntos_3d):
                # Manejo flexible de formato de datos
                if isinstance(punto, (list, tuple)):
                    x, y, z = float(punto[0]), float(punto[1]), float(punto[2])
                else:
                    x = float(punto.get('x', 0))
                    y = float(punto.get('y', 0))
                    z = float(punto.get('z', 0))

                # Calcular ángulos con la nueva cinemática
                angulos = calcular_ik(x, y, z, self.L1, self.L2, self.L3, self.L4)

                if angulos:
                    dict_angulos = {
                        'joint_base_rotate': angulos[0],
                        'joint_shoulder': angulos[1],
                        'joint_elbow': angulos[2],
                        'joint_wrist': angulos[3]
                    }
                    # Enviar al SSC-32U
                    # tiempo=50ms para suavidad en trayectorias densas
                    self.hardware.mover_multiples_articulaciones(dict_angulos, tiempo=50)
                    time.sleep(0.05)
                
                if i % 500 == 0:
                    self.get_logger().info(f"Procesando punto {i}...")

            response.success = True
            self.get_logger().info('Trayectoria completada.')

        except Exception as e:
            response.success = False
            response.error_message = str(e)
            self.get_logger().error(f'Error en ejecucion: {e}')
            
        return response

def main(args=None):
    rclpy.init(args=args)
    node = MotionExecutionService()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()

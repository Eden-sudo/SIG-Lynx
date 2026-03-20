import rclpy
from rclpy.node import Node
import json
import time
import math
import os

from sensor_msgs.msg import JointState
from lynx_interfaces.srv import EjecutarMovimiento
from lynx_motion_core.motion import kinematics
from lynx_motion_core.motion.ssc32u_controller import ControladorSSC32U

class MotionWrapperService(Node):
    """
    Nodo servidor para ejecutar trayectorias fisicas y en simulacion.
    Lee las dimensiones del YAML para pasarlas a la cinematica inversa.
    """
    def __init__(self):
        super().__init__('motion_wrapper_service')
        
        self.joint_pub = self.create_publisher(JointState, 'joint_states', 10)
        
        # Inicializar el controlador y cargar la configuracion
        ruta_yaml = os.path.join(os.path.dirname(__file__), 'config_motores.yaml')
        self.robot_hardware = ControladorSSC32U(archivo_config=ruta_yaml)
        
        # Extraer dimensiones dinamicas del YAML
        dimensiones = self.robot_hardware.config_completa.get('dimensiones_brazo', {})
        self.L1 = dimensiones.get('L1', 70.0)
        self.L2 = dimensiones.get('L2', 146.0)
        self.L3 = dimensiones.get('L3', 181.0)
        
        self.get_logger().info(f"Dimensiones cargadas: L1={self.L1}, L2={self.L2}, L3={self.L3}")
        
        self.srv = self.create_service(EjecutarMovimiento, 'ejecutar_trayectoria', self.procesar_movimiento)
        self.get_logger().info('Servicio de Movimiento iniciado. Hardware y RViz enlazados.')

    def procesar_movimiento(self, request, response):
        try:
            matriz_espacial = json.loads(request.matriz_espacial_json)
            
            for punto in matriz_espacial:
                x, y, z = punto[0], punto[1], punto[2]
                
                # Pasar las dimensiones leidas del YAML a la funcion pura
                angulos = kinematics.calcular_ik(x, y, z, self.L1, self.L2, self.L3, angulo_lapiz_deseado=-90.0)
                
                if angulos is None:
                    self.get_logger().warning(f"Punto inalcanzable ignorado: ({x}, {y}, {z})")
                    continue
                    
                theta_base, theta_hombro, theta_codo, theta_muneca = angulos
                
                diccionario_angulos = {
                    'joint_base_rotate': theta_base,
                    'joint_shoulder': theta_hombro,
                    'joint_elbow': theta_codo,
                    'joint_wrist': theta_muneca
                }

                self.robot_hardware.mover_multiples_articulaciones(diccionario_angulos, tiempo=100)
                self.publicar_rviz(diccionario_angulos)
                
                # Pausa para dar tiempo al hardware de ejecutar el comando serial
                time.sleep(0.1)

            response.success = True
            response.error_message = ""
            self.get_logger().info('Trayectoria completada fisicamente y en simulacion.')

        except Exception as e:
            response.success = False
            response.error_message = str(e)
            self.get_logger().error(f'Error ejecutando movimiento: {e}')
            
        return response

    def publicar_rviz(self, dicc_angulos):
        msg = JointState()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.name = list(dicc_angulos.keys())
        
        posiciones_rad = []
        for nombre in msg.name:
            grados = dicc_angulos[nombre]
            posiciones_rad.append(math.radians(grados))
            
        msg.position = posiciones_rad
        self.joint_pub.publish(msg)

def main(args=None):
    rclpy.init(args=args)
    motion_service = MotionWrapperService()
    try:
        rclpy.spin(motion_service)
    except KeyboardInterrupt:
        pass
    finally:
        motion_service.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()

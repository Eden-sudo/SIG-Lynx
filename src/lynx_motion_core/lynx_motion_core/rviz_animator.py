import rclpy
from rclpy.node import Node
from sensor_msgs.msg import JointState
from std_msgs.msg import String
import math
import json
import time

from lynx_motion_core.motion.kinematics import calcular_ik

class RVizAnimatorNode(Node):
    def __init__(self):
        super().__init__('rviz_animator_node')
        
        # Publicador estándar que usa robot_state_publisher para mover el modelo
        self.joint_pub = self.create_publisher(JointState, '/joint_states', 10)
        
        # Escucha la orden de simular desde la UI
        self.sub = self.create_subscription(String, '/simular_trayectoria', self.simular_callback, 10)
        
        # Tus medidas exactas
        self.L1, self.L2, self.L3, self.L4 = 115.0, 155.0, 185.0, 115.0
        
        self.get_logger().info('🤖 Simulador RViz En Línea. Esperando coordenadas...')

    def simular_callback(self, msg):
        self.get_logger().info('Recibiendo datos. Renderizando animación 3D...')
        puntos_3d = json.loads(msg.data)
        
        joint_state = JointState()
        joint_state.name = [
            'joint_base_rotate', 
            'joint_shoulder', 
            'joint_elbow', 
            'joint_wrist', 
            'joint_gripper_rotate', 
            'joint_gripper_finger',
            'joint_gripper_left_finger'
        ]
        
        for punto in puntos_3d:
            if isinstance(punto, (list, tuple)):
                x, y, z = float(punto[0]), float(punto[1]), float(punto[2])
            else:
                x, y, z = float(punto.get('x', 0)), float(punto.get('y', 0)), float(punto.get('z', 0))

            angulos = calcular_ik(x, y, z, self.L1, self.L2, self.L3, self.L4)
            
            if angulos:
                # TRADUCCIÓN A RADIANES PARA EL URDF
                # El URDF de la base va de -PI a PI
                base_rad = math.radians(angulos[0])
                
                # El URDF del hombro espera 0 cuando está adelante, PI cuando está atrás
                shoulder_rad = math.radians(angulos[1])
                
                # ¡DETALLE CLAVE! El URDF del codo tiene límite [-PI a 0]. 
                # 0 es recto, negativo es doblado. Nuestra cinemática da 90 cuando está recto.
                elbow_rad = math.radians(angulos[2] - 90.0) 
                
                wrist_rad = math.radians(angulos[3])
                
                joint_state.header.stamp = self.get_clock().now().to_msg()
                joint_state.position = [
                    base_rad, 
                    shoulder_rad, 
                    elbow_rad, 
                    wrist_rad, 
                    0.0, # Rotación de pinza fija
                    0.0, # Pinza cerrada
                    0.0
                ]
                
                self.joint_pub.publish(joint_state)
                # 30ms para que la animación en pantalla se vea fluida
                time.sleep(0.03) 
                
        self.get_logger().info('Animación en RViz completada.')

def main(args=None):
    rclpy.init(args=args)
    node = RVizAnimatorNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()

"""
RViz Digital Twin Animator - SIG-Lynx

Subscribes to trajectory commands and translates calculated Inverse Kinematics
angles into URDF-compliant radians. Publishes JointState messages to drive
the 3D visualization model in RViz smoothly.
"""

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
        
        # Standard publisher using robot_state_publisher to move the model
        self.joint_pub = self.create_publisher(JointState, '/joint_states', 10)
        
        # Listens to simulation commands from UI
        self.sub = self.create_subscription(String, '/simular_trayectoria', self.simular_callback, 10)
        
        # Exact physical measurements
        self.L1, self.L2, self.L3, self.L4 = 115.0, 155.0, 185.0, 115.0
        
        self.get_logger().info('>>> RVIZ SIMULATOR ONLINE | Waiting for coordinates... <<<')

    def simular_callback(self, msg):
        self.get_logger().info('Receiving data. Rendering 3D animation...')
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
                # TRANSLATION TO RADIANS FOR URDF
                # Base URDF range: -PI to PI
                base_rad = math.radians(angulos[0])
                
                # Shoulder URDF expects 0 when forward, PI when backward
                shoulder_rad = math.radians(angulos[1])
                
                # KEY DETAIL: Elbow URDF has limits [-PI to 0].  
                # 0 is straight, negative is bent. IK gives 90 when straight.
                elbow_rad = math.radians(angulos[2] - 90.0)  
                
                wrist_rad = math.radians(angulos[3])
                
                joint_state.header.stamp = self.get_clock().now().to_msg()
                joint_state.position = [
                    base_rad,  
                    shoulder_rad,  
                    elbow_rad,  
                    wrist_rad,  
                    0.0, # Fixed gripper rotation
                    0.0, # Closed gripper
                    0.0
                ]
                
                self.joint_pub.publish(joint_state)
                # 30ms delay for smooth screen animation
                time.sleep(0.03)  
                
        self.get_logger().info('RViz animation completed.')

def main(args=None):
    rclpy.init(args=args)
    node = RVizAnimatorNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()

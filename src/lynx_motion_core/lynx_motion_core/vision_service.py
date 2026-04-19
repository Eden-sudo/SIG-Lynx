"""
Visual Perception Module - SIG-Lynx

This node operates as the input channel from the physical environment.
It handles spatial discretization by capturing the environment through optical sensors.
Applies convolution integrals (spatial filtering) to attenuate stochastic noise,
and uses differential calculus (Gradient Vector / Canny) to isolate target topology.

Input: Video stream / Two-dimensional matrix of light intensity.
Output: Discrete matrix of physical paths in the focal plane (Pixels) requested by the math core.
"""

import rclpy
from rclpy.node import Node
import cv2
import json
import os
import traceback

from lynx_interfaces.srv import ProcesarVision
from lynx_motion_core.vision import vision_01, vision_02, vision_03

class VisionWrapperService(Node):
    def __init__(self):
        super().__init__('vision_wrapper_service')
        self.srv = self.create_service(ProcesarVision, 'procesar_imagen_vision', self.procesar_callback)
        self.get_logger().info('>>> LYNX VISION SERVICE STARTED (UNIVERSAL MODE) <<<')

    def procesar_callback(self, request, response):
        ruta = request.image_path
        sid = request.script_id

        if not os.path.exists(ruta):
            response.success = False
            response.error_message = f"Invalid path: {ruta}"
            return response

        frame = cv2.imread(ruta)
        try:
            # Dynamic script selection
            if sid == 1:   res = vision_01.procesar_frame(frame)
            elif sid == 2: res = vision_02.procesar_frame(frame)
            elif sid == 3: res = vision_03.procesar_frame(frame)
            else: raise ValueError(f"Script ID {sid} not implemented")

            # Safe extraction: ensures compatibility if script returns (paths, img) or just paths
            if isinstance(res, (tuple, list)):
                rutas_extraidas = res[0]
            else:
                rutas_extraidas = res

            response.trajectories_json = json.dumps(rutas_extraidas)
            response.success = True
            self.get_logger().info(f'Script {sid} OK | Extracted paths: {len(rutas_extraidas)}')

        except Exception as e:
            response.success = False
            response.error_message = f"Processing error: {str(e)}"
            self.get_logger().error(f"Critical failure: {traceback.format_exc()}")
            
        return response

def main(args=None):
    rclpy.init(args=args)
    node = VisionWrapperService()
    try: 
        rclpy.spin(node)
    except KeyboardInterrupt: 
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()

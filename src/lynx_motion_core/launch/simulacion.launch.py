"""
RViz2 Simulation Launch File - SIG-Lynx

Loads the URDF/Xacro description of the AL5D arm and launches the 
required nodes (Robot State Publisher and RViz2) to visualize 
the kinematic digital twin in real-time.
"""

import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch_ros.actions import Node
import xacro

def generate_launch_description():
    # 1. Get the description package path
    pkg_descripcion = get_package_share_directory('lynx_al5d_ros2_description')
    archivo_xacro = os.path.join(pkg_descripcion, 'urdf', 'lynx_al5d.urdf.xacro')

    # 2. Process Xacro file into URDF XML
    doc_xacro = xacro.process_file(archivo_xacro)
    robot_description = {'robot_description': doc_xacro.toxml()}

    # 3. Configure Robot State Publisher node
    nodo_rsp = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        name='robot_state_publisher',
        output='screen',
        parameters=[robot_description]
    )

    # 4. Configure RViz2 node
    nodo_rviz = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        output='screen'
    )

    return LaunchDescription([
        nodo_rsp,
        nodo_rviz
    ])

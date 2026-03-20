import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch_ros.actions import Node
import xacro

def generate_launch_description():
    # 1. Obtener la ruta del paquete de descripcion
    pkg_descripcion = get_package_share_directory('lynx_al5d_ros2_description')
    archivo_xacro = os.path.join(pkg_descripcion, 'urdf', 'lynx_al5d.urdf.xacro')

    # 2. Procesar el archivo Xacro a URDF XML
    doc_xacro = xacro.process_file(archivo_xacro)
    robot_description = {'robot_description': doc_xacro.toxml()}

    # 3. Configurar el nodo Robot State Publisher
    # Este nodo toma el URDF y los angulos de /joint_states para calcular la posicion 3D
    nodo_rsp = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        name='robot_state_publisher',
        output='screen',
        parameters=[robot_description]
    )

    # 4. Configurar el nodo RViz2
    # Carga la interfaz visual. Puedes especificar un archivo .rviz guardado si tienes uno
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

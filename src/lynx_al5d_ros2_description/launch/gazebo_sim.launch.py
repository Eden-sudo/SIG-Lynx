"""
Gazebo Simulation Launch File - SIG-Lynx

Spawns the AL5D URDF model into a Gazebo physics simulation environment,
initializing the necessary joint state broadcasters and arm controllers.
"""
import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, RegisterEventHandler
from launch.event_handlers import OnProcessExit
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node
import xacro

def generate_launch_description():
    pkg_share = get_package_share_directory('lynx_al5d_ros2_description')
    
    # Configure model paths to prevent invisible meshes in Gazebo
    os.environ["GAZEBO_MODEL_PATH"] = os.path.join(pkg_share, '..')

    # Process URDF/Xacro
    xacro_file = os.path.join(pkg_share, 'urdf', 'lynx_al5d.urdf.xacro')
    robot_description_config = xacro.process_file(xacro_file).toxml()

    # Robot State Publisher (Publishes TF based on simulation)
    node_robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        output='screen',
        parameters=[{'robot_description': robot_description_config, 'use_sim_time': True}]
    )

    # Launch Gazebo
    # Note: To save hardware resources, 'gui' can be set to False inside gazebo.launch.py
    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([os.path.join(
            get_package_share_directory('gazebo_ros'), 'launch', 'gazebo.launch.py')]),
    )

    # Spawn robot entity in Gazebo
    spawn_entity = Node(
        package='gazebo_ros', 
        executable='spawn_entity.py',
        arguments=['-topic', 'robot_description', '-entity', 'lynx_al5d'],
        output='screen'
    )

    # Initialize Joint State Broadcaster (Reads simulated encoders)
    joint_state_broadcaster_spawner = Node(
        package="controller_manager",
        executable="spawner",
        arguments=["joint_state_broadcaster", "--controller-manager", "/controller_manager"],
    )

    # Initialize Arm Controller (Receives position commands)
    arm_controller_spawner = Node(
        package="controller_manager",
        executable="spawner",
        arguments=["arm_controller", "--controller-manager", "/controller_manager"],
    )

    # Delay controller loading until robot entity is completely spawned
    # Prevents "Controller manager not found" initialization errors
    return LaunchDescription([
        gazebo,
        node_robot_state_publisher,
        spawn_entity,
        RegisterEventHandler(
            event_handler=OnProcessExit(
                target_action=spawn_entity,
                on_exit=[joint_state_broadcaster_spawner],
            )
        ),
        RegisterEventHandler(
            event_handler=OnProcessExit(
                target_action=joint_state_broadcaster_spawner,
                on_exit=[arm_controller_spawner],
            )
        ),
    ])

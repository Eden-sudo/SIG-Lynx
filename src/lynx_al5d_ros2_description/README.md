# lynx_al5d_ros2_description

## Overview
This package contains the Digital Twin definitions, physical properties, and URDF/Xacro models for the Lynxmotion AL5D robotic arm. It serves as the visual and physical foundation for the SIG-Lynx project, providing the necessary assets for both kinematic visualization and dynamic simulation.

## Key Components
* **urdf/**: Contains the `lynx_al5d.urdf.xacro` file, detailing the joint limits, links, and visual/collision geometries.
* **meshes/**: 3D CAD models used by the URDF for accurate rendering.
* **launch/**: Launch scripts to initialize the robot state publisher and simulation environments.
* **rviz/**: Default configuration files for RViz2 node layout.

## Usage

### Visual Kinematic Testing (RViz2)
To load the URDF and open the Joint State Publisher GUI to manually test joint limits:

    ros2 launch lynx_al5d_ros2_description display.launch.py

### Physics Simulation (Gazebo)
To spawn the robotic arm in a simulated Gazebo environment with active controller managers:

    ros2 launch lynx_al5d_ros2_description gazebo_sim.launch.py

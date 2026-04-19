# SIG-Lynx: Geometric Inspection and Autonomous Trajectory System

[Versión en Español](README.es.md)

## Project Overview
SIG-Lynx is an interdisciplinary robotic platform developed to bridge the gap between computer vision, differential calculus, and physical actuation. The system captures physical environments via optical sensors, discretizes the visual data into spatial vectors, and translates them into pure mathematical parametric models.

Utilizing the Lynxmotion AL5D robotic arm within a ROS 2 ecosystem, SIG-Lynx instantiates these models into high-precision physical trajectories. This project demonstrates advanced integration of real-time image processing, inverse kinematics, and distributed system architecture on Arch Linux.

## Core Features
* **Visual Perception Architecture**: Multi-algorithm extraction system (including B-Splines, Low-Poly approximation, and Line-Art filters) using OpenCV.
* **Mathematical Middleware**: Automatic generation of parametric functions $X(t)$ and $Y(t)$ for path interpolation and spatial scaling.
* **Kinematic Engine**: Real-time Inverse Kinematics (IK) solver with singularity protection and hardware-level calibration.
* **Dual Interface**: Local management via a CustomTkinter MVVM GUI and remote monitoring through a FastAPI web server.
* **Simulation & Digital Twin**: Full integration with RViz2 and Gazebo for pre-execution validation and physical simulation.

## System Architecture

The project follows a modular pipeline distributed across specialized ROS 2 packages:

1.  **Perception**: Captured frames are processed to isolate object topology.
2.  **Analysis**: Discrete pixel vectors are scaled and converted into continuous parametric equations.
3.  **Control**: The math core calculates articular angles and transmits PWM commands to the SSC-32U controller.

## Repository Structure

* **src/lynx_motion_core**: The main logic hub (Vision, Calculus, and Motion nodes).
* **src/lynx_al5d_ros2_description**: Robot description (URDF/Xacro), meshes, and simulation launch files.
* **lynx_ui**: Python-based local GUI for system calibration and operation.
* **lynx_server**: Web backend providing remote access to the vision and calculus engines.
* **lynx_interfaces**: Custom ROS 2 service and message definitions.

## Installation & Build

### Prerequisites
* ROS 2 (Humble/Iron/Rolling)
* Python 3.10+
* OpenCV, NumPy, SciPy, PyYAML, Serial, FastAPI

### Building the Workspace
Navigate to the root of the project and execute:

    colcon build
    source install/setup.bash

## Usage

### 1. Launching the Control Panel
The main UI coordinates all background nodes:

    cd lynx_ui
    python ui_main.py

### 2. Simulation Environment
To visualize the Digital Twin in RViz2:

    ros2 launch lynx_al5d_ros2_description display.launch.py

### 3. Remote Web Access
To start the FastAPI web dashboard:

    cd lynx_server
    python launch_server.py

## Technical Documentation
For detailed information regarding the mathematical derivation of the Inverse Kinematics and the convolution integrals used in the vision pipeline, please refer to the internal report located in the project documentation folder.

## Authors
* **Carlos Duarte** - Lead Developer
* **Project Team**: Bryan Mendez, Carla Moran, Vladimir Campos.
* **Institution**: Universidad Latina de Panama.

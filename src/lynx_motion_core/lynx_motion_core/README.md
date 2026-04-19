# lynx_motion_core

## Overview
The core processing and control package for the SIG-Lynx architecture. This package bridges the gap between raw optical data and physical electromechanical actuation. It handles computer vision, mathematical trajectory interpolation, inverse kinematics, and direct serial communication.

## Core Nodes and Services

* **Vision Service (vision_service.py)**: 
  Acts as the perception module. Receives images, applies spatial filtering, and discretizes object topologies into pixel-based spatial vectors using OpenCV. Supports multiple extraction algorithms (Line Art, B-Spline, Low-Poly).

* **Calculus Service (calculus_service.py)**: 
  The analytical middleware. Translates discrete pixel vectors into continuous parametric equations and maps them into 3D Cartesian space (mm) based on dynamic workspace constraints.

* **Motion Service (motion_service.py)**: 
  The hardware controller. Receives 3D spatial matrices, computes Inverse Kinematics (Law of Cosines) while protecting boundary singularities, and translates the data into PWM signals for the SSC-32U board.

* **RViz Animator (rviz_animator.py)**: 
  Subscribes to trajectory commands and translates kinematic angles into URDF-compliant radians to drive the digital twin simulation in real-time.

## Configuration
The physical measurements and mechanical offsets for the AL5D arm are isolated in the `config_motores.yaml` file. This allows dynamic calibration of joint limits and initial PWM offsets without recompiling the ROS 2 nodes.

## Building the Package
To compile the Python nodes and install the service interfaces, navigate to your ROS 2 workspace root and run:

    colcon build --packages-select lynx_motion_core
    source install/setup.bash

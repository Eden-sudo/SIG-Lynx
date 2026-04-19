# lynx_ui

## Overview
This package contains the Graphical User Interface (GUI) for the SIG-Lynx system. It is built using CustomTkinter and follows the MVVM (Model-View-ViewModel) architectural pattern to ensure a strict separation between the user interface, the application logic, and the ROS 2 communication layer.

## Architecture: MVVM Pattern
The package is organized to decouple hardware and middleware management from the visual representation:

* **View Layer (views/ & ui_main.py)**: Handles the rendering of frames, buttons, and visual monitors. It remains agnostic of ROS 2 implementation details.
* **ViewModel / Manager Layer (ros_client_manager.py)**: Acts as the bridge. It translates UI events into ROS 2 service calls and manages asynchronous threading to prevent GUI freezing during long-running tasks.
* **Model Layer (config_manager.py & process_manager.py)**: Manages the data state (YAML configuration) and the lifecycle of external system processes.

## Script Descriptions

### ui_main.py
The main entry point of the application. It initializes the CustomTkinter window, instantiates the managers, and handles top-level navigation between the Configuration, Process, and Operation views.

### ros_client_manager.py
The ROS 2 interface logic. It encapsulates the RosClientNode, managing asynchronous service requests for vision, calculus, and motion. It also handles the dynamic spawning of ROS 2 nodes via shell commands.

### process_manager.py
A specialized utility for lifecycle management. It tracks PIDs and handles the clean termination of background processes (such as the web server or simulation nodes) using signal groups.

### config_manager.py
The data persistence layer. It provides an interface for reading and writing hardware-specific parameters to the `config_motores.yaml` file, ensuring consistency between the UI and the motion core.

### test_motion.py
A standalone diagnostic utility. It allows for direct serial communication testing with the SSC-32U controller without requiring the full ROS 2 stack, useful for hardware-level debugging and calibration.

## Execution
To launch the control panel, ensure your ROS 2 environment is sourced and run:

    python ui_main.py

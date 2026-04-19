# SIG-Lynx: Sistema de Inspección Geométrica y Trayectorias Autónomas

[English version](README.md)

## Resumen del Proyecto
SIG-Lynx es una plataforma robótica interdisciplinaria desarrollada para cerrar la brecha entre la visión artificial, el cálculo diferencial y la actuación física. El sistema captura entornos físicos mediante sensores ópticos, discretiza los datos visuales en vectores espaciales y los traduce en modelos matemáticos paramétricos puros.

Utilizando el brazo robótico Lynxmotion AL5D dentro del ecosistema ROS 2, SIG-Lynx instancia estos modelos en trayectorias físicas de alta precisión. Este proyecto demuestra una integración avanzada de procesamiento de imágenes en tiempo real, cinemática inversa y arquitectura de sistemas distribuidos sobre Arch Linux.

## Características Principales
* **Arquitectura de Percepción Visual**: Sistema de extracción multi-algoritmo (incluyendo Splines de tipo B, aproximación Low-Poly y filtros Line-Art) utilizando OpenCV.
* **Middleware Matemático**: Generación automática de funciones paramétricas $X(t)$ y $Y(t)$ para la interpolación de rutas y escalado espacial.
* **Motor Cinemático**: Solucionador de Cinemática Inversa (IK) en tiempo real con protección contra singularidades y calibración a nivel de hardware.
* **Interfaz Dual**: Gestión local mediante una GUI CustomTkinter basada en el patrón MVVM y monitoreo remoto a través de un servidor web FastAPI.
* **Simulación y Gemelo Digital**: Integración total con RViz2 y Gazebo para la validación previa a la ejecución y simulación física.

## Arquitectura del Sistema

El proyecto sigue un pipeline modular distribuido en paquetes especializados de ROS 2:

1.  **Percepción**: Los frames capturados se procesan para aislar la topología del objeto.
2.  **Análisis**: Los vectores de píxeles discretos se escalan y convierten en ecuaciones paramétricas continuas.
3.  **Control**: El núcleo matemático calcula los ángulos articulares y transmite comandos PWM al controlador SSC-32U.

## Estructura del Repositorio

* **src/lynx_motion_core**: El núcleo lógico principal (Nodos de Visión, Cálculo y Movimiento).
* **src/lynx_al5d_ros2_description**: Descripción del robot (URDF/Xacro), mallas (meshes) y archivos de lanzamiento para simulación.
* **lynx_ui**: Interfaz gráfica local en Python para la calibración y operación del sistema.
* **lynx_server**: Backend web que proporciona acceso remoto a los motores de visión y cálculo.
* **lynx_interfaces**: Definiciones personalizadas de servicios (srv) y mensajes (msg) de ROS 2.

## Instalación y Construcción

### Prerrequisitos
* ROS 2 (Humble/Iron/Rolling)
* Python 3.10+
* OpenCV, NumPy, SciPy, PyYAML, Serial, FastAPI

### Construcción del Workspace
Navega a la raíz del proyecto y ejecuta:

    colcon build
    source install/setup.bash

## Uso

### 1. Lanzamiento del Panel de Control
La UI principal coordina todos los nodos de fondo:

    cd lynx_ui
    python ui_main.py

### 2. Entorno de Simulación
Para visualizar el Gemelo Digital en RViz2:

    ros2 launch lynx_al5d_ros2_description display.launch.py

### 3. Acceso Web Remoto
Para iniciar el dashboard web de FastAPI:

    cd lynx_server
    python launch_server.py

## Documentación Técnica
Para información detallada sobre la derivación matemática de la Cinemática Inversa y las integrales de convolución utilizadas en el pipeline de visión, por favor consulte el informe interno ubicado en la carpeta de documentación del proyecto.

## Autores
* **Carlos Duarte** - Desarrollador Principal
* **Equipo del Proyecto**: Bryan Mendez, Carla Moran, Vladimir Campos.
* **Institución**: Universidad Latina de Panamá.

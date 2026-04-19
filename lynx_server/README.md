# lynx_server

## Overview
This package provides a lightweight web interface and REST API for the SIG-Lynx system. Built with FastAPI, it allows remote users to upload images, trigger the computer vision pipeline, and visualize the resulting mathematical parametric formulas in LaTeX format.

## Architecture
The server acts as a non-ROS bridge, utilizing a dedicated ROS 2 node (`WebRosBridge`) running in a background thread to communicate with the `vision_service` and `calculus_service` nodes.

## Key Components
* **launch_server.py**: Entry point. Configures CORS, static file hosting, and initializes the Uvicorn server.
* **endpoints.py**: Defines the API routes. Handles file uploads, coordinates asynchronous ROS 2 service calls, and translates results into web-friendly formats (JSON/LaTeX).
* **web/**: Contains the frontend assets (HTML/CSS/JS) for the user interface.
* **uploads/**: Volatile storage for input images and processed vector maps.

## API Endpoints
* `GET /`: Serves the main web dashboard.
* `POST /procesar`: Receives an image file and returns coordinates, LaTeX equations, and a processed visual map.

## Execution
To launch the web interface, ensure the ROS 2 services are running and execute:

    python launch_server.py

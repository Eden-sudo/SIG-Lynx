import os
import shutil
import json
import cv2
import numpy as np
import asyncio
import threading
import rclpy
from rclpy.node import Node
from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import FileResponse

from lynx_interfaces.srv import ProcesarVision, ProcesarCalculo

router = APIRouter()
UPLOAD_FOLDER = "uploads"

# --- BRIDGE ROS 2 ---
class WebRosBridge(Node):
    def __init__(self):
        super().__init__('web_ros_bridge')
        self.cli_vision = self.create_client(ProcesarVision, 'procesar_imagen_vision')
        self.cli_calculo = self.create_client(ProcesarCalculo, 'procesar_calculo_trayectoria')

# Inicializar ROS 2 con Executor en hilo separado
try:
    if not rclpy.ok(): rclpy.init()
    ros_bridge = WebRosBridge()
    executor = rclpy.executors.SingleThreadedExecutor()
    executor.add_node(ros_bridge)
    threading.Thread(target=executor.spin, daemon=True).start()
    print("✅ [ROS 2] Bridge & Spinner ONLINE")
except Exception as e:
    print(f"❌ [ROS 2] Error: {e}")

@router.get("/")
async def leer_interfaz():
    return FileResponse(os.path.join("web", "index.html"))

@router.post("/procesar")
async def recibir_y_procesar(file: UploadFile = File(...)):
    # ID único para evitar caché y colisiones
    request_id = str(os.getpid()) + "_" + str(int(asyncio.get_event_loop().time()))
    
    # RUTA ABSOLUTA (Ajusta si mueves el proyecto)
    base_path = "/home/Eden/Desktop/lynx_calculus_project/lynx_server"
    ruta_input = os.path.abspath(os.path.join(base_path, UPLOAD_FOLDER, f"in_{request_id}.jpg"))
    ruta_output = os.path.abspath(os.path.join(base_path, UPLOAD_FOLDER, f"out_{request_id}.jpg"))
    
    print(f"\n[VERBOSE] 📥 Petición: {file.filename}")
    
    with open(ruta_input, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    try:
        # 1. VISIÓN
        if not ros_bridge.cli_vision.wait_for_service(timeout_sec=2.0):
            return {"status": "error", "detalle": "Servicio de Visión offline"}

        req_v = ProcesarVision.Request()
        req_v.image_path = ruta_input
        req_v.script_id = 1
        
        future_v = ros_bridge.cli_vision.call_async(req_v)
        while not future_v.done(): await asyncio.sleep(0.05)
        
        resp_v = future_v.result()
        if not resp_v.success:
            return {"status": "error", "detalle": "Fallo en extracción visual (Sin trazos)"}

        # 2. DIBUJO OPENCV (Filtro Neón)
        rutas = json.loads(resp_v.trajectories_json)
        canvas = np.ones((480, 640, 3), dtype=np.uint8) * 15
        for r in rutas:
            if len(r) > 1:
                pts = np.array(r, np.int32).reshape((-1,1,2))
                cv2.polylines(canvas, [pts], False, (0, 230, 255), 2, cv2.LINE_AA)
        cv2.imwrite(ruta_output, canvas)

        # 3. CÁLCULO
        if not ros_bridge.cli_calculo.wait_for_service(timeout_sec=2.0):
            return {"status": "error", "detalle": "Servicio de Cálculo offline"}

        req_c = ProcesarCalculo.Request()
        req_c.rutas_json = resp_v.trajectories_json
        req_c.config_espacio_json = json.dumps({'X_MIN': -100, 'X_MAX': 100, 'Y_MIN': 160, 'Y_MAX': 300, 'Z_DIBUJO': 0, 'Z_TRANSITO': 15})
        req_c.w_img, req_c.h_img, req_c.delta_paso = 640, 480, 5.0

        future_c = ros_bridge.cli_calculo.call_async(req_c)
        while not future_c.done(): await asyncio.sleep(0.05)
        
        resp_c = future_c.result()

        # 4. LATEX (Traducción limpia)
        formulas = json.loads(resp_c.formulas_matematicas_json)
        ecuaciones_latex = []
        for f in formulas:
            f_clean = f.replace("para 0 <= t <= 1", "\\quad t \\in [0, 1]")
            f_clean = f_clean.replace("[", "\\begin{cases} ").replace("]", " \\end{cases}").replace(",", " \\\\ ")
            ecuaciones_latex.append(f_clean)

        print(f"[VERBOSE] ✨ Proceso Completado para {len(rutas)} trazos.")
        return {
            "status": "success",
            "archivo": f"out_{request_id}.jpg",
            "ecuaciones": ecuaciones_latex,
            "conteo": len(rutas)
        }

    except Exception as e:
        print(f"[VERBOSE] ❌ Error: {e}")
        return {"status": "error", "detalle": str(e)}

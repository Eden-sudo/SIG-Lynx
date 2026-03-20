import cv2
import numpy as np
import time
from scipy.interpolate import splprep, splev

def nothing(x): pass

# ==========================================
# BLOQUE 1: FUNCIONES MATEMÁTICAS Y DE VISIÓN
# ==========================================
def suavizar_contorno_spline(contour, suavidad=0.0):
    """
    Convierte un contorno rugoso en una curva B-Spline suave.
    Retorna directamente una lista de tuplas (x, y) estandarizada.
    """
    pts = [tuple(p[0]) for p in contour]
    unique_pts = [pts[0]]
    for p in pts[1:]:
        if p != unique_pts[-1]:
            unique_pts.append(p)
            
    if len(unique_pts) < 4:
        return [(int(p[0]), int(p[1])) for p in unique_pts]

    x = [p[0] for p in unique_pts]
    y = [p[1] for p in unique_pts]

    try:
        tck, u = splprep([x, y], s=suavidad, per=True)  
        u_new = np.linspace(u.min(), u.max(), len(unique_pts) * 5)
        x_new, y_new = splev(u_new, tck, der=0)

        return [(int(x_new[i]), int(y_new[i])) for i in range(len(x_new))]
        
    except Exception as e:
        return [(int(p[0]), int(p[1])) for p in unique_pts]

def extraer_vectores_organicos(imagen_binaria, suavidad, min_len):
    """
    Motor de extracción para el look orgánico.
    """
    contornos, _ = cv2.findContours(imagen_binaria, cv2.RETR_LIST, cv2.CHAIN_APPROX_NONE)
    
    rutas_extraidas = []
    for cnt in contornos:
        if cv2.arcLength(cnt, False) > min_len:
            ruta_suave = suavizar_contorno_spline(cnt, suavidad)
            rutas_extraidas.append(ruta_suave)
            
    return rutas_extraidas

# ==========================================
# BLOQUE 2: LÓGICA PURA (Para Servidores / ROS 2)
# ==========================================
def procesar_frame(frame, config=None):
    """
    Aplica la lógica visual B-Spline a un frame de OpenCV.
    Retorna datos puros sin abrir ventanas.
    """
    if config is None:
        config = {
            'bloque': 11, 'c': 2, 'suavidad': 50, 'basura': 15
        }

    val_bloque = config['bloque']
    val_c = config['c']
    val_suavidad = config['suavidad']
    val_basura = config['basura']

    if val_bloque % 2 == 0: val_bloque += 1  
    if val_bloque < 3: val_bloque = 3

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    gray = cv2.medianBlur(gray, 5)  
    
    edges = cv2.adaptiveThreshold(
        gray, 255,  
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,  
        cv2.THRESH_BINARY,  
        val_bloque,  
        val_c
    )
    
    edges_inv = cv2.bitwise_not(edges)
    kernel = np.ones((2,2), np.uint8)
    edges_cleaned = cv2.morphologyEx(edges_inv, cv2.MORPH_OPEN, kernel)

    rutas_finales = extraer_vectores_organicos(edges_cleaned, val_suavidad, val_basura)

    return rutas_finales, edges_cleaned

# ==========================================
# BLOQUE 3: CÁMARA Y UI (Modo Standalone Original)
# ==========================================
def obtener_trazos_organicos(usar_ui=True, cam_index=0):
    """
    Función envoltorio para pruebas manuales (cámara + ventanas).
    """
    win_name = 'Vision_Organica'
    win_robot = 'Robot_Splines_Suaves'

    if usar_ui:
        cv2.namedWindow(win_name)
        cv2.namedWindow(win_robot)
        cv2.createTrackbar('Tamano_Bloque', win_name, 11, 50, nothing)  
        cv2.createTrackbar('Umbral_C', win_name, 2, 20, nothing)
        cv2.createTrackbar('Suavidad_Spline', win_name, 5, 50, nothing)  
        cv2.createTrackbar('Filtro_Basura', win_name, 15, 100, nothing)

    cap = cv2.VideoCapture(cam_index)

    if not usar_ui:
        for _ in range(10):
            cap.read()
            time.sleep(0.05)

    rutas_finales = []
    imagen_final = None

    while True:
        ret, frame = cap.read()
        if not ret: break
        
        h, w = frame.shape[:2]

        config = None
        if usar_ui:
            config = {
                'bloque': cv2.getTrackbarPos('Tamano_Bloque', win_name),
                'c': cv2.getTrackbarPos('Umbral_C', win_name),
                'suavidad': cv2.getTrackbarPos('Suavidad_Spline', win_name) * 10,
                'basura': cv2.getTrackbarPos('Filtro_Basura', win_name)
            }

        rutas_finales, imagen_final = procesar_frame(frame, config)

        if not usar_ui:
            break
        else:
            cv2.imshow(win_name, imagen_final)
            
            key = cv2.waitKey(1)
            if key & 0xFF == ord('q'):  
                rutas_finales = []
                break
            elif key & 0xFF == ord('t'):
                lienzo_vector = np.zeros((h, w, 3), dtype=np.uint8)
                for ruta in rutas_finales:
                    pts_np = np.array(ruta, dtype=np.int32).reshape((-1, 1, 2))
                    cv2.polylines(lienzo_vector, [pts_np], False, (0, 255, 0), 1)
                
                cv2.putText(lienzo_vector, f"Curvas Spline: {len(rutas_finales)}", (10, h-20),  
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
                cv2.imshow(win_robot, lienzo_vector)
                print("¡Vectorización orgánica completada! Presiona 'q' para salir y retornar datos.")

    cap.release()
    if usar_ui:
        cv2.destroyAllWindows()
        
    return rutas_finales, imagen_final

# ==========================================
# PRUEBA DE UNIDAD LOCAL
# ==========================================
if __name__ == "__main__":
    print("Iniciando módulo de visión (Splines Orgánicos)...")
    coordenadas, matriz_img = obtener_trazos_organicos(usar_ui=True)  
    
    if coordenadas:
        print(f"\n¡Listo! Extraídas {len(coordenadas)} curvas suavizadas con Scipy.")
    else:
        print("\nCancelado.")

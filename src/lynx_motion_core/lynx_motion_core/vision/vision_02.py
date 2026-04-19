import cv2
import numpy as np
import time
from scipy.interpolate import splprep, splev

def nothing(x): pass

# --- Math & Vision Functions ---

def suavizar_contorno_spline(contour, suavidad=0.0):
    """Converts a rough contour into a smooth B-Spline curve."""
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
        # per=False prevents Scipy from forcing a closed curve, avoiding warnings
        tck, u = splprep([x, y], s=suavidad, per=False)   
        u_new = np.linspace(u.min(), u.max(), len(unique_pts) * 5)
        x_new, y_new = splev(u_new, tck, der=0)

        return [(int(x_new[i]), int(y_new[i])) for i in range(len(x_new))]
        
    except Exception:
        return [(int(p[0]), int(p[1])) for p in unique_pts]

def extraer_vectores_organicos(imagen_binaria, suavidad, min_len):
    """Extraction engine for organic contour smoothing."""
    contornos, _ = cv2.findContours(imagen_binaria, cv2.RETR_LIST, cv2.CHAIN_APPROX_NONE)
    
    rutas_extraidas = []
    for cnt in contornos:
        if cv2.arcLength(cnt, False) > min_len:
            ruta_suave = suavizar_contorno_spline(cnt, suavidad)
            rutas_extraidas.append(ruta_suave)
            
    return rutas_extraidas

# --- Core Logic ---

def procesar_frame(frame, config=None):
    """
    Applies B-Spline visual logic.
    Returns: rutas_finales, edges_cleaned
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

# --- Camera & Standalone UI ---

def obtener_trazos_organicos(usar_ui=True, cam_index=0):
    """Standalone test for organic splines extraction."""
    cap = cv2.VideoCapture(cam_index)
    while True:
        ret, frame = cap.read()
        if not ret: break
        
        frame = cv2.flip(frame, 1)
        rutas, img_debug = procesar_frame(frame)
        
        if usar_ui:
            cv2.imshow('Script 2: Organic Splines', img_debug)
            if cv2.waitKey(1) & 0xFF == ord('q'): break
        else: 
            break
            
    cap.release()
    cv2.destroyAllWindows()
    return rutas, img_debug

if __name__ == "__main__":
    print("Starting Vision Module 02 (Splines)...")
    obtener_trazos_organicos(usar_ui=True)

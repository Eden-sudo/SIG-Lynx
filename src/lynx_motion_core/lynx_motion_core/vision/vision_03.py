import cv2
import numpy as np
import time

def nothing(x): pass

# --- Math Functions (Low-Poly) ---

def aproximar_poligono(contour, factor_rigidez):
    """
    Converts a contour into a straight-line polygon.
    Higher rigidity results in fewer points and straighter lines.
    """
    epsilon = (factor_rigidez / 1000.0) * cv2.arcLength(contour, False)
    approx = cv2.approxPolyDP(contour, epsilon, False)
    
    puntos_rectos = []
    for p in approx:
        puntos_rectos.append((int(p[0][0]), int(p[0][1])))
        
    return puntos_rectos

def extraer_vectores_geometricos(imagen_binaria, rigidez, min_len):
    """Extraction engine for geometric/industrial vectors."""
    contornos, _ = cv2.findContours(imagen_binaria, cv2.RETR_LIST, cv2.CHAIN_APPROX_NONE)
    
    rutas_extraidas = []
    for cnt in contornos:
        if cv2.arcLength(cnt, False) > min_len:
            ruta_recta = aproximar_poligono(cnt, rigidez)
            
            if len(ruta_recta) >= 2:
                rutas_extraidas.append(ruta_recta)
                
    return rutas_extraidas

# --- Core Logic ---

def procesar_frame(frame, config=None):
    """
    Applies Geometric (Low-Poly) visual logic.
    Returns: rutas_finales, edges_cleaned
    """
    if config is None:
        config = {
            'bloque': 11, 'c': 2, 'rigidez': 15, 'basura': 15
        }

    val_bloque = config['bloque']
    val_c = config['c']
    val_rigidez = config['rigidez']
    val_basura = config['basura']

    if val_bloque % 2 == 0: val_bloque += 1
    if val_bloque < 3: val_bloque = 3

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    
    edges = cv2.adaptiveThreshold(
        gray, 255,   
        cv2.ADAPTIVE_THRESH_MEAN_C,   
        cv2.THRESH_BINARY,   
        val_bloque,   
        val_c
    )
    
    edges_inv = cv2.bitwise_not(edges)
    kernel = np.ones((2,2), np.uint8)
    edges_cleaned = cv2.morphologyEx(edges_inv, cv2.MORPH_OPEN, kernel)

    rutas_finales = extraer_vectores_geometricos(edges_cleaned, val_rigidez, val_basura)

    return rutas_finales, edges_cleaned

# --- Camera & Standalone UI ---

def obtener_trazos_geometricos(usar_ui=True, cam_index=0):
    """Standalone manual testing for geometric extraction."""
    win_name = 'Vision_Geometrica_LowPoly'
    win_robot = 'Robot_Trazos_Rectos'

    if usar_ui:
        cv2.namedWindow(win_name)
        cv2.namedWindow(win_robot)
        cv2.createTrackbar('Tamano_Bloque', win_name, 11, 50, nothing)   
        cv2.createTrackbar('Umbral_C', win_name, 2, 20, nothing)
        cv2.createTrackbar('Rigidez_Lineas', win_name, 15, 100, nothing) 
        cv2.createTrackbar('Filtro_Basura', win_name, 15, 100, nothing)

    cap = cv2.VideoCapture(cam_index)

    if not usar_ui:
        for _ in range(10): cap.read(); time.sleep(0.05)

    rutas_finales = []
    imagen_final = None

    while True:
        ret, frame = cap.read()
        if not ret: break
        
        h, w = frame.shape[:2]
        frame = cv2.flip(frame, 1)

        config = None
        if usar_ui:
            config = {
                'bloque': cv2.getTrackbarPos('Tamano_Bloque', win_name),
                'c': cv2.getTrackbarPos('Umbral_C', win_name),
                'rigidez': cv2.getTrackbarPos('Rigidez_Lineas', win_name),
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
                    cv2.polylines(lienzo_vector, [pts_np], False, (0, 165, 255), 1)
                
                cv2.putText(lienzo_vector, f"Lineas Geometricas: {len(rutas_finales)}", (10, h-20),   
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
                cv2.imshow(win_robot, lienzo_vector)
                print("Vectorization complete! Press 'q' to exit.")

    cap.release()
    if usar_ui: cv2.destroyAllWindows()
    return rutas_finales, imagen_final

if __name__ == "__main__":
    print("Starting Vision Module (Script 3 - Low Poly)...")
    coordenadas, matriz_img = obtener_trazos_geometricos(usar_ui=True)  
    if coordenadas: print(f"\nDone! Extracted {len(coordenadas)} routes.")
    else: print("\nCancelled.")

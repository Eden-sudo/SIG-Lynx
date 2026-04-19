import cv2
import numpy as np
import time

def nothing(x): pass

# --- Support Functions ---

def generar_trama(w, h, esp, inv=False):
    """Generates a shading pattern."""
    patron = np.ones((h, w), dtype=np.uint8) * 255
    if esp < 2: esp = 2
    for i in range(-h, w + h, esp):
        p1, p2 = (i, 0), (i + h, h) if not inv else (i - h, h)
        cv2.line(patron, p1, p2, 0, 1)
    return patron

def limpiar_manchas(mask, min_size):
    """Removes noise and small artifacts from the mask."""
    if min_size == 0: return mask
    cnts, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    mask_limpia = np.zeros_like(mask)
    for c in cnts:
        if cv2.contourArea(c) > min_size * 5:   
            cv2.drawContours(mask_limpia, [c], -1, 255, -1)
    return mask_limpia

def calcular_vectores(imagen_binaria):
    """Extracts X, Y coordinates from the processed binary image."""
    img_inv = cv2.bitwise_not(imagen_binaria)
    kernel = np.ones((2,2), np.uint8)
    img_inv = cv2.dilate(img_inv, kernel, iterations=1)
    
    contornos, _ = cv2.findContours(img_inv, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    
    rutas = []
    for cnt in contornos:
        if cv2.arcLength(cnt, False) > 20:
            ruta_actual = []
            for punto in cnt:
                x, y = punto[0]
                ruta_actual.append((int(x), int(y)))
            rutas.append(ruta_actual)
            
    return rutas

# --- Core Logic ---

def procesar_frame(frame, config=None):
    """
    Applies visual logic to an OpenCV frame.
    Returns: routes (paths), robot_canvas (binary image)
    """
    if config is None:
        config = {
            'grosor': 7, 'sens': 4, 'limpieza': 2,  
            'radio': 0, 'sombra': 49, 'trama': 8, 'suavizado': 7
        }

    val_grosor = config['grosor'] | 1
    val_suavizado = config['suavizado'] | 1
    val_sens = config['sens']
    val_limpieza = config['limpieza']
    val_radio = config['radio']
    val_sombra = config['sombra']
    val_trama = config['trama']

    h, w = frame.shape[:2]

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    gray = cv2.bilateralFilter(gray, val_suavizado, 75, 75)
    
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
    balanced = clahe.apply(gray)
    
    rasgos_raw = cv2.adaptiveThreshold(balanced, 255, cv2.ADAPTIVE_THRESH_MEAN_C,   
                                        cv2.THRESH_BINARY, val_grosor, val_sens)
    rasgos_inv = cv2.bitwise_not(rasgos_raw)
    rasgos_limpios = limpiar_manchas(rasgos_inv, val_limpieza)

    kernel_prot = np.ones((val_radio*2+1, val_radio*2+1), np.uint8) if val_radio > 0 else np.ones((1,1), np.uint8)
    mascara_proteccion = cv2.dilate(rasgos_limpios, kernel_prot, iterations=1)

    blur_shadow = cv2.GaussianBlur(balanced, (31, 31), 0)
    _, mask_zona_sombra = cv2.threshold(blur_shadow, val_sombra, 255, cv2.THRESH_BINARY_INV)
    if val_limpieza > 0:
        mask_zona_sombra = limpiar_manchas(mask_zona_sombra, val_limpieza * 2)

    trama = generar_trama(w, h, val_trama, False)
    sombra_bruta = cv2.bitwise_or(trama, cv2.bitwise_not(mask_zona_sombra))

    canvas_robot = np.ones((h, w), dtype=np.uint8) * 255
    canvas_robot = cv2.min(canvas_robot, sombra_bruta)
    canvas_robot = cv2.max(canvas_robot, mascara_proteccion)
    canvas_robot = cv2.min(canvas_robot, cv2.bitwise_not(rasgos_limpios))

    rutas_finales = calcular_vectores(canvas_robot)

    return rutas_finales, canvas_robot

# --- Camera & UI ---

def obtener_trazos(usar_ui=True, cam_index=0):
    """Standalone manual testing."""
    cap = cv2.VideoCapture(cam_index)
    while True:
        ret, frame = cap.read()
        if not ret: break
        
        frame = cv2.flip(frame, 1)
        rutas, img_debug = procesar_frame(frame)
        
        if usar_ui:
            cv2.imshow('Script 1: High Detail', img_debug)
            if cv2.waitKey(1) & 0xFF == ord('q'): break
        else:
            break
            
    cap.release()
    cv2.destroyAllWindows()
    return rutas, img_debug

if __name__ == "__main__":
    print("Starting Script 1...")
    obtener_trazos(usar_ui=True)

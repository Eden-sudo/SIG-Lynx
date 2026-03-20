import cv2
import numpy as np
import time

def nothing(x): pass

# ==========================================
# BLOQUE 1: FUNCIONES DE APOYO
# ==========================================
def generar_trama(w, h, esp, inv=False):
    """Genera el patrón de sombreado"""
    patron = np.ones((h, w), dtype=np.uint8) * 255
    if esp < 2: esp = 2
    for i in range(-h, w + h, esp):
        p1, p2 = (i, 0), (i + h, h) if not inv else (i - h, h)
        cv2.line(patron, p1, p2, 0, 1)
    return patron

def limpiar_manchas(mask, min_size):
    """Elimina ruido y pequeños artefactos de la máscara"""
    if min_size == 0: return mask
    cnts, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    mask_limpia = np.zeros_like(mask)
    for c in cnts:
        if cv2.contourArea(c) > min_size * 5:  
            cv2.drawContours(mask_limpia, [c], -1, 255, -1)
    return mask_limpia

def calcular_vectores(imagen_binaria):
    """Extrae las coordenadas X, Y de la imagen procesada"""
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

# ==========================================
# BLOQUE 2: LÓGICA PURA
# ==========================================
def procesar_frame(frame, config=None):
    """
    Recibe un frame de OpenCV y aplica la lógica visual.
    Retorna datos puros sin abrir ventanas.
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

    return rutas_finales, canvas_robot, balanced, mascara_proteccion

# ==========================================
# BLOQUE 3: CÁMARA Y UI
# ==========================================
def obtener_trazos(usar_ui=True, cam_index=0):
    """
    Función envoltorio para pruebas manuales (cámara + ventanas).
    """
    win_name = 'AL5D_Panel_Control_Unico'
    
    if usar_ui:
        cv2.namedWindow(win_name)
        cv2.createTrackbar('Detalle_Grosor', win_name, 7, 21, nothing)  
        cv2.createTrackbar('Detalle_Sens', win_name, 4, 20, nothing)
        cv2.createTrackbar('LIMPIEZA_TOTAL', win_name, 2, 20, nothing)
        cv2.createTrackbar('RADIO_PROTECCION', win_name, 0, 15, nothing)
        cv2.createTrackbar('Sombra_Umbral', win_name, 49, 255, nothing)
        cv2.createTrackbar('Espacio_Trama', win_name, 8, 20, nothing)
        cv2.createTrackbar('Suavizado', win_name, 7, 20, nothing)

    cap = cv2.VideoCapture(cam_index)
    
    if not usar_ui:
        for _ in range(10):
            cap.read()
            time.sleep(0.05)

    rutas_finales = []
    imagen_final = None

    while True:
        ret, frame = cap.read()
        if not ret: 
            print("Error: No se pudo leer la cámara.")
            break
            
        frame = cv2.flip(frame, 1)
        
        config = None
        if usar_ui:
            config = {
                'grosor': cv2.getTrackbarPos('Detalle_Grosor', win_name),
                'sens': cv2.getTrackbarPos('Detalle_Sens', win_name),
                'limpieza': cv2.getTrackbarPos('LIMPIEZA_TOTAL', win_name),
                'radio': cv2.getTrackbarPos('RADIO_PROTECCION', win_name),
                'sombra': cv2.getTrackbarPos('Sombra_Umbral', win_name),
                'trama': cv2.getTrackbarPos('Espacio_Trama', win_name),
                'suavizado': cv2.getTrackbarPos('Suavizado', win_name)
            }

        rutas_finales, imagen_final, balanced, mascara_proteccion = procesar_frame(frame, config)

        if not usar_ui:
            break
        else:
            preview = cv2.cvtColor(balanced, cv2.COLOR_GRAY2BGR)
            robot_bgr = cv2.cvtColor(imagen_final, cv2.COLOR_GRAY2BGR)
            
            proteccion_vis = cv2.cvtColor(mascara_proteccion, cv2.COLOR_GRAY2BGR)
            proteccion_vis[:, :, 1] = 0  
            proteccion_vis[:, :, 2] = 0
            preview = cv2.addWeighted(preview, 1.0, proteccion_vis, 0.3, 0)
            
            info_valores = [
                f"1. Detalle: {config['grosor']}/{config['sens']}",
                f"2. Limpieza: {config['limpieza']}",
                f"3. Proteccion: {config['radio']}",
                f"4. Sombra: {config['sombra']}",
                f"5. Trama: {config['trama']}",
                "'T' -> Calcular y Retornar | 'Q' -> Salir sin nada"
            ]
            
            cv2.rectangle(preview, (0,0), (320, 180), (0,0,0), -1)
            for i, txt in enumerate(info_valores):
                cv2.putText(preview, txt, (10, 25 + i*25), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0,255,255), 1)

            combined = np.hstack((preview, robot_bgr))
            cv2.imshow(win_name, combined)
            
            key = cv2.waitKey(1)
            if key & 0xFF == ord('q'):  
                rutas_finales = []
                break
            elif key & 0xFF == ord('t'):
                break 

    cap.release()
    if usar_ui:
        cv2.destroyAllWindows()
        
    return rutas_finales, imagen_final

# ==========================================
# PRUEBA LOCAL
# ==========================================
if __name__ == "__main__":
    print("Iniciando módulo de visión...")
    coordenadas_generadas, matriz_imagen = obtener_trazos(usar_ui=True)  
    
    if coordenadas_generadas:
        print(f"\n¡Éxito! Se obtuvieron {len(coordenadas_generadas)} líneas/trazos.")
        print(f"La imagen no se guardó, pero está en memoria con resolución: {matriz_imagen.shape}")
        print(f"Ejemplo de los 3 primeros puntos del primer trazo: {coordenadas_generadas[0][:3]}")
    else:
        print("\nOperación cancelada por el usuario o fallo de cámara.")

import cv2
import numpy as np
import time

# ==========================================
# BLOQUE 1: MOTOR LEGACY (El "Script Zero")
# ==========================================
class SketchExtractorLegacy:
    def __init__(self, config=None):
        self.cfg = config if config else {}
        self.blur_radius = 7     
        self.line_thickness = 5  
        self.sensitivity = 85    
        
    def extract_features(self, image):
        """
        Convierte la imagen en 'Line Art'.
        Retorna la matriz estandarizada para el calculador de trayectoria.
        """
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        inv_gray = 255 - gray
        blur = cv2.GaussianBlur(inv_gray, (21, 21), 0)
        
        # Color Dodge manual
        def dodge(image, mask):
            return cv2.divide(image, 255 - mask, scale=256)
        
        sketch = dodge(gray, blur)
        
        # Binarización
        _, bin_sketch = cv2.threshold(sketch, 240, 255, cv2.THRESH_BINARY)
        edges = 255 - bin_sketch
        
        # Adelgazamiento
        kernel = np.ones((2,2), np.uint8)
        edges = cv2.erode(edges, kernel, iterations=1)
        
        # Extracción
        contours, _ = cv2.findContours(edges, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
        
        rutas_estandarizadas = []
        visual_debug = cv2.cvtColor(bin_sketch, cv2.COLOR_GRAY2BGR) 
        
        for cnt in contours:
            if cv2.contourArea(cnt) < 20: continue
            
            # ¡Aquí ya usabas la simplificación RDP que es vital para el robot!
            epsilon = 0.002 * cv2.arcLength(cnt, True)
            approx = cv2.approxPolyDP(cnt, epsilon, True)
            
            if len(approx) > 2:
                # --- ADAPTACIÓN AL ESTÁNDAR DEL PROYECTO ---
                # Convertimos el array de numpy a la lista de tuplas (x, y)
                ruta_actual = []
                for pt in approx.reshape(-1, 2):
                    ruta_actual.append((int(pt[0]), int(pt[1])))
                
                rutas_estandarizadas.append(ruta_actual)
                
                for pt in approx:
                    cv2.circle(visual_debug, tuple(pt[0]), 2, (0, 0, 255), -1)

        return rutas_estandarizadas, visual_debug

# ==========================================
# BLOQUE 2: MÓDULO EXPORTABLE (Caja Negra)
# ==========================================
def obtener_trazos_legacy_alpha(usar_ui=True, cam_index=0):
    """
    Función principal de la versión Alpha.
    Retorna: (lista_de_coordenadas, imagen_generada_en_memoria)
    """
    extractor = SketchExtractorLegacy()
    cap = cv2.VideoCapture(cam_index)

    # WARMUP DE CÁMARA
    if not usar_ui:
        for _ in range(10):
            cap.read()
            time.sleep(0.05)

    rutas_finales = []
    imagen_final = None
    win_name = "Estilo Line Art (Legacy Alpha)"

    while True:
        ret, frame = cap.read()
        if not ret: break
        
        frame = cv2.flip(frame, 1)
        
        # Procesamos la imagen con la clase antigua
        paths, view = extractor.extract_features(frame)
        imagen_final = view.copy()

        if not usar_ui:
            rutas_finales = paths
            break
        else:
            # Como este script no tenía trackbars, solo mostramos la info en pantalla
            cv2.putText(view, f"Trazos Alpha: {len(paths)}", (10, 30), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)
            cv2.putText(view, "'T' -> Capturar y Vectorizar | 'Q' -> Salir", (10, 60), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1)
            
            cv2.imshow(win_name, view)
            
            key = cv2.waitKey(1)
            if key & 0xFF == ord('q'):
                break
            elif key & 0xFF == ord('t'):
                rutas_finales = paths
                break

    cap.release()
    if usar_ui:
        cv2.destroyAllWindows()
        
    return rutas_finales, imagen_final

# ==========================================
# PRUEBA DE UNIDAD LOCAL
# ==========================================
if __name__ == "__main__":
    print("Iniciando módulo de visión (Legacy Alpha Sketch)...")
    coordenadas, _ = obtener_trazos_legacy_alpha(usar_ui=True) 
    
    if coordenadas:
        print(f"\n¡Éxito! Se obtuvieron {len(coordenadas)} líneas estilo dibujo manual.")
        print(f"Muestra del primer trazo: {coordenadas[0][:3]}")
    else:
        print("\nOperación cancelada.")

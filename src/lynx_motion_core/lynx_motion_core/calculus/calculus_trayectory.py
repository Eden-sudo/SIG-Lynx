import numpy as np

# ==========================================
# LÓGICA MATEMÁTICA Y CINEMÁTICA ESPACIAL
# ==========================================

def transformar_coordenadas(x_px, y_px, w_img, h_img, config_espacio):
    """
    Transformación lineal (mapeo) de espacio de píxeles a espacio cartesiano (mm).
    """
    x_cart = config_espacio['X_MIN'] + (x_px / w_img) * (config_espacio['X_MAX'] - config_espacio['X_MIN'])
    # Se invierte Y porque el origen (0,0) en visión está arriba, y en cartesiano estándar está abajo
    y_cart = config_espacio['Y_MAX'] - (y_px / h_img) * (config_espacio['Y_MAX'] - config_espacio['Y_MIN'])
    
    return round(x_cart, 3), round(y_cart, 3)

def generar_formula_segmento(p1, p2):
    """
    Genera la representación matemática paramétrica del segmento lineal.
    Retorna un string con el formato matemático para la UI.
    """
    dx = round(p2[0] - p1[0], 3)
    dy = round(p2[1] - p1[1], 3)
    
    # Formateo de signos para que no quede " + -5t"
    signo_x = "+" if dx >= 0 else "-"
    signo_y = "+" if dy >= 0 else "-"
    
    formula_x = f"X(t) = {p1[0]} {signo_x} {abs(dx)}t"
    formula_y = f"Y(t) = {p1[1]} {signo_y} {abs(dy)}t"
    
    return f"[{formula_x}, {formula_y}] para 0 <= t <= 1"

def interpolar_segmento(p1, p2, delta_paso):
    """
    Aplica la fórmula paramétrica para generar puntos discretos entre P1 y P2.
    """
    puntos_segmento = []
    distancia = np.sqrt((p2[0] - p1[0])**2 + (p2[1] - p1[1])**2)
    
    if distancia <= delta_paso:
        return [p2]
    
    num_pasos = int(distancia / delta_paso)
    for paso in range(1, num_pasos + 1):
        t = paso / num_pasos
        inter_x = p1[0] + t * (p2[0] - p1[0])
        inter_y = p1[1] + t * (p2[1] - p1[1])
        puntos_segmento.append((round(inter_x, 3), round(inter_y, 3)))
        
    return puntos_segmento

def generar_matriz_trayectoria(rutas_pixeles, w_img, h_img, config_espacio, delta_paso=1.0):
    """
    Función principal. 
    Recibe rutas, dimensiones y los límites físicos dinámicos.
    Retorna la matriz de trayectoria 3D y la lista de fórmulas matemáticas.
    """
    matriz_espacial = []
    lista_formulas = []

    for id_ruta, ruta in enumerate(rutas_pixeles):
        if not ruta or len(ruta) < 2:
            continue
            
        # 1. Punto de entrada (Elevado)
        x_ini, y_ini = transformar_coordenadas(ruta[0][0], ruta[0][1], w_img, h_img, config_espacio)
        matriz_espacial.append((x_ini, y_ini, config_espacio['Z_TRANSITO']))
        
        # 2. Punto de contacto
        matriz_espacial.append((x_ini, y_ini, config_espacio['Z_DIBUJO']))
        
        # 3. Cálculo de la curva y fórmulas
        for i in range(len(ruta) - 1):
            p1 = transformar_coordenadas(ruta[i][0], ruta[i][1], w_img, h_img, config_espacio)
            p2 = transformar_coordenadas(ruta[i+1][0], ruta[i+1][1], w_img, h_img, config_espacio)
            
            # Guardamos la representación matemática
            formula = generar_formula_segmento(p1, p2)
            lista_formulas.append(f"Trazo {id_ruta+1}, Seg {i+1}: {formula}")
            
            # Generamos los puntos físicos
            puntos_interpolados = interpolar_segmento(p1, p2, delta_paso)
            for p_int in puntos_interpolados:
                matriz_espacial.append((p_int[0], p_int[1], config_espacio['Z_DIBUJO']))
                
        # 4. Punto de salida (Elevado)
        x_fin, y_fin = matriz_espacial[-1][0], matriz_espacial[-1][1]
        matriz_espacial.append((x_fin, y_fin, config_espacio['Z_TRANSITO']))

    return matriz_espacial, lista_formulas

# ==========================================
# PRUEBA DE UNIDAD LOCAL
# ==========================================
if __name__ == "__main__":
    rutas_test = [[(10, 10), (100, 10), (100, 100)]]
    ancho, alto = 640, 480
    
    # Configuración inyectada de prueba (simulando lo que enviaría la UI)
    espacio_test = {
        'X_MIN': -100.0, 'X_MAX': 100.0,
        'Y_MIN': 50.0, 'Y_MAX': 250.0,
        'Z_DIBUJO': 0.0, 'Z_TRANSITO': 20.0
    }
    
    matriz, formulas = generar_matriz_trayectoria(rutas_test, ancho, alto, espacio_test, delta_paso=50.0)
    
    print("--- FÓRMULAS MATEMÁTICAS ---")
    for f in formulas:
        print(f)
        
    print("\n--- MATRIZ ESPACIAL (X, Y, Z) ---")
    for coordenada in matriz:
        print(coordenada)

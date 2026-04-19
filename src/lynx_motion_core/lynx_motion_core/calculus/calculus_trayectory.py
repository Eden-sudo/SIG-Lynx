import numpy as np

# --- Math & Spatial Kinematics Logic ---

def transformar_coordenadas(x_px, y_px, w_img, h_img, config_espacio):
    """Linear transformation mapping from pixel space to Cartesian space (mm)."""
    x_cart = config_espacio['X_MIN'] + (x_px / w_img) * (config_espacio['X_MAX'] - config_espacio['X_MIN'])
    
    # Invert Y: vision origin (0,0) is top-left, standard Cartesian is bottom-left
    y_cart = config_espacio['Y_MAX'] - (y_px / h_img) * (config_espacio['Y_MAX'] - config_espacio['Y_MIN'])
    
    return round(x_cart, 3), round(y_cart, 3)

def generar_formula_segmento(p1, p2):
    """
    Generates the mathematical parametric representation of a linear segment.
    Returns a formatted string for UI display.
    """
    dx = round(p2[0] - p1[0], 3)
    dy = round(p2[1] - p1[1], 3)
    
    # Format signs to avoid "+ -5t" structures
    signo_x = "+" if dx >= 0 else "-"
    signo_y = "+" if dy >= 0 else "-"
    
    formula_x = f"X(t) = {p1[0]} {signo_x} {abs(dx)}t"
    formula_y = f"Y(t) = {p1[1]} {signo_y} {abs(dy)}t"
    
    return f"[{formula_x}, {formula_y}] for 0 <= t <= 1"

def interpolar_segmento(p1, p2, delta_paso):
    """Applies parametric formula to generate discrete points between P1 and P2."""
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
    Core function. Takes pixel paths, dimensions, and dynamic physical limits.
    Returns the 3D trajectory matrix and a list of mathematical formulas.
    """
    matriz_espacial = []
    lista_formulas = []

    for id_ruta, ruta in enumerate(rutas_pixeles):
        if not ruta or len(ruta) < 2:
            continue
            
        # 1. Entry point (Elevated Z_TRANSITO)
        x_ini, y_ini = transformar_coordenadas(ruta[0][0], ruta[0][1], w_img, h_img, config_espacio)
        matriz_espacial.append((x_ini, y_ini, config_espacio['Z_TRANSITO']))
        
        # 2. Contact point (Drawing Z_DIBUJO)
        matriz_espacial.append((x_ini, y_ini, config_espacio['Z_DIBUJO']))
        
        # 3. Curve calculation & formulas
        for i in range(len(ruta) - 1):
            p1 = transformar_coordenadas(ruta[i][0], ruta[i][1], w_img, h_img, config_espacio)
            p2 = transformar_coordenadas(ruta[i+1][0], ruta[i+1][1], w_img, h_img, config_espacio)
            
            formula = generar_formula_segmento(p1, p2)
            lista_formulas.append(f"Path {id_ruta+1}, Seg {i+1}: {formula}")
            
            puntos_interpolados = interpolar_segmento(p1, p2, delta_paso)
            for p_int in puntos_interpolados:
                matriz_espacial.append((p_int[0], p_int[1], config_espacio['Z_DIBUJO']))
                
        # 4. Exit point (Elevated Z_TRANSITO)
        x_fin, y_fin = matriz_espacial[-1][0], matriz_espacial[-1][1]
        matriz_espacial.append((x_fin, y_fin, config_espacio['Z_TRANSITO']))

    return matriz_espacial, lista_formulas

# --- Local Unit Test ---
if __name__ == "__main__":
    rutas_test = [[(10, 10), (100, 10), (100, 100)]]
    ancho, alto = 640, 480
    
    # Mock injected config
    espacio_test = {
        'X_MIN': -100.0, 'X_MAX': 100.0,
        'Y_MIN': 50.0, 'Y_MAX': 250.0,
        'Z_DIBUJO': 0.0, 'Z_TRANSITO': 20.0
    }
    
    matriz, formulas = generar_matriz_trayectoria(rutas_test, ancho, alto, espacio_test, delta_paso=50.0)
    
    print("--- MATH FORMULAS ---")
    for f in formulas:
        print(f)
        
    print("\n--- SPATIAL MATRIX (X, Y, Z) ---")
    for coordenada in matriz:
        print(coordenada)

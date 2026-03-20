import math

# ==========================================
# LÓGICA MATEMÁTICA Y CINEMÁTICA ESPACIAL
# ==========================================

def calcular_ik(x, y, z, L1, L2, L3, angulo_lapiz_deseado=-90.0):
    """
    Calcula la Cinemática Inversa (Inverse Kinematics) para el AL5D.
    
    Argumentos:
        x, y, z (float): Coordenadas objetivo en milímetros.
        L1, L2, L3 (float): Dimensiones físicas del brazo extraídas de la configuración.
        angulo_lapiz_deseado (float): Ángulo absoluto del efector final respecto a la horizontal.
        
    Retorna:
        tuple: (theta_base, theta_hombro, theta_codo, theta_muneca) en GRADOS.
        Retorna None si el punto está fuera del alcance físico.
    """
    # 1. Ángulo de la Base
    theta_base_rad = math.atan2(y, x)
    theta_base = math.degrees(theta_base_rad)
    
    # 2. Geometría plana del brazo (r y z_eff)
    r = math.sqrt(x**2 + y**2) 
    z_eff = z - L1             
    
    # 3. Distancia hipotenusa (D)
    D = math.sqrt(r**2 + z_eff**2)
    
    # --- BLOQUEO DE SEGURIDAD ---
    if D > (L2 + L3):
        print(f"[IK Error] Coordenada inalcanzable: ({x}, {y}, {z}). D={round(D,1)}mm > Brazo={L2+L3}mm")
        return None
        
    # 4. Ángulo del Codo (Ley de Cosenos)
    cos_codo = (L2**2 + L3**2 - D**2) / (2 * L2 * L3)
    cos_codo = max(-1.0, min(1.0, cos_codo))
    theta_codo = math.degrees(math.acos(cos_codo))
    
    # 5. Ángulo del Hombro
    alpha = math.atan2(z_eff, r)
    cos_beta = (L2**2 + D**2 - L3**2) / (2 * L2 * D)
    cos_beta = max(-1.0, min(1.0, cos_beta))
    beta = math.acos(cos_beta)
    theta_hombro = math.degrees(alpha + beta)

    # 6. Compensación de Orientación de la Muñeca (Pitch)
    theta_muneca = angulo_lapiz_deseado - (theta_hombro - theta_codo)
    
    return round(theta_base, 2), round(theta_hombro, 2), round(theta_codo, 2), round(theta_muneca, 2)

# ==========================================
# PRUEBA DE UNIDAD LOCAL
# ==========================================
if __name__ == "__main__":
    print("--- Test 1: Punto en (X=0, Y=200mm, Z=0mm) ---")
    # Pasamos las constantes manualmente solo para la prueba local
    angulos = calcular_ik(0.0, 200.0, 0.0, L1=70.0, L2=146.0, L3=181.0)
    
    if angulos:
        print(f"Resultados (Grados) -> Base: {angulos[0]}°, Hombro: {angulos[1]}°, Codo: {angulos[2]}°, Muñeca: {angulos[3]}°\n")
    
    print("--- Test 2: Punto inalcanzable (X=0, Y=500mm, Z=0mm) ---")
    angulos_fallo = calcular_ik(0.0, 500.0, 0.0, L1=70.0, L2=146.0, L3=181.0)

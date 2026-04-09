import math

def calcular_ik(x, y, z, L_base, L_superior, L_antebrazo, L_efector, pitch_objetivo=-90.0):
    """
    Cinemática Inversa para AL5D.
    Convención: 90° = Vertical, 0° = Horizontal Adelante.
    """
    # 1. Ángulo de la Base
    theta_base = math.degrees(math.atan2(y, x))
    
    # 2. Posición de la Muñeca (Joint de inclinación)
    # Calculamos dónde debe estar el eje de la muñeca para que la punta toque (x, y, z)
    r_punta = math.sqrt(x**2 + y**2)
    phi_rad = math.radians(pitch_objetivo)
    
    # Si el pitch es -90 (vertical abajo), la muñeca está exactamente arriba de la punta
    r_muneca = r_punta - (L_efector * math.cos(phi_rad))
    z_muneca = z - (L_efector * math.sin(phi_rad))
    
    # 3. Geometría del brazo (Plano R-Z)
    z_eff = z_muneca - L_base
    D = math.sqrt(r_muneca**2 + z_eff**2)
    
    # Verificación de alcance físico
    if D > (L_superior + L_antebrazo) or D < abs(L_superior - L_antebrazo):
        return None
        
    # 4. Ángulo del Codo (Ley de Cosenos)
    # Buscamos el ángulo interno gamma
    cos_gamma = (L_superior**2 + L_antebrazo**2 - D**2) / (2 * L_superior * L_antebrazo)
    cos_gamma = max(-1.0, min(1.0, cos_gamma))
    gamma = math.degrees(math.acos(cos_gamma))
    
    # Ajuste a tu sistema: Si el brazo está recto, gamma=180, queremos que devuelva 90
    theta_codo = gamma - 90.0

    # 5. Ángulo del Hombro
    alpha = math.atan2(z_eff, r_muneca)
    cos_beta = (L_superior**2 + D**2 - L_antebrazo**2) / (2 * L_superior * D)
    cos_beta = max(-1.0, min(1.0, cos_beta))
    beta = math.acos(cos_beta)
    
    # Hombro en grados (0=adelante, 90=arriba)
    theta_hombro = math.degrees(alpha + beta)

    # 6. Ángulo de la Muñeca (Compensación de Pitch)
    # Para mantener la punta a -90° respecto al suelo:
    theta_muneca = 90.0 - theta_hombro - theta_codo
    
    return (round(theta_base, 2), 
            round(theta_hombro, 2), 
            round(theta_codo, 2), 
            round(theta_muneca, 2))

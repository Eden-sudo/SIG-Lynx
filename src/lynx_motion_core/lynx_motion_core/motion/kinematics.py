import math

def calcular_ik(x, y, z, L_base, L_superior, L_antebrazo, L_efector, pitch_objetivo=-90.0):
    """
    Inverse Kinematics solver.
    Convention: 90° = Vertical Up, 0° = Horizontal Forward.
    """
    # 1. Base Rotation
    theta_base = math.degrees(math.atan2(y, x))

    # 2. Wrist Position (Pitch Joint)
    r_punta = math.sqrt(x**2 + y**2)
    phi_rad = math.radians(pitch_objetivo)

    r_muneca = r_punta - (L_efector * math.cos(phi_rad))
    z_muneca = z - (L_efector * math.sin(phi_rad))

    # 3. Arm Geometry (R-Z Plane)
    z_eff = z_muneca - L_base
    D = math.sqrt(r_muneca**2 + z_eff**2)

    # Physical reach constraint validation
    if D > (L_superior + L_antebrazo) or D < abs(L_superior - L_antebrazo):
        return None

    # 4. Elbow Angle (Law of Cosines)
    cos_gamma = (L_superior**2 + L_antebrazo**2 - D**2) / (2 * L_superior * L_antebrazo)
    cos_gamma = max(-1.0, min(1.0, cos_gamma))
    gamma = math.degrees(math.acos(cos_gamma))

    # Structural offset adjustment
    theta_codo = gamma - 90.0

    # 5. Shoulder Angle
    alpha = math.atan2(z_eff, r_muneca)
    cos_beta = (L_superior**2 + D**2 - L_antebrazo**2) / (2 * L_superior * D)
    cos_beta = max(-1.0, min(1.0, cos_beta))
    beta = math.acos(cos_beta)

    theta_hombro = math.degrees(alpha + beta)

    # 6. Wrist Angle (Pitch Compensation)
    theta_muneca = 90.0 - theta_hombro - theta_codo

    return (round(theta_base, 2),
            round(theta_hombro, 2),
            round(theta_codo, 2),
            round(theta_muneca, 2))

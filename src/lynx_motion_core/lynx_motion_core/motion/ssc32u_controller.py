import yaml
import serial

class ControladorSSC32U:
    def __init__(self, archivo_config="config_motores.yaml", puerto="/dev/ttyUSB0"):
        try:
            with open(archivo_config, 'r') as f:
                self.config_completa = yaml.safe_load(f)
                self.motores = self.config_completa.get("articulaciones", {})
        except Exception as e:
            print(f"Error cargando config: {e}")
            self.motores = {}
            self.config_completa = {}

        try:
            self.serial = serial.Serial(puerto, 9600, timeout=1)
        except serial.SerialException:
            print(f"ADVERTENCIA: Puerto {puerto} no disponible. Modo simulación.")
            self.serial = None

    def grados_a_pwm(self, grados):
        # 90 grados = 1500 PWM
        pwm = 500 + (grados / 180.0) * 2000
        return int(max(500, min(2500, pwm)))

    def mover_multiples_articulaciones(self, diccionario_angulos, tiempo=1000):
        comando_completo = ""
        
        # INYECCIÓN DE SEGURIDAD: 
        # Mantenemos la pinza y la rotación firmes aunque la cinemática no los calcule
        angulos_seguros = diccionario_angulos.copy()
        if 'joint_gripper_rotate' not in angulos_seguros:
            angulos_seguros['joint_gripper_rotate'] = 90.0 # Posición central
        if 'joint_gripper_finger' not in angulos_seguros:
            angulos_seguros['joint_gripper_finger'] = 90.0 # Pinza cerrada/neutral

        for nombre, grados in angulos_seguros.items():
            if nombre not in self.motores: continue

            # Restricción física de la pinza
            if nombre == 'joint_gripper_finger':
                grados = max(68.0, min(180.0, grados))

            datos = self.motores[nombre]
            
            # Aplicamos los offsets milimétricos que descubriste en tu test
            grados_finales = grados + datos["offset_grados"]

            pulso = self.grados_a_pwm(grados_finales)
            comando_completo += f"#{datos['canal']} P{pulso} "

        if comando_completo:
            comando_completo += f"T{tiempo}\r"
            if self.serial:
                self.serial.write(comando_completo.encode('ascii'))
            else:
                print(f"[HW_SIM] {comando_completo.strip()}")

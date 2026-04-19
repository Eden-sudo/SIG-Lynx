import yaml
import serial

class ControladorSSC32U:
    def __init__(self, archivo_config="config_motores.yaml", puerto="/dev/ttyUSB0"):
        try:
            with open(archivo_config, 'r') as f:
                self.config_completa = yaml.safe_load(f)
                self.motores = self.config_completa.get("articulaciones", {})
        except Exception as e:
            print(f"Error loading config: {e}")
            self.motores = {}
            self.config_completa = {}

        try:
            self.serial = serial.Serial(puerto, 9600, timeout=1)
        except serial.SerialException:
            print(f"WARNING: Port {puerto} unavailable. Running in Simulation Mode.")
            self.serial = None

    def grados_a_pwm(self, grados):
        """Converts degrees to PWM signal (1500 = 90 deg center)."""
        pwm = 500 + (grados / 180.0) * 2000
        return int(max(500, min(2500, pwm)))

    def mover_multiples_articulaciones(self, diccionario_angulos, tiempo=1000):
        """Builds and transmits the serial command string for the controller."""
        comando_completo = ""
        
        # Safety Injection: Maintain firm grip and rotation if not computed by IK
        angulos_seguros = diccionario_angulos.copy()
        if 'joint_gripper_rotate' not in angulos_seguros:
            angulos_seguros['joint_gripper_rotate'] = 90.0 
        if 'joint_gripper_finger' not in angulos_seguros:
            angulos_seguros['joint_gripper_finger'] = 90.0 

        for nombre, grados in angulos_seguros.items():
            if nombre not in self.motores: continue

            # Physical limit constraint for gripper
            if nombre == 'joint_gripper_finger':
                grados = max(68.0, min(180.0, grados))

            datos = self.motores[nombre]
            
            # Apply mechanical offsets 
            grados_finales = grados + datos["offset_grados"]

            pulso = self.grados_a_pwm(grados_finales)
            comando_completo += f"#{datos['canal']} P{pulso} "

        if comando_completo:
            comando_completo += f"T{tiempo}\r"
            if self.serial:
                self.serial.write(comando_completo.encode('ascii'))
            else:
                print(f"[HW_SIM] {comando_completo.strip()}")

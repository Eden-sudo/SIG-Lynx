import yaml
import serial

class ControladorSSC32U:
    def __init__(self, archivo_config="config_motores.yaml", puerto="/dev/ttyUSB0"):
        # 1. Cargar la configuración YAML
        try:
            with open(archivo_config, 'r') as f:
                self.config_completa = yaml.safe_load(f)
                self.motores = self.config_completa.get("articulaciones", {})
        except Exception as e:
            print(f"Error cargando {archivo_config}: {e}")
            self.motores = {}
            self.config_completa = {}
            
        # 2. Iniciar conexión serial (con fallback para simulacion)
        try:
            self.serial = serial.Serial(puerto, 9600, timeout=1)
        except serial.SerialException:
            print(f"ADVERTENCIA: No se pudo abrir {puerto}. Ejecutando en modo simulacion.")
            self.serial = None
        
    def grados_a_pwm(self, grados):
        # Mapeo lineal: 0°=500, 90°=1500, 180°=2500
        pwm = 500 + (grados / 180.0) * 2000
        return int(max(500, min(2500, pwm))) 

    def mover_articulacion(self, nombre_articulacion, grados, tiempo=1000):
        """
        Mueve un solo motor. Útil para pruebas manuales o controlar la pinza de forma independiente.
        """
        if nombre_articulacion not in self.motores:
            print(f"Error: {nombre_articulacion} no existe en config_motores.yaml")
            return
            
        datos = self.motores[nombre_articulacion]
        canal = datos["canal"]
        
        grados_finales = grados + datos["offset_grados"]
        if datos["invertido"]:
            grados_finales = 180 - grados_finales
            
        pulso = self.grados_a_pwm(grados_finales)
        comando = f"#{canal} P{pulso} T{tiempo}\r"
        
        if self.serial:
            self.serial.write(comando.encode('ascii'))
        else:
            print(f"[SIMULACION SERIAL] Enviando: {comando.strip()}")

    def mover_multiples_articulaciones(self, diccionario_angulos, tiempo=1000):
        """
        Recibe un diccionario y mueve todos los motores al mismo tiempo enviando un solo string serial.
        """
        comando_completo = ""
        
        for nombre_articulacion, grados in diccionario_angulos.items():
            if nombre_articulacion not in self.motores:
                continue
                
            datos = self.motores[nombre_articulacion]
            canal = datos["canal"]
            
            grados_finales = grados + datos["offset_grados"]
            if datos["invertido"]:
                grados_finales = 180 - grados_finales
                
            pulso = self.grados_a_pwm(grados_finales)
            comando_completo += f"#{canal} P{pulso} "
            
        if comando_completo:
            comando_completo += f"T{tiempo}\r"
            if self.serial:
                self.serial.write(comando_completo.encode('ascii'))
            else:
                print(f"[SIMULACION SERIAL] Enviando Múltiple: {comando_completo.strip()}")

# ==========================================
# PRUEBA DE UNIDAD LOCAL
# ==========================================
if __name__ == "__main__":
    robot = ControladorSSC32U(archivo_config="config_motores.yaml", puerto="/dev/ttyUSB0")
    
    print("--- Test de movimiento múltiple ---")
    angulos_test = {
        'joint_base_rotate': 90.0,
        'joint_shoulder': 45.0,
        'joint_elbow': 90.0,
        'joint_wrist': 180.0
    }
    robot.mover_multiples_articulaciones(angulos_test, tiempo=500)

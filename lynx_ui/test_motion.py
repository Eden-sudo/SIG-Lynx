import yaml
import serial
import time

class ControladorSSC32U:
    def __init__(self, archivo_config="config_motores.yaml", puerto="/dev/ttyUSB0", baudrate=9600):
        print("="*60)
        print("[SSC32U-CORE] [BOOT] INICIALIZANDO CONTROLADOR DE HARDWARE")
        print("="*60)
        print(f"[SSC32U-CORE] [IO] TRATANDO DE CARGAR YAML: {archivo_config}")
        
        try:
            with open(archivo_config, 'r') as f:
                self.config_completa = yaml.safe_load(f)
                self.motores = self.config_completa.get("articulaciones", {})
            print(f"[SSC32U-CORE] [IO-SUCCESS] YAML CARGADO. {len(self.motores)} MOTORES ENCONTRADOS.")
        except Exception as e:
            print(f"[SSC32U-CORE] [FATAL-IO] ERROR CARGANDO {archivo_config}: {e}")
            self.motores = {}
            self.config_completa = {}
            
        print(f"[SSC32U-CORE] [SERIAL] INTENTANDO ABRIR PUERTO -> DISPOSITIVO: {puerto} | BAUDRATE: {baudrate}")
        try:
            self.serial = serial.Serial(puerto, baudrate, timeout=1)
            # Pequeña pausa porque algunos chips USB-Serial se reinician al abrir la conexión
            time.sleep(1.5) 
            print(f"[SSC32U-CORE] [SERIAL-SUCCESS] PUERTO ABIERTO Y ESTABILIZADO: {self.serial.name}")
        except serial.SerialException as e:
            print(f"[SSC32U-CORE] [SERIAL-ERROR] NO SE PUDO ABRIR EL PUERTO {puerto}.")
            print(f"[SSC32U-CORE] [SERIAL-TRACE] CAUSA EXACTA: {e}")
            print(f"[SSC32U-CORE] [WARN] EL SISTEMA ENTRARÁ EN MODO SIMULACIÓN. EL HARDWARE NO SE MOVERÁ.")
            self.serial = None

    def grados_a_pwm(self, grados):
        pwm = 500 + (grados / 180.0) * 2000
        return int(max(500, min(2500, pwm)))

    def mover_multiples_articulaciones(self, diccionario_angulos, tiempo=1000):
        print(f"\n[SSC32U-CORE] [RX-CMD] RECIBIDA ORDEN DE MOVIMIENTO: {diccionario_angulos}")
        comando_completo = ""
        
        for nombre, grados in diccionario_angulos.items():
            if nombre not in self.motores: 
                print(f"[SSC32U-CORE] [WARN] Articulación ignorada (No existe en YAML): {nombre}")
                continue
            
            # --- CANDADO DE PINZA ---
            if nombre == 'joint_gripper_finger':
                grados = max(68.0, min(180.0, grados))
                print(f"[SSC32U-CORE] [SEC-CHECK] Pinza forzada a márgenes seguros: {grados}°")
                
            datos = self.motores[nombre]
            canal = datos["canal"]
            grados_finales = grados + datos["offset_grados"]
            pulso = self.grados_a_pwm(grados_finales)
            
            print(f"[SSC32U-CORE] [MATH] {nombre} | Input: {grados}° | Offset: {datos['offset_grados']}° | Final: {grados_finales}° | PWM: {pulso}")
            
            comando_completo += f"#{canal} P{pulso} "
            
        if comando_completo:
            # El SSC-32U REQUIERE ESTRICTAMENTE un Carriage Return (\r) al final para ejecutar.
            comando_completo += f"T{tiempo}\r"
            
            # Usamos repr() para ver si los espacios y el \r están correctos en consola
            print(f"[SSC32U-CORE] [TX-RAW] STRING ASCII A ENVIAR: {repr(comando_completo)}")
            
            if self.serial:
                try:
                    self.serial.write(comando_completo.encode('ascii'))
                    print("[SSC32U-CORE] [TX-SUCCESS] BYTES ENVIADOS CORRECTAMENTE AL BUFFER USB.")
                except Exception as e:
                    print(f"[SSC32U-CORE] [TX-ERROR] FALLÓ LA ESCRITURA EN EL PUERTO SERIAL: {e}")
            else:
                print(f"[SSC32U-CORE] [SIMULADOR] VIRTUAL TX BYPASS: {repr(comando_completo)}")
        print("="*60)

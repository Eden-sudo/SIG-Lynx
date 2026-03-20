import yaml
import os

class ConfigManager:
    def __init__(self):
        # Calcula la ruta exacta: lynx_ui/../src/lynx_motion_core/lynx_motion_core/config_motores.yaml
        directorio_actual = os.path.dirname(os.path.abspath(__file__))
        self.ruta_yaml = os.path.abspath(os.path.join(
            directorio_actual, 
            '..', 
            'src', 
            'lynx_motion_core', 
            'lynx_motion_core', 
            'config_motores.yaml'
        ))

    def cargar(self):
        """Lee el archivo YAML y retorna el diccionario de datos."""
        if not os.path.exists(self.ruta_yaml):
            print(f"[ConfigManager] Error: No se encontró el archivo en {self.ruta_yaml}")
            return {}

        try:
            with open(self.ruta_yaml, 'r') as archivo:
                datos = yaml.safe_load(archivo)
                return datos if datos is not None else {}
        except Exception as e:
            print(f"[ConfigManager] Error al leer YAML: {e}")
            return {}

    def guardar(self, datos_actualizados):
        """Sobrescribe el archivo YAML con el nuevo diccionario."""
        try:
            with open(self.ruta_yaml, 'w') as archivo:
                # default_flow_style=False asegura que se guarde en formato de bloque legible, no en línea
                yaml.dump(datos_actualizados, archivo, default_flow_style=False, sort_keys=False)
            print("[ConfigManager] Configuración guardada exitosamente.")
            return True
        except Exception as e:
            print(f"[ConfigManager] Error al guardar YAML: {e}")
            return False

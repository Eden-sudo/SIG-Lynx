import yaml
import os

class ConfigManager:
    def __init__(self):
        # Calculates the exact path: lynx_ui/../src/lynx_motion_core/lynx_motion_core/config_motores.yaml
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
        """Reads the YAML file and returns the data dictionary."""
        if not os.path.exists(self.ruta_yaml):
            print(f"[ConfigManager] Error: File not found at {self.ruta_yaml}")
            return {}

        try:
            with open(self.ruta_yaml, 'r') as archivo:
                datos = yaml.safe_load(archivo)
                return datos if datos is not None else {}
        except Exception as e:
            print(f"[ConfigManager] Error reading YAML: {e}")
            return {}

    def guardar(self, datos_actualizados):
        """Overwrites the YAML file with the new dictionary."""
        try:
            with open(self.ruta_yaml, 'w') as archivo:
                # default_flow_style=False ensures it is saved in a readable block format, not inline
                yaml.dump(datos_actualizados, archivo, default_flow_style=False, sort_keys=False)
            print("[ConfigManager] Configuration saved successfully.")
            return True
        except Exception as e:
            print(f"[ConfigManager] Error saving YAML: {e}")
            return False

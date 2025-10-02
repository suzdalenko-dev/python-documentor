import os
import json

def load_app_config():
    try:
        base_path = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "../../../../froxa-keys/froxa.db.json")
        )
        with open(base_path, "r", encoding="utf-8") as f:
            config_data = json.load(f)
            return config_data[0]  # Usar la primera configuración del JSON
    except Exception as e:
        print(f"❌ No se pudo cargar la configuración de PostgreSQL: {e}")
        return None
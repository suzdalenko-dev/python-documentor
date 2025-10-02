import os
import json
import mysql.connector
from froxa.utils.utilities.suzdal_logger import SuzdalLogger

# Load MySQL config from erpold.json
def load_mysql_config():
    try:
        base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../../froxa-keys/erpold.json"))
        with open(base_path, "r", encoding="utf-8") as f:
            config_data = json.load(f)
            return config_data[0]  # Use first connection
    except Exception as e:
        return None

class MySQLConn:
    def __init__(self):
        self.connection = None
        self.cursor = None
        self.config = load_mysql_config()

    def connect(self):
        if not self.config:
            return

        try:
            self.connection = mysql.connector.connect(
                host=self.config["host"],
                user=self.config["user"],
                password=self.config["password"],
                database=self.config["dbname"],
                port=self.config["port"]
            )
            self.cursor = self.connection.cursor()
        except mysql.connector.Error as e:
            self.connection = None

    def consult(self, query, params=None):
        result = []
  
        if not self.connection or not self.cursor:
            self.connect()

        if not self.connection:
            return None

        try:
            self.cursor.execute(query, params or ())
            columns = [col[0] for col in self.cursor.description]
            for row in self.cursor.fetchall():
                result.append({columns[i]: str(value) for i, value in enumerate(row)})
            return result
        except mysql.connector.Error as e:
            return None

    def close(self):
        try:
            if self.cursor:
                self.cursor.close()
        except Exception as e:
            print(f"❌ Error cerrando cursor: {e}")

        try:
            if self.connection:
                self.connection.close()
        except Exception as e:
            print(f"❌ Error cerrando conexión: {e}")

        self.cursor = None
        self.connection = None
        

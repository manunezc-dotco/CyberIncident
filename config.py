# config.py
import os

class Config:
    # Configuración XAMPP MySQL
    DB_HOST = "localhost"
    DB_USER = "root"
    DB_PASSWORD = ""  # XAMPP por defecto tiene password vacío
    DB_NAME = "cyberincident"
    DB_PORT = 3306
    
    # Configuración Flask
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-key-12345-cambiar-en-produccion')
    UPLOAD_FOLDER = "uploads"
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
    
    # Extensiones permitidas
    ALLOWED_EXTENSIONS = {
        'pdf', 'png', 'jpg', 'jpeg', 'txt', 'log', 
        'pcap', 'gif', 'bmp', 'webp'
    }

# Diccionario para mysql.connector
DB_CONFIG = {
    "host": Config.DB_HOST,
    "user": Config.DB_USER,
    "password": Config.DB_PASSWORD,
    "database": Config.DB_NAME,
    "port": Config.DB_PORT,
    "charset": "utf8mb4"
}
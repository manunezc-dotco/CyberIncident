Sistema de Gestión de Incidentes de Seguridad en AWS

---

1. Introducción y Contexto

1.1 Contexto del Proyecto

Las organizaciones actuales enfrentan un aumento constante de amenazas de seguridad informática. La gestión adecuada de incidentes es esencial para proteger la información de las empresas. CyberIncident es un sistema desarrollado para gestionar incidentes de seguridad utilizando servicios de Amazon Web Services (AWS), aprovechando las ventajas de la computación en la nube.

1.2 Objetivos del Sistema

Objetivo General

Implementar un sistema de información en la nube llamado CyberIncident para el registro, clasificación y análisis de incidentes de seguridad, utilizando servicios básicos de AWS con buenas prácticas de configuración y seguridad.

Objetivos Específicos

1. Desplegar una aplicación backend en una instancia EC2 con sistema operativo Linux
2. Utilizar una base de datos para almacenar información estructurada de incidentes
3. Implementar Amazon S3 para almacenamiento de evidencias
4. Integrar los servicios EC2, base de datos y S3 en una arquitectura básica
5. Documentar el proceso de despliegue y funcionamiento del sistema

---

2. Descripción del Sistema

2.1 Funcionalidades Principales

CyberIncident es una aplicación web que permite:

· Registrar incidentes de seguridad informática
· Clasificar incidentes por tipo, severidad y estado
· Adjuntar evidencias técnicas como logs, imágenes o documentos
· Consultar el historial de incidentes registrados
· Generar reportes y estadísticas

2.2 Arquitectura del Sistema

La arquitectura utiliza los siguientes servicios de AWS:

1. Amazon EC2: Instancia Linux que aloja la aplicación Flask
2. Base de Datos: Motor MySQL para almacenar información de incidentes
3. Amazon S3: Servicio de almacenamiento para evidencias
4. VPC: Red virtual para conectar los componentes
5. Security Groups: Control de acceso a los servicios

2.3 Flujo de Datos

1. Registro de Incidente
   · Usuario completa formulario
   · Aplicación valida datos
   · Se guarda en base de datos
   · Se registra en historial
2. Subida de Evidencias
   · Usuario selecciona archivo
   · Aplicación valida tipo y tamaño
   · Archivo se sube a S3
   · Se guardan metadatos en base de datos
   · Se crea backup local
3. Consulta de Información
   · Aplicación consulta base de datos
   · Recupera información de incidentes
   · Genera URLs para acceder a evidencias
   · Presenta datos en interfaz web

---

3. Componentes Técnicos

3.1 Backend (Flask Application)

· Framework: Flask (Python)
· Base de datos: MySQL
· Almacenamiento: AWS S3
· Autenticación: Sistema básico de sesiones

3.2 Frontend

· Templates: HTML con Jinja2
· Estilos: Bootstrap 5
· JavaScript: Funcionalidades básicas

3.3 Base de Datos

Tablas principales:

· incidentes: Información de cada incidente
· evidencias: Archivos adjuntos a incidentes
· historial: Registro de actividades del sistema

3.4 AWS S3

· Bucket: cyberincident
· Estructura: evidencias/{incidente_id}/
· Configuración: Acceso privado, encriptación SSE-S3

---

4. Configuración de Seguridad

4.1 EC2 Security Group

· Puerto 22 (SSH): Solo desde IP específica
· Puerto 5000 (HTTP): Acceso público
· Puerto 3306 (MySQL): Solo desde EC2

4.2 RDS Security Group

· Puerto 3306: Solo acceso desde EC2 Security Group

4.3 S3 Policies

· Bloqueo de acceso público
· Políticas IAM restrictivas
· Encriptación automática

4.4 Seguridad en la Aplicación

· Sanitización de inputs
· Validación de archivos
· Protección contra XSS
· Límites de tamaño de archivo

---

5. Proceso de Despliegue

5.1 Paso 1: Configuración de AWS

1. Crear VPC y subredes
2. Configurar Internet Gateway
3. Crear Security Groups

5.2 Paso 2: Despliegue de RDS

1. Crear instancia MySQL
2. Configurar parámetros de seguridad
3. Establecer credenciales

5.3 Paso 3: Configuración de S3

1. Crear bucket
2. Configurar políticas de acceso
3. Establecer configuración de encriptación

5.4 Paso 4: Despliegue de EC2

1. Lanzar instancia Ubuntu
2. Configurar Security Group
3. Instalar dependencias
4. Desplegar aplicación

5.5 Paso 5: Configuración de Aplicación

1. Configurar conexión a base de datos
2. Establecer credenciales AWS
3. Configurar parámetros de seguridad
4. Iniciar servicio

---

6. Scripts y Configuraciones

6.1 Script de Inicialización EC2

```bash
#!/bin/bash
# Script de inicialización para instancia EC2

# Actualizar sistema
apt-get update
apt-get upgrade -y

# Instalar dependencias
apt-get install -y python3-pip python3-dev nginx git

# Instalar paquetes Python
pip3 install flask mysql-connector-python boto3 werkzeug

# Configurar Nginx
cat > /etc/nginx/sites-available/cyberincident << 'EOF'
server {
    listen 80;
    server_name _;
    
    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
EOF

# Habilitar sitio
ln -s /etc/nginx/sites-available/cyberincident /etc/nginx/sites-enabled/
rm /etc/nginx/sites-enabled/default

# Reiniciar Nginx
systemctl restart nginx
systemctl enable nginx

# Configurar servicio Systemd
cat > /etc/systemd/system/cyberincident.service << 'EOF'
[Unit]
Description=CyberIncident Application
After=network.target

[Service]
User=ubuntu
WorkingDirectory=/var/www/cyberincident
ExecStart=/usr/bin/python3 app.py
Restart=always

[Install]
WantedBy=multi-user.target
EOF

# Iniciar servicio
systemctl daemon-reload
systemctl start cyberincident
systemctl enable cyberincident
```

6.2 Configuración de la Aplicación

```python
# config.py
import os

class Config:
    # Configuración de base de datos
    DB_HOST = 'cyberincident-db.cxvvvkdnihbk.us-east-1.rds.amazonaws.com'
    DB_USER = 'Maik'
    DB_PASSWORD = 'cyberIncident123'
    DB_NAME = 'cyberincident'
    DB_PORT = 3306
    
    # Configuración de S3
    S3_BUCKET = 'cyberincident'
    S3_REGION = 'us-east-1'
    
    # Configuración de aplicación
    SECRET_KEY = 'clave-secreta-de-desarrollo'
    UPLOAD_FOLDER = 'uploads'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
```

6.3 Estructura de Base de Datos

```sql
-- Tabla de incidentes
CREATE TABLE incidentes (
    id INT PRIMARY KEY AUTO_INCREMENT,
    titulo VARCHAR(200) NOT NULL,
    descripcion TEXT NOT NULL,
    tipo VARCHAR(50) NOT NULL,
    severidad VARCHAR(20) NOT NULL,
    estado VARCHAR(30) DEFAULT 'Abierto',
    usuario_reporta VARCHAR(100),
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabla de evidencias
CREATE TABLE evidencias (
    id INT PRIMARY KEY AUTO_INCREMENT,
    incidente_id INT NOT NULL,
    nombre_archivo VARCHAR(255) NOT NULL,
    tipo_archivo VARCHAR(30),
    ruta TEXT,
    s3_key VARCHAR(500),
    s3_url VARCHAR(1000),
    tamano BIGINT,
    fecha_subida TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (incidente_id) REFERENCES incidentes(id) ON DELETE CASCADE
);

-- Tabla de historial
CREATE TABLE historial (
    id INT PRIMARY KEY AUTO_INCREMENT,
    incidente_id INT NOT NULL,
    usuario VARCHAR(100) NOT NULL,
    accion VARCHAR(50) NOT NULL,
    descripcion TEXT,
    fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (incidente_id) REFERENCES incidentes(id) ON DELETE CASCADE
);
```

---

7. Verificación y Monitoreo

7.1 Comandos de Verificación

```bash
# Verificar conexión a RDS
mysql -h cyberincident-db.cxvvvkdnihbk.us-east-1.rds.amazonaws.com -u Maik -p

# Verificar bucket S3
aws s3 ls s3://cyberincident

# Verificar aplicación
curl http://localhost:5000/status

# Verificar logs
journalctl -u cyberincident -f
tail -f /var/log/nginx/access.log
```

7.2 Monitoreo de Recursos

```bash
# Uso de CPU y memoria
top

# Uso de disco
df -h

# Conexiones de red
netstat -tulpn
```

---

8. Solución de Problemas

8.1 Problema: Conexión a base de datos fallida

Solución:

1. Verificar Security Groups
2. Confirmar que RDS está disponible
3. Verificar credenciales
4. Probar conexión desde EC2

8.2 Problema: Aplicación no responde

Solución:

1. Verificar estado del servicio
2. Revisar logs de error
3. Confirmar que puertos están abiertos
4. Reiniciar servicios

8.3 Problema: Archivos no se suben a S3

Solución:

1. Verificar credenciales AWS
2. Confirmar permisos del bucket
3. Verificar tamaño de archivo
4. Revisar tipos de archivo permitidos

---

9. Evidencias del Sistema (Espacio para imágenes)

9.1 Evidencias de Amazon EC2

Figura 1: Estado de la instancia EC2 en ejecución (Running)
Figura 2: Detalles generales de la instancia (ID, tipo, región, sistema operativo)
Figura 3: Configuración del Security Group asociado
Figura 4: Conexión exitosa por SSH desde un cliente local
Figura 5: Acceso a la aplicación web mediante la IP pública o DNS

9.2 Evidencias de la Base de Datos (RDS / MySQL)

Figura 6: Estado de la instancia RDS como disponible
Figura 7: Endpoint de conexión configurado
Figura 8: Conexión exitosa desde la instancia EC2
Figura 9: Ejecución de consultas SQL que evidencien datos almacenados

9.3 Evidencias de Amazon S3

Figura 10: Bucket cyberincident creado
Figura 11: Estructura de carpetas evidencias/{incidente_id}/
Figura 12: Archivos cargados (capturas, documentos, logs)
Figura 13: Configuración de bloqueo de acceso público
Figura 14: Encriptación habilitada en el bucket

9.4 Evidencias del Funcionamiento de la Aplicación

Figura 15: Formulario de registro de incidentes
Figura 16: Incidentes creados correctamente
Figura 17: Subida de evidencias desde la aplicación
Figura 18: Consulta del historial de incidentes
Figura 19: Registros de logs del sistema

9.5 Evidencias de Integración entre Servicios AWS

Figura 20: EC2 accediendo a RDS
Figura 21: EC2 subiendo archivos a S3
Figura 22: Registros en la base de datos con referencias a objetos almacenados en S3

---

10. Anexos

Anexo A: Comandos AWS CLI Utilizados

```bash
# EC2
aws ec2 describe-instances
aws ec2 run-instances
aws ec2 create-security-group

# RDS
aws rds create-db-instance
aws rds describe-db-instances

# S3
aws s3api create-bucket
aws s3api put-public-access-block
aws s3 ls
```

Anexo B: Estructura del Proyecto

```
cyberincident/
├── app.py
├── config.py
├── requirements.txt
├── templates/
│   ├── base.html
│   ├── index.html
│   ├── incidentes.html
│   ├── nuevo_incidente.html
│   ├── detalle.html
│   ├── historial.html
├── static/
│   ├── css/
│   ├── js/
│   └── img/
├── uploads/
└── README.md
```

Anexo C: Referencias Técnicas

1. Documentación oficial AWS
2. Flask Documentation
3. MySQL Documentation
4. Bootstrap Documentation
5. Python Documentation

---

11. Información del Documento

Documentación elaborada por: Maik
Fecha: Enero 2026
Versión: 1.0
Estado: Completada

https://github.com/user-attachments/assets/9aa65e82-21f0-4d7b-b57b-daf6e8759a4b

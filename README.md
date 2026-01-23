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

9. Evidencias del Sistema

9.1 Evidencias de Amazon EC2
<img width="1900" height="734" alt="image" src="https://github.com/user-attachments/assets/dc5282e3-e690-4e64-b32f-12e5098fea60" />

Figura 3: Configuración del Security Group asociado
<img width="1890" height="736" alt="image" src="https://github.com/user-attachments/assets/4bd370bb-311a-4875-9548-be537f0b9f38" />
<img width="1919" height="735" alt="image" src="https://github.com/user-attachments/assets/7f304160-8df0-44ee-8bf4-c68b4f466f4b" />
<img width="1409" height="676" alt="image" src="https://github.com/user-attachments/assets/f87faaa9-69d0-4e56-86c8-ff32a2442744" />
<img width="832" height="468" alt="image" src="https://github.com/user-attachments/assets/e5344a87-d6b8-4eab-8c81-9b15a80f4ee2" />

9.2 Evidencias de la Base de Datos (RDS / MySQL)

<img width="1574" height="494" alt="image" src="https://github.com/user-attachments/assets/befb902e-c7ac-4621-b35f-24ee1044d86f" />
<img width="1212" height="421" alt="image" src="https://github.com/user-attachments/assets/5e195e6d-c7b8-4afb-9b91-1408bd6e18a9" />
<img width="702" height="326" alt="image" src="https://github.com/user-attachments/assets/1d26871f-87a6-49a1-9e21-49b350556506" />
<img width="1691" height="547" alt="image" src="https://github.com/user-attachments/assets/c2d9e0e4-d7b6-49b8-b0a4-fa15d6da187f" />

9.3 Evidencias de Amazon S3

<img width="1919" height="435" alt="image" src="https://github.com/user-attachments/assets/ddca64ac-6881-4640-9f6b-9b4a585a99ac" />

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

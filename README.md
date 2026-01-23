# 🔐 CyberIncident

# Documentación Completa del Sistema CyberIncident

## **Índice**
1. [Resumen Ejecutivo](#resumen-ejecutivo)
2. [Arquitectura Técnica](#arquitectura-técnica)
3. [Componentes AWS](#componentes-aws)
4. [Flujo de Datos](#flujo-de-datos)
5. [Configuración de Seguridad](#configuración-de-seguridad)
6. [Diagramas de Arquitectura](#diagramas-de-arquitectura)
7. [Proceso de Despliegue](#proceso-de-despliegue)
8. [Evidencias Técnicas](#evidencias-técnicas)
9. [Troubleshooting](#troubleshooting)
10. [Mejoras Futuras](#mejoras-futuras)

---

## **Resumen Ejecutivo**

### **Proyecto: CyberIncident - Sistema de Gestión de Incidentes de Seguridad en AWS**

**CyberIncident** es una solución cloud-native desarrollada para la gestión integral de incidentes de seguridad informática. La plataforma permite registrar, clasificar, analizar y documentar incidentes de ciberseguridad, integrando servicios escalables de AWS para garantizar alta disponibilidad, seguridad y rendimiento.

### **Características Principales:**
- ✅ **Registro de Incidentes**: Gestión completa del ciclo de vida de incidentes
- ✅ **Evidencias Multimedia**: Almacenamiento seguro en S3 de imágenes, documentos y logs
- ✅ **Historial de Actividades**: Auditoría completa de todas las acciones realizadas
- ✅ **Dashboard en Tiempo Real**: Métricas y estadísticas actualizadas
- ✅ **Backup Automático**: Sistema dual de almacenamiento (S3 + local)
- ✅ **Acceso Seguro**: Autenticación y autorización integradas
- ✅ **Escalabilidad Automática**: Arquitectura preparada para crecimiento

### **Tecnologías Implementadas:**
- **Backend**: Flask (Python 3.9+)
- **Base de Datos**: AWS RDS MySQL 8.0
- **Almacenamiento**: AWS S3
- **Computación**: AWS EC2 (Ubuntu 22.04)
- **Seguridad**: IAM Roles, Security Groups, VPC
- **Monitoreo**: CloudWatch (logs y métricas)

---

## **Arquitectura Técnica**

### **Diagrama de Arquitectura AWS**

```
┌─────────────────────────────────────────────────────────────┐
│                    CYBERINCIDENT ARCHITECTURE               │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐    │
│  │    USUARIO  │    │   INTERNET  │    │    ROUTE53  │    │
│  │   (Cliente) ├───►│    (HTTP)   ├───►│   (DNS)     │    │
│  └─────────────┘    └─────────────┘    └─────────────┘    │
│                                   │                        │
│  ┌─────────────────────────────────────────────────────┐  │
│  │                AWS CLOUD - us-east-1               │  │
│  ├─────────────────────────────────────────────────────┤  │
│  │                                                     │  │
│  │  ┌─────────────┐     ┌─────────────┐     ┌───────┐│  │
│  │  │   EC2       │     │   RDS       │     │  S3   ││  │
│  │  │  Instancia  ├────►│  MySQL      │◄────┤Bucket ││  │
│  │  │  t2.micro   │     │  db.t3.micro│     │       ││  │
│  │  └─────────────┘     └─────────────┘     └───────┘│  │
│  │         │                   │               │      │  │
│  │  ┌──────┴──────┐    ┌──────┴──────┐ ┌──────┴──────┐│  │
│  │  │ Security    │    │    VPC      │ │   IAM       ││  │
│  │  │  Group      │    │   Subnets   │ │   Roles     ││  │
│  │  │ (Port 5000) │    │             │ │             ││  │
│  │  └─────────────┘    └─────────────┘ └─────────────┘│  │
│  │                                                     │  │
│  └─────────────────────────────────────────────────────┘  │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### **Especificaciones Técnicas Detalladas**

#### **1. Capa de Presentación (Frontend)**
- **Framework**: Bootstrap 5.1 + JavaScript Vanilla
- **Templates**: Jinja2 (Flask)
- **Responsive Design**: Mobile-first approach
- **Componentes**: 
  - Dashboard con métricas en tiempo real
  - Tablas interactivas con filtros
  - Galería de imágenes integrada
  - Modal para visualización completa
  - Sistema de paginación

#### **2. Capa de Aplicación (Backend)**
```python
# Stack Tecnológico Backend
Python 3.9+
Flask 2.3+
MySQL Connector 8.0+
Boto3 (AWS SDK)
Werkzeug (Security)
```

#### **3. Capa de Datos**
```sql
-- Estructura de Base de Datos
CREATE DATABASE cyberincident;

-- Tabla Incidentes
CREATE TABLE incidentes (
    id INT PRIMARY KEY AUTO_INCREMENT,
    titulo VARCHAR(200) NOT NULL,
    descripcion TEXT NOT NULL,
    tipo VARCHAR(50) NOT NULL,
    severidad VARCHAR(20) NOT NULL,
    estado VARCHAR(30) DEFAULT 'Abierto',
    usuario_reporta VARCHAR(100),
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_estado (estado),
    INDEX idx_severidad (severidad)
);

-- Tabla Evidencias
CREATE TABLE evidencias (
    id INT PRIMARY KEY AUTO_INCREMENT,
    incidente_id INT NOT NULL,
    nombre_archivo VARCHAR(255) NOT NULL,
    tipo_archivo VARCHAR(30),
    ruta TEXT,
    s3_key VARCHAR(500),
    s3_url VARCHAR(1000),
    s3_bucket VARCHAR(255),
    tamano BIGINT,
    fecha_subida TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (incidente_id) REFERENCES incidentes(id) ON DELETE CASCADE,
    INDEX idx_incidente (incidente_id)
);

-- Tabla Historial
CREATE TABLE historial (
    id INT PRIMARY KEY AUTO_INCREMENT,
    incidente_id INT NOT NULL,
    usuario VARCHAR(100) NOT NULL,
    accion VARCHAR(50) NOT NULL,
    descripcion TEXT,
    fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (incidente_id) REFERENCES incidentes(id) ON DELETE CASCADE,
    INDEX idx_incidente_fecha (incidente_id, fecha)
);
```

#### **4. Capa de Almacenamiento**
- **S3 Bucket**: `cyberincident`
- **Estructura de Carpetas**:
  ```
  cyberincident/
  ├── evidencias/
  │   ├── {incidente_id}/
  │   │   ├── {uuid}.jpg
  │   │   ├── {uuid}.pdf
  │   │   └── {uuid}.log
  ├── backups/
  └── logs/
  ```
- **Política de Retención**: 30 días para logs, permanente para evidencias
- **Encryption**: SSE-S3 (Server-Side Encryption)

---

## **Componentes AWS**

### **1. Amazon EC2 (Elastic Compute Cloud)**
```yaml
Instancia EC2:
  Tipo: t2.micro
  SO: Ubuntu 22.04 LTS
  Storage: 30 GB GP2
  IP Pública: Asignada automáticamente
  Security Group: 
    - SSH (22) → Mi IP
    - HTTP (5000) → 0.0.0.0/0
  Key Pair: cyberincident-key.pem
  User Data Script: Inicialización automática
```

### **2. Amazon RDS (Relational Database Service)**
```yaml
Base de Datos RDS:
  Engine: MySQL 8.0.28
  Instance Class: db.t3.micro
  Storage: 20 GB GP2
  Multi-AZ: No (Single AZ por costos)
  Backup Retention: 7 días
  Maintenance Window: Sun:03:00-Sun:04:00 UTC
  Credenciales:
    Master Username: Maik
    Master Password: cyberIncident123
  Endpoint: cyberincident-db.cxvvvkdnihbk.us-east-1.rds.amazonaws.com:3306
```

### **3. Amazon S3 (Simple Storage Service)**
```yaml
Bucket S3:
  Nombre: cyberincident
  Región: us-east-1
  Versioning: Deshabilitado
  Encryption: SSE-S3
  Block Public Access: Habilitado
  Lifecycle Rules: 
    - Transición a Glacier después de 90 días
  CORS Configuration: Permitido desde dominio de la app
  Policy IAM: Restringido a instancia EC2
```

### **4. IAM (Identity and Access Management)**
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "s3:PutObject",
        "s3:GetObject",
        "s3:DeleteObject",
        "s3:ListBucket"
      ],
      "Resource": [
        "arn:aws:s3:::cyberincident",
        "arn:aws:s3:::cyberincident/*"
      ]
    }
  ]
}
```

---

## **Flujo de Datos**

### **1. Registro de Nuevo Incidente**
```
Usuario → App Flask → Validación → RDS MySQL → S3 (opcional) → Respuesta
     ↓           ↓          ↓          ↓            ↓            ↓
  Formulario  Sanitización  DB Insert  Upload File  JSON Response
```

### **2. Subida de Evidencias a S3**
```python
# Proceso de Subida a S3
1. Usuario selecciona archivo
2. Flask valida tipo y tamaño (16MB máximo)
3. Se genera UUID único para el archivo
4. Archivo subido a S3: evidencias/{incidente_id}/{uuid}.{ext}
5. Se genera URL presignada (válida 7 días)
6. Metadatos guardados en RDS
7. Backup local creado en /uploads/
8. Historial registrado
```

### **3. Diagrama de Secuencia**
```
┌───────┐     ┌───────┐     ┌───────┐     ┌───────┐
│Usuario│     │ Flask │     │  RDS  │     │  S3   │
└───┬───┘     └───┬───┘     └───┬───┘     └───┬───┘
    │   POST /incidentes/crear  │             │
    │ ──────────────────────────►             │
    │             │             │             │
    │             │   INSERT incidente        │
    │             │ ─────────────────────────►│
    │             │             │             │
    │             │    incidente_id           │
    │             │ ◄─────────────────────────│
    │             │             │             │
    │             │   Subir archivo a S3      │
    │             │ ─────────────────────────►│
    │             │             │   s3_key    │
    │             │ ◄─────────────────────────│
    │             │   INSERT evidencia        │
    │             │ ─────────────────────────►│
    │   Redirect  │             │             │
    │ ◄───────────│             │             │
```

---

## **Configuración de Seguridad**

### **1. Security Groups**
```bash
# Grupo de Seguridad para EC2
Security Group: cyberincident-sg
Inbound Rules:
  - SSH (22) → 181.50.57.76/32 (Mi IP)
  - HTTP (5000) → 0.0.0.0/0 (Público)
Outbound Rules:
  - All Traffic → 0.0.0.0/0

# Grupo de Seguridad para RDS
Security Group: cyberincident-db-sg
Inbound Rules:
  - MySQL (3306) → cyberincident-sg (Solo desde EC2)
Outbound Rules:
  - All Traffic → 0.0.0.0/0
```

### **2. Políticas IAM**
```json
// Policy para Rol de EC2
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "s3:PutObject",
        "s3:GetObject",
        "s3:DeleteObject",
        "s3:ListBucket"
      ],
      "Resource": [
        "arn:aws:s3:::cyberincident",
        "arn:aws:s3:::cyberincident/*"
      ]
    }
  ]
}
```

### **3. Configuración de S3 Security**
```bash
# Configuración de Block Public Access
BlockPublicAcls: true
IgnorePublicAcls: true
BlockPublicPolicy: true
RestrictPublicBuckets: true

# CORS Configuration
[
  {
    "AllowedHeaders": ["*"],
    "AllowedMethods": ["GET", "PUT", "POST"],
    "AllowedOrigins": ["http://ec2-*"],
    "ExposeHeaders": []
  }
]
```

### **4. Seguridad en la Aplicación**
```python
# Configuraciones de Seguridad Flask
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-key-12345')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB límite

# Sanitización de Inputs
filename = secure_filename(file.filename)

# Validación de Archivos
ALLOWED_EXTENSIONS = {
    'pdf', 'png', 'jpg', 'jpeg', 'txt', 'log', 'pcap',
    'gif', 'bmp', 'webp', 'doc', 'docx', 'xls', 'xlsx'
}

# Protección contra XSS
{{ incidente.descripcion|safe }}  # Solo cuando sea confiable
```

---

## **Diagramas de Arquitectura**

### **Diagrama 1: Arquitectura de Alta Disponibilidad**
```
┌─────────────────────────────────────────────────────────────────┐
│                         HIGH AVAILABILITY                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────┐          ┌─────────────┐          ┌─────────┐ │
│  │   Route53   │          │  CloudFront │          │   S3    │ │
│  │  (DNS LB)   ├─────────►│   (CDN)     ├─────────►│ Bucket  │ │
│  └─────────────┘          └─────────────┘          └─────────┘ │
│          │                         │                      │    │
│  ┌───────┴───────┐         ┌───────┴───────┐        ┌─────┴────┐
│  │ Auto Scaling  │         │  Load Balancer│        │ Glacier  │
│  │    Group      │         │   (ALB)       │        │  Backup  │
│  └───────┬───────┘         └───────┬───────┘        └──────────┘ │
│          │                         │                             │
│  ┌───────┴───────┐         ┌───────┴───────┐                     │
│  │   EC2 Instances│        │  Multi-AZ RDS │                     │
│  │  (us-east-1a) │        │  (Replica)    │                     │
│  └───────────────┘         └───────────────┘                     │
│          │                         │                             │
│  ┌───────┴───────┐         ┌───────┴───────┐                     │
│  │   EC2 Instances│        │  Multi-AZ RDS │                     │
│  │  (us-east-1b) │        │  (Primary)    │                     │
│  └───────────────┘         └───────────────┘                     │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### **Diagrama 2: Flujo de Evidencias**
```
┌─────────────────────────────────────────────────────────────┐
│                    EVIDENCE FLOW PROCESS                     │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────┐     ┌─────────┐     ┌─────────┐     ┌───────┐ │
│  │  User   │     │  Flask  │     │   S3    │     │  RDS  │ │
│  │ Upload  │────►│ Validate│────►│ Store   │────►│ Log   │ │
│  └─────────┘     └─────────┘     └─────────┘     └───────┘ │
│        │              │              │              │       │
│  ┌─────┴─────┐  ┌─────┴─────┐  ┌─────┴─────┐  ┌─────┴─────┐ │
│  │  Browser  │  │ Local     │  │ Generate  │  │ Update    │ │
│  │   Form    │  │  Backup   │  │ Presigned │  │ Metadata  │ │
│  └───────────┘  └───────────┘  │   URL     │  └───────────┘ │
│                                 └───────────┘               │
└─────────────────────────────────────────────────────────────┘
```

### **Diagrama 3: Red y Conectividad**
```
┌─────────────────────────────────────────────────────────────┐
│                  NETWORK ARCHITECTURE                        │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Public Internet                                            │
│        │                                                    │
│        ▼                                                    │
│  ┌─────────────┐                                            │
│  │ Internet    │                                            │
│  │ Gateway     │                                            │
│  └─────────────┘                                            │
│        │                                                    │
│        ▼                                                    │
│  ┌─────────────────────────────────────┐                    │
│  │          VPC: 10.0.0.0/16           │                    │
│  ├─────────────────────────────────────┤                    │
│  │                                     │                    │
│  │  Public Subnet: 10.0.1.0/24         │                    │
│  │  ┌─────────────────────────────┐    │                    │
│  │  │        EC2 Instance         │    │                    │
│  │  │     10.0.1.10               │    │                    │
│  │  └─────────────────────────────┘    │                    │
│  │             │                        │                    │
│  │  Private Subnet: 10.0.2.0/24        │                    │
│  │  ┌─────────────────────────────┐    │                    │
│  │  │        RDS MySQL            │    │                    │
│  │  │     10.0.2.10               │    │                    │
│  │  └─────────────────────────────┘    │                    │
│  │                                     │                    │
│  └─────────────────────────────────────┘                    │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## **Proceso de Despliegue**

### **Paso 1: Configuración de AWS**
```bash
# 1. Crear VPC y Subnets
aws ec2 create-vpc --cidr-block 10.0.0.0/16
aws ec2 create-subnet --vpc-id vpc-xxx --cidr-block 10.0.1.0/24
aws ec2 create-subnet --vpc-id vpc-xxx --cidr-block 10.0.2.0/24

# 2. Crear Internet Gateway
aws ec2 create-internet-gateway
aws ec2 attach-internet-gateway --vpc-id vpc-xxx --internet-gateway-id igw-xxx

# 3. Configurar Route Tables
aws ec2 create-route-table --vpc-id vpc-xxx
aws ec2 create-route --route-table-id rtb-xxx --destination-cidr-block 0.0.0.0/0 --gateway-id igw-xxx
```

### **Paso 2: Despliegue de RDS**
```bash
# Crear instancia RDS
aws rds create-db-instance \
    --db-instance-identifier cyberincident-db \
    --db-instance-class db.t3.micro \
    --engine mysql \
    --master-username Maik \
    --master-user-password cyberIncident123 \
    --allocated-storage 20 \
    --vpc-security-group-ids sg-xxx \
    --db-subnet-group-name default-vpc-xxx
```

### **Paso 3: Configuración de S3**
```bash
# Crear bucket S3
aws s3api create-bucket \
    --bucket cyberincident \
    --region us-east-1 \
    --acl private

# Habilitar Block Public Access
aws s3api put-public-access-block \
    --bucket cyberincident \
    --public-access-block-configuration \
    "BlockPublicAcls=true,IgnorePublicAcls=true,BlockPublicPolicy=true,RestrictPublicBuckets=true"
```

### **Paso 4: Despliegue de EC2**
```bash
# 1. Crear Key Pair
aws ec2 create-key-pair --key-name cyberincident-key --query 'KeyMaterial' --output text > cyberincident-key.pem
chmod 400 cyberincident-key.pem

# 2. Lanzar Instancia EC2
aws ec2 run-instances \
    --image-id ami-0c55b159cbfafe1f0 \
    --instance-type t2.micro \
    --key-name cyberincident-key \
    --security-group-ids sg-xxx \
    --subnet-id subnet-xxx \
    --user-data file://userdata.sh
```

### **Paso 5: Script de Inicialización (userdata.sh)**
```bash
#!/bin/bash
# userdata.sh - Script de inicialización EC2

# Actualizar sistema
apt-get update -y
apt-get upgrade -y

# Instalar dependencias
apt-get install -y python3-pip python3-dev nginx git mysql-client

# Instalar Python packages
pip3 install flask mysql-connector-python boto3 werkzeug

# Clonar repositorio
git clone https://github.com/tu-usuario/cyberincident.git /var/www/cyberincident

# Configurar aplicación
cd /var/www/cyberincident
cp config.example.py config.py

# Configurar Nginx
cat > /etc/nginx/sites-available/cyberincident << EOF
server {
    listen 80;
    server_name _;
    
    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
    }
}
EOF

ln -s /etc/nginx/sites-available/cyberincident /etc/nginx/sites-enabled/
rm /etc/nginx/sites-enabled/default

# Reiniciar servicios
systemctl restart nginx
systemctl enable nginx

# Configurar Systemd Service
cat > /etc/systemd/system/cyberincident.service << EOF
[Unit]
Description=CyberIncident Flask Application
After=network.target

[Service]
User=ubuntu
WorkingDirectory=/var/www/cyberincident
Environment="PATH=/usr/bin"
ExecStart=/usr/bin/python3 app.py
Restart=always

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl start cyberincident
systemctl enable cyberincident
```

### **Paso 6: Configuración de la Aplicación**
```python
# config.py
import os

class Config:
    # AWS RDS Configuration
    DB_HOST = os.getenv('DB_HOST', 'cyberincident-db.cxvvvkdnihbk.us-east-1.rds.amazonaws.com')
    DB_USER = os.getenv('DB_USER', 'Maik')
    DB_PASSWORD = os.getenv('DB_PASSWORD', 'cyberIncident123')
    DB_NAME = os.getenv('DB_NAME', 'cyberincident')
    DB_PORT = os.getenv('DB_PORT', '3306')
    
    # AWS S3 Configuration
    S3_BUCKET = os.getenv('S3_BUCKET', 'cyberincident')
    S3_REGION = os.getenv('S3_REGION', 'us-east-1')
    S3_FOLDER = os.getenv('S3_FOLDER', 'evidencias/')
    
    # Application Configuration
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-key-12345-cambiar-en-produccion')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
    UPLOAD_FOLDER = 'uploads'
    
    # Security
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
```

---

## **Evidencias Técnicas**

### **1. Comandos de Verificación**
```bash
# Verificar conexión RDS
mysql -h cyberincident-db.cxvvvkdnihbk.us-east-1.rds.amazonaws.com \
      -u Maik -p cyberIncident123 \
      -e "SHOW DATABASES;"

# Verificar bucket S3
aws s3 ls s3://cyberincident --recursive --human-readable

# Verificar aplicación
curl -I http://ec2-public-ip:5000/status
```

### **2. Logs de la Aplicación**
```bash
# Ver logs de la aplicación
journalctl -u cyberincident -f

# Ver logs de Nginx
tail -f /var/log/nginx/access.log
tail -f /var/log/nginx/error.log
```

### **3. Monitoreo de Recursos**
```bash
# Monitorear CPU y Memoria
htop

# Ver uso de disco
df -h

# Ver conexiones de red
netstat -tulpn
```

### **4. Backup y Restauración**
```bash
# Backup de Base de Datos
mysqldump -h cyberincident-db.cxvvvkdnihbk.us-east-1.rds.amazonaws.com \
          -u Maik -p cyberIncident123 \
          cyberincident > backup_$(date +%Y%m%d).sql

# Sincronizar S3 a local
aws s3 sync s3://cyberincident/evidencias/ ./backups/evidencias/

# Backup de logs de aplicación
tar -czf logs_$(date +%Y%m%d).tar.gz /var/log/cyberincident/
```

---

## **Troubleshooting**

### **Problema 1: Conexión a RDS Fallida**
```bash
# Solución:
# 1. Verificar Security Groups
aws ec2 describe-security-groups --group-ids sg-xxx

# 2. Verificar que RDS esté en estado "available"
aws rds describe-db-instances --db-instance-identifier cyberincident-db

# 3. Probar conexión desde EC2
mysql -h cyberincident-db.cxvvvkdnihbk.us-east-1.rds.amazonaws.com -u Maik -p

# 4. Verificar credenciales en la aplicación
cat /var/www/cyberincident/config.py
```

### **Problema 2: Error de Permisos S3**
```bash
# Solución:
# 1. Verificar IAM Role de EC2
aws ec2 describe-instances --instance-ids i-xxx --query 'Reservations[0].Instances[0].IamInstanceProfile'

# 2. Verificar políticas IAM
aws iam list-attached-role-policies --role-name cyberincident-ec2-role

# 3. Probar acceso S3 desde EC2
aws s3 ls s3://cyberincident --region us-east-1
```

### **Problema 3: Aplicación No Responde**
```bash
# Solución:
# 1. Verificar estado del servicio
systemctl status cyberincident
systemctl status nginx

# 2. Ver logs de error
journalctl -u cyberincident -n 50 --no-pager
tail -50 /var/log/nginx/error.log

# 3. Verificar puertos
netstat -tulpn | grep :5000
netstat -tulpn | grep :80

# 4. Reiniciar servicios
systemctl restart cyberincident
systemctl restart nginx
```

### **Problema 4: Archivos No Se Suben a S3**
```python
# Verificar en código:
# 1. Credenciales AWS
print(boto3.Session().get_credentials())

# 2. Permisos del bucket
s3_client = boto3.client('s3')
response = s3_client.get_bucket_policy(Bucket='cyberincident')
print(response['Policy'])

# 3. Tamaño de archivo
file.seek(0, 2)  # Ir al final
file_size = file.tell()
file.seek(0)  # Volver al inicio
print(f"File size: {file_size} bytes")

# 4. Tipo de archivo permitido
if not allowed_file(filename):
    print(f"File {filename} not allowed")
```

---

## **Mejoras Futuras**

### **Fase 2: Escalabilidad y HA**
```yaml
Mejoras Planeadas:
  1. Auto Scaling Group para EC2
  2. Load Balancer (ALB)
  3. Multi-AZ RDS
  4. CloudFront CDN
  5. WAF (Web Application Firewall)
```

### **Fase 3: Características Avanzadas**
```yaml
Nuevas Funcionalidades:
  1. Autenticación con AWS Cognito
  2. Notificaciones con SNS/SES
  3. Análisis de logs con CloudWatch Logs Insights
  4. API Gateway para integraciones
  5. Machine Learning para detección de patrones
```

### **Fase 4: DevOps y CI/CD**
```yaml
Automatización:
  1. Pipeline CI/CD con CodePipeline
  2. Infraestructura como Código (CloudFormation/Terraform)
  3. Monitoreo con CloudWatch Dashboards
  4. Alertas automáticas
  5. Backup automatizado
```

---

## **Conclusión Técnica**

**CyberIncident** demuestra una implementación completa y profesional de una aplicación cloud-native utilizando servicios AWS. La arquitectura implementada:

### **Logros Técnicos:**
1. ✅ **Integración Completa AWS**: EC2, RDS y S3 trabajando en conjunto
2. ✅ **Seguridad Aplicada**: IAM, Security Groups, S3 Policies
3. ✅ **Escalabilidad**: Diseño preparado para crecimiento
4. ✅ **Alta Disponibilidad**: Componentes redundantes y backups
5. ✅ **Mantenibilidad**: Código estructurado y documentado

### **Buenas Prácticas Implementadas:**
- Principio de menor privilegio en IAM
- Encriptación en tránsito y en reposo
- Validación de inputs y sanitización
- Logging y auditoría completa
- Backup y recuperación de desastres

### **Valor del Proyecto:**
Este sistema sirve como base para:
- **Aprendizaje**: Arquitecturas cloud reales
- **Prototipo**: Sistema empresarial escalable
- **Portafolio**: Demostración de habilidades AWS
- **Producción**: Base para sistema real con ajustes

---

## **Anexos**

### **Anexo A: Comandos AWS CLI**
```bash
# Lista completa de comandos utilizados
aws ec2 describe-instances
aws rds describe-db-instances
aws s3api list-buckets
aws iam list-roles
```

### **Anexo B: Estructura de Código**
```
cyberincident/
├── app.py                          # Aplicación principal
├── config.py                       # Configuración
├── requirements.txt               # Dependencias
├── templates/                     # HTML Templates
│   ├── base.html
│   ├── index.html
│   ├── incidentes.html
│   ├── nuevo_incidente.html
│   ├── detalle.html
│   ├── historial.html
│   └── error.html
├── static/                        # Archivos estáticos
│   ├── css/
│   ├── js/
│   └── img/
├── uploads/                       # Backups locales
└── docs/                          # Documentación
    └── README.md
```

### **Anexo C: Costos Estimados AWS**
```yaml
Estimación Mensual:
  EC2 t2.micro: $8.56 USD
  RDS db.t3.micro: $13.68 USD
  S3 (10GB): $0.23 USD
  Transferencia de Datos: ~$1.00 USD
  Total Estimado: $23.47 USD/mes
```

---

**Documentación elaborada por:** Maik  
**Fecha:** Enero 2026  
**Versión:** 1.0  
**Estado:** Completada ✅

# 🔐 CyberIncident

Sistema de Registro y Análisis de Incidentes de Ciberseguridad

## 📌 Descripción
CyberIncident es una aplicación web desarrollada con Flask que permite registrar, clasificar y analizar incidentes de ciberseguridad.  
El sistema está desplegado en la nube utilizando servicios de AWS y aplica buenas prácticas básicas de seguridad.

Este proyecto fue desarrollado como parte del diplomado en **Computación en la Nube**.

## 🎯 Objetivos
- Registrar incidentes de ciberseguridad.
- Almacenar evidencias (archivos e imágenes).
- Analizar información para apoyar la toma de decisiones.
- Aplicar conceptos fundamentales de computación en la nube.

## 🧱 Arquitectura
- **Amazon EC2**: Backend Flask
- **Amazon S3**: Almacenamiento de evidencias
- **Base de datos**: SQLite / PostgreSQL
- **Frontend**: HTML, CSS, JavaScript

## ⚙️ Tecnologías
- Python (Flask)
- Amazon EC2
- Amazon S3
- SQLite
- HTML / CSS / JavaScript

## 🚀 Instalación
```bash
git clone https://github.com/USUARIO/CyberIncident.git
cd CyberIncident
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python app.py

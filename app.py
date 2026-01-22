from flask import Flask, render_template, request, redirect, url_for, send_from_directory, abort, flash, jsonify, session
import mysql.connector
import os
from datetime import datetime
from werkzeug.utils import secure_filename
import logging
import traceback
import time

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = 'dev-key-12345-cambiar-en-produccion'

# ==============================
# CONFIGURACIÓN XAMPP
# ==============================
UPLOAD_FOLDER = "uploads"
ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg', 'txt', 'log', 'pcap', 'gif', 'bmp', 'webp'}

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024  # 16MB

# Crear carpeta uploads si no existe
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Configuración XAMPP MySQL
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "",
    "database": "cyberincident",
    "port": 3306,
    "charset": "utf8mb4",
    "autocommit": True
}

# ==============================
# FUNCIONES AUXILIARES
# ==============================
def allowed_file(filename):
    if '.' not in filename or filename.strip() == '':
        return False
    extension = filename.rsplit('.', 1)[1].lower()
    return extension in ALLOWED_EXTENSIONS

def get_db():
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        return conn
    except mysql.connector.Error as err:
        logger.error(f"Error de conexión MySQL: {err}")
        raise

def get_current_user():
    """Obtiene el usuario actual (simulado para desarrollo)"""
    return session.get('usuario', 'admin@cyberincident.com')

def registrar_historial(incidente_id, accion, descripcion=None, usuario=None):
    """Registra una acción en el historial"""
    try:
        if usuario is None:
            usuario = get_current_user()
        
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        sql = """
            INSERT INTO historial
            (incidente_id, usuario, accion, descripcion)
            VALUES (%s, %s, %s, %s)
        """
        
        cursor.execute(sql, (incidente_id, usuario, accion, descripcion))
        conn.commit()
        cursor.close()
        conn.close()
        
        logger.debug(f"Historial registrado: {accion} para incidente {incidente_id}")
        return True
        
    except Exception as e:
        logger.error(f"Error registrando historial: {e}")
        return False

def init_database():
    """Inicializa la base de datos"""
    try:
        temp_config = DB_CONFIG.copy()
        temp_config.pop('database', None)
        
        conn = mysql.connector.connect(**temp_config)
        cursor = conn.cursor()
        
        cursor.execute("CREATE DATABASE IF NOT EXISTS cyberincident")
        cursor.execute("USE cyberincident")
        
        # Tabla incidentes
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS incidentes (
                id INT PRIMARY KEY AUTO_INCREMENT,
                titulo VARCHAR(200) NOT NULL,
                descripcion TEXT NOT NULL,
                tipo VARCHAR(50) NOT NULL,
                severidad VARCHAR(20) NOT NULL,
                estado VARCHAR(30) DEFAULT 'Abierto',
                usuario_reporta VARCHAR(100),
                fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Tabla evidencias
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS evidencias (
                id INT PRIMARY KEY AUTO_INCREMENT,
                incidente_id INT NOT NULL,
                nombre_archivo VARCHAR(255) NOT NULL,
                tipo_archivo VARCHAR(30),
                ruta TEXT,
                tamano BIGINT,
                fecha_subida TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (incidente_id) REFERENCES incidentes(id) ON DELETE CASCADE
            )
        """)
        
        # Tabla historial
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS historial (
                id INT PRIMARY KEY AUTO_INCREMENT,
                incidente_id INT NOT NULL,
                usuario VARCHAR(100) NOT NULL,
                accion VARCHAR(50) NOT NULL,
                descripcion TEXT,
                fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (incidente_id) REFERENCES incidentes(id) ON DELETE CASCADE
            )
        """)
        
        # Insertar datos de prueba si está vacío
        cursor.execute("SELECT COUNT(*) FROM incidentes")
        if cursor.fetchone()[0] == 0:
            logger.info("Insertando datos de prueba...")
            
            cursor.execute("""
                INSERT INTO incidentes (titulo, descripcion, tipo, severidad, usuario_reporta, estado)
                VALUES 
                ('Intento de phishing detectado', 'Se recibieron correos sospechosos', 'phishing', 'media', 'admin', 'Abierto'),
                ('Malware en equipo', 'Antivirus detectó troyano', 'malware', 'alta', 'soporte', 'En Investigación'),
                ('Acceso no autorizado', 'Intentos de acceso desde IPs desconocidas', 'intrusion', 'critica', 'admin', 'Resuelto')
            """)
            
            conn.commit()
        
        cursor.close()
        conn.close()
        
        logger.info("✅ Base de datos inicializada")
        return True
        
    except Exception as err:
        logger.error(f"Error inicializando base de datos: {err}")
        return False

# ==============================
# RUTAS PRINCIPALES
# ==============================

@app.route("/")
def index():
    try:
        db = get_db()
        cursor = db.cursor(dictionary=True)
        
        cursor.execute("SELECT COUNT(*) as total FROM incidentes")
        total = cursor.fetchone()['total']
        
        cursor.execute("SELECT COUNT(*) as abiertos FROM incidentes WHERE estado = 'Abierto'")
        abiertos = cursor.fetchone()['abiertos']
        
        cursor.execute("SELECT COUNT(*) as criticos FROM incidentes WHERE severidad = 'critica'")
        criticos = cursor.fetchone()['criticos']
        
        cursor.execute("SELECT COUNT(*) as resueltos FROM incidentes WHERE estado = 'Resuelto'")
        resueltos = cursor.fetchone()['resueltos']
        
        cursor.close()
        db.close()
        
        return render_template("index.html",
                             total=total,
                             abiertos=abiertos,
                             criticos=criticos,
                             resueltos=resueltos)
    
    except Exception as e:
        logger.error(f"Error en página principal: {e}")
        return render_template("index.html",
                             total=0,
                             abiertos=0,
                             criticos=0,
                             resueltos=0)

@app.route("/incidentes")
def listar_incidentes():
    try:
        db = get_db()
        cursor = db.cursor(dictionary=True)
        
        estado_filter = request.args.get('estado', 'todos')
        
        if estado_filter != 'todos':
            cursor.execute("SELECT * FROM incidentes WHERE estado = %s ORDER BY fecha_creacion DESC", (estado_filter,))
        else:
            cursor.execute("SELECT * FROM incidentes ORDER BY fecha_creacion DESC")
        
        incidentes = cursor.fetchall()
        
        cursor.close()
        db.close()
        
        return render_template("incidentes.html", 
                             incidentes=incidentes,
                             estado_filter=estado_filter)
    
    except Exception as e:
        logger.error(f"Error listando incidentes: {e}")
        flash("Error al cargar los incidentes", "danger")
        return render_template("incidentes.html", incidentes=[])

@app.route("/incidentes/nuevo")
def nuevo_incidente():
    return render_template("nuevo_incidente.html")

@app.route("/incidentes/crear", methods=["POST"])
def crear_incidente():
    try:
        data = request.form
        
        if not data.get('titulo') or not data.get('descripcion'):
            flash("Título y descripción son requeridos", "danger")
            return redirect(url_for('nuevo_incidente'))
        
        db = get_db()
        cursor = db.cursor()
        
        sql_incidente = """
            INSERT INTO incidentes
            (titulo, descripcion, tipo, severidad, usuario_reporta)
            VALUES (%s, %s, %s, %s, %s)
        """
        
        cursor.execute(sql_incidente, (
            data["titulo"],
            data["descripcion"],
            data["tipo"],
            data["severidad"],
            data.get("usuario_reporta", "Anónimo")
        ))
        
        incidente_id = cursor.lastrowid
        
        # Registrar en historial
        registrar_historial(
            incidente_id=incidente_id,
            accion="CREACION",
            descripcion=f"Incidente creado: {data['titulo']}"
        )
        
        uploaded_files = 0
        
        if 'evidencias' in request.files:
            files = request.files.getlist('evidencias')
            
            for file in files:
                if file and file.filename and file.filename.strip():
                    filename = secure_filename(file.filename)
                    
                    if not allowed_file(filename):
                        flash(f'Archivo "{filename}" no permitido', 'warning')
                        continue
                    
                    file.seek(0, 2)
                    file_size = file.tell()
                    file.seek(0)
                    
                    if file_size > app.config["MAX_CONTENT_LENGTH"]:
                        flash(f'Archivo "{filename}" es muy grande (máx 16MB)', 'warning')
                        continue
                    
                    incidente_folder = os.path.join(app.config["UPLOAD_FOLDER"], str(incidente_id))
                    os.makedirs(incidente_folder, exist_ok=True)
                    
                    unique_filename = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{filename}"
                    ruta = os.path.join(incidente_folder, unique_filename)
                    file.save(ruta)
                    
                    tipo_archivo = 'imagen' if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp', '.webp')) else 'documento'
                    
                    sql_evidencia = """
                        INSERT INTO evidencias
                        (incidente_id, nombre_archivo, tipo_archivo, ruta, tamano)
                        VALUES (%s, %s, %s, %s, %s)
                    """
                    
                    cursor.execute(sql_evidencia, (
                        incidente_id,
                        filename,
                        tipo_archivo,
                        ruta,
                        os.path.getsize(ruta)
                    ))
                    
                    uploaded_files += 1
        
        db.commit()
        cursor.close()
        db.close()
        
        if uploaded_files > 0:
            flash(f'✅ Incidente creado con {uploaded_files} archivo(s)', 'success')
        else:
            flash('✅ Incidente creado sin archivos adjuntos', 'info')
        
        return redirect(url_for("detalle_incidente", id=incidente_id))
        
    except Exception as e:
        logger.error(f"Error creando incidente: {e}")
        flash(f"❌ Error al crear incidente: {str(e)}", "danger")
        return redirect(url_for('nuevo_incidente'))

@app.route("/incidentes/<int:id>")
def detalle_incidente(id):
    try:
        db = get_db()
        cursor = db.cursor(dictionary=True)
        
        # Obtener incidente
        cursor.execute("SELECT * FROM incidentes WHERE id = %s", (id,))
        incidente = cursor.fetchone()
        
        if not incidente:
            flash("Incidente no encontrado", "danger")
            return redirect(url_for('listar_incidentes'))
        
        # Obtener evidencias
        cursor.execute("SELECT * FROM evidencias WHERE incidente_id = %s", (id,))
        evidencias = cursor.fetchall()
        
        # Obtener historial del incidente
        cursor.execute("""
            SELECT * FROM historial 
            WHERE incidente_id = %s 
            ORDER BY fecha DESC
            LIMIT 20
        """, (id,))
        historial = cursor.fetchall()
        
        cursor.close()
        db.close()
        
        return render_template(
            "detalle.html",
            incidente=incidente,
            evidencias=evidencias,
            historial=historial
        )
    
    except Exception as e:
        logger.error(f"Error obteniendo incidente {id}: {e}")
        flash("Error al cargar el incidente", "danger")
        return redirect(url_for('listar_incidentes'))

@app.route("/incidentes/<int:id>/cambiar-estado", methods=["POST"])
def cambiar_estado(id):
    try:
        nuevo_estado = request.form.get('estado')
        
        if nuevo_estado not in ['Abierto', 'En Investigación', 'Resuelto', 'Cerrado']:
            flash("Estado no válido", "danger")
            return redirect(url_for('detalle_incidente', id=id))
        
        db = get_db()
        cursor = db.cursor(dictionary=True)
        
        # Obtener estado actual
        cursor.execute("SELECT estado FROM incidentes WHERE id = %s", (id,))
        resultado = cursor.fetchone()
        estado_actual = resultado['estado'] if resultado else 'Desconocido'
        
        # Actualizar estado
        cursor.execute(
            "UPDATE incidentes SET estado = %s WHERE id = %s",
            (nuevo_estado, id)
        )
        
        db.commit()
        cursor.close()
        db.close()
        
        # Registrar en historial
        registrar_historial(
            incidente_id=id,
            accion="CAMBIO_ESTADO",
            descripcion=f"Estado cambiado de '{estado_actual}' a '{nuevo_estado}'"
        )
        
        flash(f'✅ Estado cambiado a {nuevo_estado}', 'success')
        return redirect(url_for('detalle_incidente', id=id))
    
    except Exception as e:
        logger.error(f"Error cambiando estado: {e}")
        flash("Error al cambiar estado", "danger")
        return redirect(url_for('detalle_incidente', id=id))

@app.route("/incidentes/<int:id>/eliminar", methods=["POST"])
def eliminar_incidente(id):
    try:
        db = get_db()
        cursor = db.cursor(dictionary=True)
        
        # Obtener información del incidente
        cursor.execute("SELECT titulo FROM incidentes WHERE id = %s", (id,))
        incidente = cursor.fetchone()
        titulo_incidente = incidente['titulo'] if incidente else 'Desconocido'
        
        # Obtener evidencias para eliminar archivos
        cursor.execute("SELECT ruta FROM evidencias WHERE incidente_id = %s", (id,))
        evidencias = cursor.fetchall()
        
        # Registrar en historial
        registrar_historial(
            incidente_id=id,
            accion="ELIMINACION",
            descripcion=f"Incidente eliminado: {titulo_incidente}"
        )
        
        # Eliminar archivos físicos
        for evidencia in evidencias:
            if evidencia['ruta'] and os.path.exists(evidencia['ruta']):
                try:
                    os.remove(evidencia['ruta'])
                except Exception as e:
                    logger.error(f"Error eliminando archivo: {e}")
        
        # Eliminar carpeta del incidente
        incidente_folder = os.path.join(app.config["UPLOAD_FOLDER"], str(id))
        if os.path.exists(incidente_folder):
            try:
                import shutil
                shutil.rmtree(incidente_folder)
            except Exception as e:
                logger.warning(f"No se pudo eliminar carpeta: {e}")
        
        # Eliminar de la base de datos
        cursor.execute("DELETE FROM incidentes WHERE id = %s", (id,))
        
        db.commit()
        cursor.close()
        db.close()
        
        flash('✅ Incidente eliminado correctamente', 'success')
        return redirect(url_for('listar_incidentes'))
    
    except Exception as e:
        db.rollback()
        logger.error(f"Error eliminando incidente: {e}")
        flash("Error al eliminar incidente", "danger")
        return redirect(url_for('detalle_incidente', id=id))

@app.route("/evidencias/<int:id>/eliminar", methods=["POST"])
def eliminar_evidencia(id):
    try:
        db = get_db()
        cursor = db.cursor(dictionary=True)
        
        # Obtener información de la evidencia
        cursor.execute("SELECT * FROM evidencias WHERE id = %s", (id,))
        evidencia = cursor.fetchone()
        
        if not evidencia:
            flash("Evidencia no encontrada", "danger")
            return redirect(url_for('listar_incidentes'))
        
        incidente_id = evidencia['incidente_id']
        nombre_archivo = evidencia['nombre_archivo']
        
        # Registrar en historial
        registrar_historial(
            incidente_id=incidente_id,
            accion="EVIDENCIA_ELIMINADA",
            descripcion=f"Archivo eliminado: {nombre_archivo}"
        )
        
        # Eliminar archivo físico
        if evidencia['ruta'] and os.path.exists(evidencia['ruta']):
            try:
                os.remove(evidencia['ruta'])
            except Exception as e:
                logger.error(f"Error eliminando archivo: {e}")
        
        # Eliminar de la base de datos
        cursor.execute("DELETE FROM evidencias WHERE id = %s", (id,))
        
        db.commit()
        cursor.close()
        db.close()
        
        flash('✅ Evidencia eliminada correctamente', 'success')
        return redirect(url_for('detalle_incidente', id=incidente_id))
    
    except Exception as e:
        db.rollback()
        logger.error(f"Error eliminando evidencia: {e}")
        flash("Error al eliminar evidencia", "danger")
        return redirect(url_for('detalle_incidente', id=evidencia['incidente_id']))

@app.route("/incidentes/<int:incidente_id>/comentario", methods=["POST"])
def agregar_comentario(incidente_id):
    """Agrega un comentario al historial del incidente"""
    try:
        comentario = request.form.get('comentario', '').strip()
        
        if not comentario:
            flash("El comentario no puede estar vacío", "warning")
            return redirect(url_for('detalle_incidente', id=incidente_id))
        
        # Registrar en historial
        if registrar_historial(
            incidente_id=incidente_id,
            accion="COMENTARIO",
            descripcion=comentario
        ):
            flash('✅ Comentario agregado al historial', 'success')
        else:
            flash('⚠️ Comentario guardado, pero error en historial', 'warning')
        
        return redirect(url_for('detalle_incidente', id=incidente_id))
    
    except Exception as e:
        logger.error(f"Error agregando comentario: {e}")
        flash("Error al agregar comentario", "danger")
        return redirect(url_for('detalle_incidente', id=incidente_id))

@app.route("/descargar/<int:evidencia_id>")
def descargar_evidencia(evidencia_id):
    try:
        db = get_db()
        cursor = db.cursor(dictionary=True)
        
        cursor.execute("SELECT * FROM evidencias WHERE id = %s", (evidencia_id,))
        evidencia = cursor.fetchone()
        
        cursor.close()
        db.close()
        
        if not evidencia or not evidencia['ruta']:
            flash("Archivo no encontrado", "danger")
            return redirect(request.referrer or url_for('index'))
        
        if os.path.exists(evidencia['ruta']):
            # Registrar descarga en historial
            registrar_historial(
                incidente_id=evidencia['incidente_id'],
                accion="DESCARGA_EVIDENCIA",
                descripcion=f"Archivo descargado: {evidencia['nombre_archivo']}"
            )
            
            directory = os.path.dirname(evidencia['ruta'])
            filename = os.path.basename(evidencia['ruta'])
            return send_from_directory(directory, filename, as_attachment=True, download_name=evidencia['nombre_archivo'])
        else:
            flash("El archivo no existe en el servidor", "danger")
            return redirect(request.referrer or url_for('index'))
    
    except Exception as e:
        logger.error(f"Error descargando archivo: {e}")
        flash("Error al descargar el archivo", "danger")
        return redirect(request.referrer or url_for('index'))

@app.route("/historial")
def ver_historial_completo():
    """Página para ver todo el historial del sistema"""
    try:
        db = get_db()
        cursor = db.cursor(dictionary=True)
        
        # Verificar si la tabla historial existe
        cursor.execute("SHOW TABLES LIKE 'historial'")
        if not cursor.fetchone():
            flash("La tabla de historial no está disponible", "warning")
            return render_template("historial.html", historial=[], page=1, total_pages=0, total=0)
        
        # Paginación
        page = request.args.get('page', 1, type=int)
        items_per_page = 20
        offset = (page - 1) * items_per_page
        
        # Obtener historial
        cursor.execute("""
            SELECT h.*, i.titulo as incidente_titulo, i.id as incidente_id
            FROM historial h 
            LEFT JOIN incidentes i ON h.incidente_id = i.id 
            ORDER BY h.fecha DESC 
            LIMIT %s OFFSET %s
        """, (items_per_page, offset))
        
        historial = cursor.fetchall()
        
        # Contar total de registros
        cursor.execute("SELECT COUNT(*) as total FROM historial")
        total = cursor.fetchone()['total']
        total_pages = (total + items_per_page - 1) // items_per_page
        
        cursor.close()
        db.close()
        
        return render_template(
            "historial.html",
            historial=historial,
            page=page,
            total_pages=total_pages,
            total=total
        )
    
    except Exception as e:
        logger.error(f"Error obteniendo historial: {e}")
        flash("Error al cargar el historial", "danger")
        return render_template("historial.html", historial=[], page=1, total_pages=0, total=0)
    
@app.route("/incidentes/<int:incidente_id>/evidencias/agregar", methods=["POST"])
def agregar_evidencias(incidente_id):
    """Agrega evidencias a un incidente existente"""
    try:
        uploaded_files = 0
        
        if 'evidencias' in request.files:
            files = request.files.getlist('evidencias')
            
            if not files or not files[0].filename:
                flash("Seleccione al menos un archivo", "warning")
                return redirect(url_for('detalle_incidente', id=incidente_id))
            
            db = get_db()
            cursor = db.cursor()
            
            for file in files:
                if file and file.filename and file.filename.strip():
                    filename = secure_filename(file.filename)
                    
                    if not allowed_file(filename):
                        flash(f'Archivo "{filename}" no permitido', 'warning')
                        continue
                    
                    file.seek(0, 2)
                    file_size = file.tell()
                    file.seek(0)
                    
                    if file_size > app.config["MAX_CONTENT_LENGTH"]:
                        flash(f'Archivo "{filename}" es muy grande (máx 16MB)', 'warning')
                        continue
                    
                    incidente_folder = os.path.join(app.config["UPLOAD_FOLDER"], str(incidente_id))
                    os.makedirs(incidente_folder, exist_ok=True)
                    
                    unique_filename = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{filename}"
                    ruta = os.path.join(incidente_folder, unique_filename)
                    file.save(ruta)
                    
                    # Determinar tipo de archivo
                    extension = filename.lower().split('.')[-1]
                    if extension in ['png', 'jpg', 'jpeg', 'gif', 'bmp', 'webp']:
                        tipo_archivo = 'imagen'
                    else:
                        tipo_archivo = 'documento'
                    
                    sql_evidencia = """
                        INSERT INTO evidencias
                        (incidente_id, nombre_archivo, tipo_archivo, ruta, tamano)
                        VALUES (%s, %s, %s, %s, %s)
                    """
                    
                    cursor.execute(sql_evidencia, (
                        incidente_id,
                        filename,
                        tipo_archivo,
                        ruta,
                        os.path.getsize(ruta)
                    ))
                    
                    uploaded_files += 1
                    
                    # Registrar en historial
                    registrar_historial(
                        incidente_id=incidente_id,
                        accion="EVIDENCIA_AGREGADA",
                        descripcion=f"Archivo agregado: {filename}"
                    )
            
            db.commit()
            cursor.close()
            db.close()
            
            if uploaded_files > 0:
                flash(f'✅ {uploaded_files} archivo(s) agregado(s)', 'success')
            else:
                flash('❌ No se pudieron agregar los archivos', 'warning')
        
        return redirect(url_for('detalle_incidente', id=incidente_id))
        
    except Exception as e:
        logger.error(f"Error agregando evidencias: {e}")
        flash(f"❌ Error al agregar evidencias: {str(e)}", "danger")
        return redirect(url_for('detalle_incidente', id=incidente_id))

@app.route("/evidencias/<int:evidencia_id>/ver")
def ver_imagen(evidencia_id):
    """Muestra una imagen en el navegador"""
    try:
        db = get_db()
        cursor = db.cursor(dictionary=True)
        
        cursor.execute("SELECT * FROM evidencias WHERE id = %s", (evidencia_id,))
        evidencia = cursor.fetchone()
        
        cursor.close()
        db.close()
        
        if not evidencia or not evidencia['ruta']:
            abort(404, "Imagen no encontrada")
        
        # Verificar que sea una imagen
        if evidencia['tipo_archivo'] != 'imagen':
            abort(400, "No es una imagen válida")
        
        if not os.path.exists(evidencia['ruta']):
            abort(404, "Archivo no encontrado en el servidor")
        
        # Registrar visualización en historial
        registrar_historial(
            incidente_id=evidencia['incidente_id'],
            accion="VISUALIZACION_IMAGEN",
            descripcion=f"Imagen visualizada: {evidencia['nombre_archivo']}"
        )
        
        return send_file(evidencia['ruta'], mimetype=f'image/{evidencia["nombre_archivo"].split(".")[-1]}')
    
    except Exception as e:
        logger.error(f"Error mostrando imagen: {e}")
        abort(404, f"Error al mostrar la imagen: {str(e)}")

@app.route("/incidentes/<int:incidente_id>/descargar-todo")
def descargar_todo(incidente_id):
    """Descarga todas las evidencias de un incidente en un ZIP"""
    try:
        import zipfile
        import io
        import tempfile
        
        db = get_db()
        cursor = db.cursor(dictionary=True)
        
        cursor.execute("SELECT * FROM evidencias WHERE incidente_id = %s", (incidente_id,))
        evidencias = cursor.fetchall()
        
        cursor.close()
        db.close()
        
        if not evidencias:
            flash("No hay evidencias para descargar", "warning")
            return redirect(url_for('detalle_incidente', id=incidente_id))
        
        # Crear archivo ZIP en memoria
        memory_file = io.BytesIO()
        with zipfile.ZipFile(memory_file, 'w', zipfile.ZIP_DEFLATED) as zf:
            for evidencia in evidencias:
                if os.path.exists(evidencia['ruta']):
                    zf.write(evidencia['ruta'], evidencia['nombre_archivo'])
        
        memory_file.seek(0)
        
        # Registrar en historial
        registrar_historial(
            incidente_id=incidente_id,
            accion="DESCARGA_COMPLETA",
            descripcion=f"Descargadas todas las evidencias ({len(evidencias)} archivos)"
        )
        
        return send_file(
            memory_file,
            mimetype='application/zip',
            as_attachment=True,
            download_name=f'incidente_{incidente_id}_evidencias.zip'
        )
    
    except Exception as e:
        logger.error(f"Error creando ZIP: {e}")
        flash("Error al crear el archivo ZIP", "danger")
        return redirect(url_for('detalle_incidente', id=incidente_id))

@app.route("/incidentes/<int:incidente_id>/exportar")
def exportar_informe(incidente_id):
    """Genera un informe PDF del incidente"""
    try:
        db = get_db()
        cursor = db.cursor(dictionary=True)
        
        # Obtener incidente
        cursor.execute("SELECT * FROM incidentes WHERE id = %s", (incidente_id,))
        incidente = cursor.fetchone()
        
        if not incidente:
            flash("Incidente no encontrado", "danger")
            return redirect(url_for('listar_incidentes'))
        
        # Obtener evidencias
        cursor.execute("SELECT * FROM evidencias WHERE incidente_id = %s", (incidente_id,))
        evidencias = cursor.fetchall()
        
        # Obtener historial
        cursor.execute("SELECT * FROM historial WHERE incidente_id = %s ORDER BY fecha DESC", (incidente_id,))
        historial = cursor.fetchall()
        
        cursor.close()
        db.close()
        
        # Para simplicidad, devolvemos una página HTML con la información
        # En producción, usarías una librería como ReportLab para PDF
        flash("Función de exportación en desarrollo", "info")
        return redirect(url_for('detalle_incidente', id=incidente_id))
    
    except Exception as e:
        logger.error(f"Error exportando informe: {e}")
        flash("Error al generar el informe", "danger")
        return redirect(url_for('detalle_incidente', id=incidente_id))

# Añade esta importación al inicio del archivo
from flask import send_file

def detectar_tipo_archivo(filename):
    """Detecta el tipo de archivo basado en la extensión"""
    if not filename or '.' not in filename:
        return 'desconocido'
    
    extension = filename.lower().split('.')[-1]
    
    tipos_imagen = ['png', 'jpg', 'jpeg', 'gif', 'bmp', 'webp', 'svg']
    tipos_documento = ['pdf', 'doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx']
    tipos_texto = ['txt', 'log', 'csv', 'json', 'xml', 'html', 'htm']
    tipos_archivo = ['zip', 'rar', '7z', 'tar', 'gz']
    tipos_video = ['mp4', 'avi', 'mov', 'wmv', 'flv', 'mkv']
    tipos_audio = ['mp3', 'wav', 'ogg', 'flac', 'aac']
    
    if extension in tipos_imagen:
        return 'imagen'
    elif extension in tipos_documento:
        return 'documento'
    elif extension in tipos_texto:
        return 'texto'
    elif extension in tipos_archivo:
        return 'archivo_comprimido'
    elif extension in tipos_video:
        return 'video'
    elif extension in tipos_audio:
        return 'audio'
    elif extension in ['pcap', 'pcapng']:
        return 'captura_red'
    else:
        return 'desconocido'

# Modifica la función allowed_file para aceptar más tipos
ALLOWED_EXTENSIONS = {
    # Imágenes
    'png', 'jpg', 'jpeg', 'gif', 'bmp', 'webp', 'svg',
    # Documentos
    'pdf', 'doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx', 'txt', 'csv',
    # Archivos de red/logs
    'log', 'pcap', 'pcapng',
    # Archivos comprimidos
    'zip', 'rar', '7z',
    # Video/Audio (opcional)
    'mp4', 'avi', 'mov', 'mp3', 'wav'
}


@app.route("/status")
def status():
    try:
        db = get_db()
        cursor = db.cursor()
        
        cursor.execute("SELECT 1")
        result = cursor.fetchone()
        
        db_status = 'connected' if result else 'disconnected'
        
        # Obtener estadísticas
        cursor.execute("SELECT COUNT(*) as total FROM incidentes")
        total_incidentes = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) as total FROM evidencias")
        total_evidencias = cursor.fetchone()[0]
        
        # Verificar si existe la tabla historial
        cursor.execute("SHOW TABLES LIKE 'historial'")
        historial_exists = cursor.fetchone() is not None
        
        if historial_exists:
            cursor.execute("SELECT COUNT(*) as total FROM historial")
            total_historial = cursor.fetchone()[0]
        else:
            total_historial = 0
        
        cursor.close()
        db.close()
        
        status_info = {
            'flask': 'running',
            'database': db_status,
            'database_type': 'MySQL (XAMPP)',
            'host': DB_CONFIG['host'],
            'database_name': DB_CONFIG['database'],
            'total_incidentes': total_incidentes,
            'total_evidencias': total_evidencias,
            'total_historial': total_historial,
            'historial_disponible': historial_exists,
            'uploads_folder': os.path.exists(app.config["UPLOAD_FOLDER"])
        }
        
        return jsonify(status_info)
    
    except Exception as e:
        return jsonify({
            'flask': 'running',
            'database': 'disconnected',
            'error': str(e)
        })

# ==============================
# MANEJO DE ERRORES
# ==============================

@app.errorhandler(404)
def pagina_no_encontrada(e):
    return "Página no encontrada - 404", 404

@app.errorhandler(500)
def error_servidor(e):
    logger.error(f"Error 500: {e}")
    return "Error interno del servidor - 500", 500

# ==============================
# MAIN
# ==============================
if __name__ == "__main__":
    print("\n" + "="*60)
    print("🚀 CYBERINCIDENT - Sistema de Gestión de Incidentes")
    print("="*60)
    print("📁 BASE DE DATOS: MySQL (XAMPP)")
    print(f"📂 Carpeta uploads: {UPLOAD_FOLDER}")
    print(f"🔗 URL principal: http://127.0.0.1:5000")
    print(f"📊 Estado: http://127.0.0.1:5000/status")
    print("="*60)
    print("📋 Rutas principales:")
    print("   /                    - Dashboard principal")
    print("   /incidentes          - Lista de incidentes")
    print("   /incidentes/nuevo    - Crear nuevo incidente")
    print("   /historial           - Historial completo")
    print("   /descargar/<id>      - Descargar evidencia")
    print("="*60)
    print("📝 FUNCIONALIDADES:")
    print("   ✅ Gestión de incidentes")
    print("   ✅ Subida de evidencias")
    print("   ✅ Sistema de historial")
    print("   ✅ Cambio de estados")
    print("   ✅ Comentarios")
    print("="*60)
    
    # Inicializar base de datos
    if init_database():
        print("✅ Base de datos inicializada")
    else:
        print("❌ Error inicializando base de datos")
    
    print("="*60 + "\n")
    
    app.run(host='127.0.0.1', port=5000, debug=True)
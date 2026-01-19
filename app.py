from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, abort, send_file, session
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, FileField, SubmitField
from wtforms.validators import DataRequired
from werkzeug.utils import secure_filename
import os
from datetime import datetime
import uuid
from PIL import Image
import io
import base64

# Inicializar Flask
app = Flask(__name__)

# Configuración para desarrollo local
app.config['SECRET_KEY'] = 'dev-key-12345-cambiar-en-produccion'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cyberincident.db'  # SQLite para desarrollo
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max-limit

# Configuración para archivos (almacenamiento local en desarrollo)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['THUMBNAIL_FOLDER'] = 'uploads/thumbnails'
app.config['ALLOWED_EXTENSIONS'] = {'pdf', 'png', 'jpg', 'jpeg', 'txt', 'log', 'pcap', 'gif', 'bmp', 'webp'}
app.config['THUMBNAIL_SIZE'] = (200, 200)
app.config['MAX_IMAGE_SIZE'] = (1920, 1080)

# Crear carpetas de uploads si no existen
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['THUMBNAIL_FOLDER'], exist_ok=True)

# Inicializar base de datos
db = SQLAlchemy(app)

# Modelos
class Incidente(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(200), nullable=False)
    descripcion = db.Column(db.Text, nullable=False)
    tipo = db.Column(db.String(50), nullable=False)
    severidad = db.Column(db.String(20), nullable=False)
    estado = db.Column(db.String(20), default='Abierto')
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    fecha_actualizacion = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    usuario_reporta = db.Column(db.String(100))
    evidencias = db.relationship('Evidencia', backref='incidente', lazy=True, cascade='all, delete-orphan')

class Evidencia(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre_archivo = db.Column(db.String(255), nullable=False)
    ruta_local = db.Column(db.String(500))  # Para desarrollo local
    datos_imagen = db.Column(db.Text)  # Para almacenar imágenes como base64
    tipo_archivo = db.Column(db.String(50))
    fecha_subida = db.Column(db.DateTime, default=datetime.utcnow)
    incidente_id = db.Column(db.Integer, db.ForeignKey('incidente.id'), nullable=False)

# Formularios
class IncidenteForm(FlaskForm):
    titulo = StringField('Título', validators=[DataRequired()])
    descripcion = TextAreaField('Descripción', validators=[DataRequired()])
    tipo = SelectField('Tipo', choices=[
        ('intrusion', 'Intrusión'),
        ('malware', 'Malware'),
        ('phishing', 'Phishing'),
        ('ddos', 'DDoS'),
        ('config_error', 'Error de Configuración'),
        ('data_leak', 'Fuga de Datos'),
        ('otro', 'Otro')
    ], validators=[DataRequired()])
    severidad = SelectField('Severidad', choices=[
        ('baja', 'Baja'),
        ('media', 'Media'),
        ('alta', 'Alta'),
        ('critica', 'Crítica')
    ], validators=[DataRequired()])
    usuario_reporta = StringField('Usuario que Reporta')
    evidencias = FileField('Evidencias (múltiples)')
    submit = SubmitField('Registrar Incidente')

# Funciones auxiliares
def allowed_file(filename):
    """Verifica si la extensión del archivo está permitida"""
    if '.' not in filename:
        return False
    extension = filename.rsplit('.', 1)[1].lower()
    # Asegúrate que 'pdf' esté en la lista
    return extension in app.config['ALLOWED_EXTENSIONS']

def is_image_file(filename):
    image_extensions = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'webp'}
    extension = filename.rsplit('.', 1)[1].lower()
    return extension in image_extensions

def save_file_locally(file, incidente_id):
    """Guarda archivo localmente y devuelve información"""
    try:
        filename = secure_filename(file.filename)
        # Crear carpeta para el incidente si no existe
        incidente_folder = os.path.join(app.config['UPLOAD_FOLDER'], str(incidente_id))
        os.makedirs(incidente_folder, exist_ok=True)
        
        # Generar nombre único
        unique_filename = f"{uuid.uuid4()}_{filename}"
        filepath = os.path.join(incidente_folder, unique_filename)
        
        # Leer el archivo
        file_data = file.read()
        
        # Guardar archivo
        with open(filepath, 'wb') as f:
            f.write(file_data)
        
        # Solo procesar como imagen si es realmente una imagen
        imagen_base64 = None
        if is_image_file(filename):
            try:
                # Convertir a base64 para mostrar en HTML
                imagen_base64 = base64.b64encode(file_data).decode('utf-8')
                
                # También crear una versión optimizada para vista previa
                img_buffer = io.BytesIO(file_data)
                img = Image.open(img_buffer)
                
                # Crear thumbnail si la imagen es grande
                if img.size[0] > 800 or img.size[1] > 600:
                    img.thumbnail((800, 600), Image.Resampling.LANCZOS)
                    buffer = io.BytesIO()
                    img.save(buffer, format='JPEG', quality=85, optimize=True)
                    imagen_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
                    
            except Exception as e:
                print(f"Error procesando imagen: {e}")
                # Si hay error, usar los datos originales
                imagen_base64 = base64.b64encode(file_data).decode('utf-8')
        
        return {
            'filename': filename,
            'filepath': filepath,
            'imagen_base64': imagen_base64,
            'tamano_bytes': len(file_data)
        }
        
    except Exception as e:
        print(f"Error guardando archivo: {e}")
        return None

# Rutas principales
@app.route('/')
def index():
    """Página principal con estadísticas y dashboard"""
    try:
        # Obtener estadísticas básicas
        total_incidentes = Incidente.query.count()
        incidentes_abiertos = Incidente.query.filter_by(estado='Abierto').count()
        incidentes_criticos = Incidente.query.filter_by(severidad='critica').count()
        incidentes_resueltos = Incidente.query.filter_by(estado='Resuelto').count()
        
        # Obtener incidentes recientes (últimos 5)
        incidentes_recientes = Incidente.query.order_by(Incidente.fecha_creacion.desc()).limit(5).all()
        
        # Calcular distribución por tipo
        tipos = db.session.query(
            Incidente.tipo, 
            db.func.count(Incidente.id).label('cantidad')
        ).group_by(Incidente.tipo).all()
        
        # Convertir a diccionario
        distribucion_tipos = {}
        for tipo, cantidad in tipos:
            distribucion_tipos[tipo] = cantidad
        
        # Si no hay datos, crear diccionario vacío
        if not distribucion_tipos:
            distribucion_tipos = {
                'intrusion': 0,
                'malware': 0,
                'phishing': 0,
                'ddos': 0,
                'config_error': 0,
                'data_leak': 0,
                'otro': 0
            }
        
        return render_template('index.html',
                             total=total_incidentes,
                             abiertos=incidentes_abiertos,
                             criticos=incidentes_criticos,
                             resueltos=incidentes_resueltos,
                             incidentes_recientes=incidentes_recientes,
                             distribucion_tipos=distribucion_tipos)
    
    except Exception as e:
        print(f"Error en página principal: {e}")
        # En caso de error, mostrar página básica
        return render_template('index.html',
                             total=0,
                             abiertos=0,
                             criticos=0,
                             resueltos=0,
                             incidentes_recientes=[],
                             distribucion_tipos={})

@app.route('/incidentes')
def listar_incidentes():
    """Lista todos los incidentes con paginación"""
    page = request.args.get('page', 1, type=int)
    estado_filter = request.args.get('estado', 'todos')
    
    query = Incidente.query
    
    if estado_filter != 'todos':
        query = query.filter_by(estado=estado_filter)
    
    incidentes = query.order_by(Incidente.fecha_creacion.desc()).paginate(
        page=page, per_page=10, error_out=False
    )
    
    return render_template('incidentes.html', 
                         incidentes=incidentes, 
                         estado_filter=estado_filter)

@app.route('/incidente/nuevo', methods=['GET', 'POST'])
def nuevo_incidente():
    form = IncidenteForm()
    
    if form.validate_on_submit():
        try:
            # Crear incidente
            incidente = Incidente(
                titulo=form.titulo.data,
                descripcion=form.descripcion.data,
                tipo=form.tipo.data,
                severidad=form.severidad.data,
                usuario_reporta=form.usuario_reporta.data or 'Anónimo'
            )
            
            db.session.add(incidente)
            db.session.commit()  # Commit para obtener el ID
            
            # Manejar evidencias
            uploaded_files = []
            if 'evidencias' in request.files:
                files = request.files.getlist('evidencias')
                
                for file in files:
                    if file and file.filename and file.filename.strip():
                        filename = secure_filename(file.filename)
                        
                        # Validaciones básicas
                        if not allowed_file(filename):
                            flash(f'⚠️ Archivo "{filename}" no permitido. Use formatos: {", ".join(app.config["ALLOWED_EXTENSIONS"])}', 'warning')
                            continue
                        
                        # Validar tamaño
                        file.seek(0, 2)  # Ir al final para obtener tamaño
                        file_size = file.tell()
                        file.seek(0)  # Volver al inicio
                        
                        if file_size > app.config['MAX_CONTENT_LENGTH']:
                            flash(f'⚠️ Archivo "{filename}" es muy grande (máx 16MB)', 'warning')
                            continue
                        
                        # Guardar archivo
                        file_info = save_file_locally(file, incidente.id)
                        
                        if file_info:
                            # Determinar tipo de archivo
                            tipo_archivo = 'imagen' if is_image_file(filename) else 'documento'
                            
                            evidencia = Evidencia(
                                nombre_archivo=file_info['filename'],
                                ruta_local=file_info['filepath'],
                                datos_imagen=file_info['imagen_base64'] if tipo_archivo == 'imagen' else None,
                                tipo_archivo=tipo_archivo,
                                incidente_id=incidente.id
                            )
                            db.session.add(evidencia)
                            uploaded_files.append(filename)
            
            db.session.commit()
            
            # Mensajes de confirmación
            if uploaded_files:
                flash(f'✅ {len(uploaded_files)} archivo(s) subido(s) correctamente', 'success')
            
            flash('✅ Incidente registrado exitosamente!', 'success')
            return redirect(url_for('detalle_incidente', id=incidente.id))
            
        except Exception as e:
            db.session.rollback()
            flash(f'❌ Error al registrar incidente: {str(e)}', 'danger')
            print(f"Error en nuevo_incidente: {e}")
            return redirect(url_for('nuevo_incidente'))
    
    return render_template('nuevo_incidente.html', form=form)

@app.route('/incidente/<int:id>')
def detalle_incidente(id):
    """Detalle de un incidente específico"""
    incidente = Incidente.query.get_or_404(id)
    return render_template('detalle.html', incidente=incidente)

@app.route('/incidente/<int:id>/cambiar-estado', methods=['POST'])
def cambiar_estado(id):
    """Cambia el estado de un incidente"""
    incidente = Incidente.query.get_or_404(id)
    nuevo_estado = request.form.get('estado')
    
    if nuevo_estado in ['Abierto', 'En Investigación', 'Resuelto', 'Cerrado']:
        incidente.estado = nuevo_estado
        db.session.commit()
        flash(f'Estado cambiado a {nuevo_estado}', 'success')
    
    return redirect(url_for('detalle_incidente', id=id))

@app.route('/incidente/<int:id>/galeria')
def galeria_incidente(id):
    """Galería de imágenes de un incidente"""
    incidente = Incidente.query.get_or_404(id)
    imagenes = [ev for ev in incidente.evidencias if ev.tipo_archivo == 'imagen']
    return render_template('galeria.html', incidente=incidente, imagenes=imagenes)

@app.route('/imagen/<int:evidencia_id>')
def vista_imagen(evidencia_id):
    """Vista individual de una evidencia (imagen u otro archivo)"""
    evidencia = Evidencia.query.get_or_404(evidencia_id)
    
    # Verificar si el archivo existe localmente
    if evidencia.ruta_local and not os.path.exists(evidencia.ruta_local):
        flash('❌ El archivo no se encuentra en el servidor', 'danger')
        return redirect(url_for('detalle_incidente', id=evidencia.incidente_id))
    
    return render_template('visor_imagen.html', evidencia=evidencia)

@app.route('/descargar/<int:evidencia_id>')
def descargar_evidencia(evidencia_id):
    """Descarga una evidencia"""
    evidencia = Evidencia.query.get_or_404(evidencia_id)
    
    if evidencia.ruta_local and os.path.exists(evidencia.ruta_local):
        try:
            return send_file(
                evidencia.ruta_local,
                as_attachment=True,
                download_name=evidencia.nombre_archivo
            )
        except Exception as e:
            flash(f'❌ Error descargando archivo: {e}', 'danger')
            return redirect(url_for('detalle_incidente', id=evidencia.incidente_id))
    
    flash('❌ Archivo no encontrado', 'danger')
    return redirect(url_for('detalle_incidente', id=evidencia.incidente_id))

# API endpoints
@app.route('/api/incidentes')
def api_incidentes():
    """API para obtener lista de incidentes"""
    incidentes = Incidente.query.all()
    return jsonify([{
        'id': i.id,
        'titulo': i.titulo,
        'tipo': i.tipo,
        'severidad': i.severidad,
        'estado': i.estado,
        'fecha_creacion': i.fecha_creacion.strftime('%Y-%m-%d %H:%M:%S')
    } for i in incidentes])

@app.route('/api/evidencia/<int:id>')
def api_evidencia(id):
    """API para obtener datos de una evidencia"""
    evidencia = Evidencia.query.get_or_404(id)
    
    # Obtener tamaño del archivo
    tamano = "Desconocido"
    if evidencia.ruta_local and os.path.exists(evidencia.ruta_local):
        tamano_bytes = os.path.getsize(evidencia.ruta_local)
        if tamano_bytes < 1024:
            tamano = f"{tamano_bytes} B"
        elif tamano_bytes < 1024 * 1024:
            tamano = f"{tamano_bytes/1024:.1f} KB"
        else:
            tamano = f"{tamano_bytes/(1024*1024):.1f} MB"
    
    return jsonify({
        'id': evidencia.id,
        'nombre_archivo': evidencia.nombre_archivo,
        'tipo_archivo': evidencia.tipo_archivo,
        'tamano': tamano,
        'fecha_subida': evidencia.fecha_subida.strftime('%Y-%m-%d %H:%M:%S'),
        'incidente_id': evidencia.incidente_id,
        'tiene_imagen': evidencia.datos_imagen is not None
    })

@app.route('/api/evidencia/<int:id>/imagen')
def api_evidencia_imagen(id):
    """API para obtener la imagen base64 de una evidencia"""
    evidencia = Evidencia.query.get_or_404(id)
    
    if evidencia.tipo_archivo != 'imagen':
        return jsonify({'error': 'No es una imagen'}), 400
    
    # Si tenemos datos de imagen en base64
    if evidencia.datos_imagen:
        return jsonify({
            'imagen_base64': evidencia.datos_imagen,
            'nombre_archivo': evidencia.nombre_archivo,
            'tipo_archivo': evidencia.tipo_archivo
        })
    
    # Si no tenemos datos base64 pero tenemos archivo local
    elif evidencia.ruta_local and os.path.exists(evidencia.ruta_local):
        try:
            with open(evidencia.ruta_local, 'rb') as f:
                imagen_bytes = f.read()
                imagen_base64 = base64.b64encode(imagen_bytes).decode('utf-8')
            
            return jsonify({
                'imagen_base64': imagen_base64,
                'nombre_archivo': evidencia.nombre_archivo,
                'tipo_archivo': evidencia.tipo_archivo
            })
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    else:
        return jsonify({'error': 'Imagen no encontrada'}), 404

@app.route('/api/estadisticas')
def api_estadisticas():
    """API para obtener estadísticas"""
    total = Incidente.query.count()
    abiertos = Incidente.query.filter_by(estado='Abierto').count()
    criticos = Incidente.query.filter_by(severidad='critica').count()
    resueltos = Incidente.query.filter_by(estado='Resuelto').count()
    
    return jsonify({
        'total': total,
        'abiertos': abiertos,
        'criticos': criticos,
        'resueltos': resueltos
    })

# Ruta para verificar subida de archivos
@app.route('/api/upload/check', methods=['POST'])
def check_upload():
    """API para verificar archivos antes de subir"""
    if 'files' not in request.files:
        return jsonify({'error': 'No hay archivos'}), 400
    
    files = request.files.getlist('files')
    results = []
    
    for file in files:
        if file and file.filename != '':
            # Verificar tamaño
            max_size = 16 * 1024 * 1024
            file.seek(0, 2)  # Ir al final del archivo
            file_size = file.tell()
            file.seek(0)  # Volver al inicio
            
            is_valid_size = file_size <= max_size
            is_valid_extension = allowed_file(file.filename)
            
            results.append({
                'filename': file.filename,
                'size': file_size,
                'valid_size': is_valid_size,
                'valid_extension': is_valid_extension,
                'status': 'valid' if is_valid_size and is_valid_extension else 'invalid'
            })
    
    return jsonify({'files': results})

@app.route('/status')
def status():
    """Endpoint para verificar el estado del sistema"""
    status_info = {
        'flask': 'running',
        'database': 'connected',
        'uploads_folder': os.path.exists(app.config['UPLOAD_FOLDER']),
        'total_incidentes': Incidente.query.count(),
        'total_evidencias': Evidencia.query.count(),
        'modo': 'desarrollo_local'
    }
    return jsonify(status_info)

# Ruta para eliminar incidente (opcional)
@app.route('/incidente/<int:id>/eliminar', methods=['POST'])
def eliminar_incidente(id):
    incidente = Incidente.query.get_or_404(id)
    
    # Eliminar archivos asociados
    for evidencia in incidente.evidencias:
        if evidencia.ruta_local and os.path.exists(evidencia.ruta_local):
            try:
                os.remove(evidencia.ruta_local)
            except:
                pass
    
    # Eliminar de la base de datos
    db.session.delete(incidente)
    db.session.commit()
    
    flash('Incidente eliminado correctamente', 'success')
    return redirect(url_for('listar_incidentes'))

# Ruta para eliminar evidencia (opcional)
@app.route('/evidencia/<int:id>/eliminar', methods=['POST'])
def eliminar_evidencia(id):
    evidencia = Evidencia.query.get_or_404(id)
    incidente_id = evidencia.incidente_id
    
    # Eliminar archivo físico
    if evidencia.ruta_local and os.path.exists(evidencia.ruta_local):
        try:
            os.remove(evidencia.ruta_local)
        except:
            pass
    
    # Eliminar de la base de datos
    db.session.delete(evidencia)
    db.session.commit()
    
    flash('Evidencia eliminada correctamente', 'success')
    return redirect(url_for('detalle_incidente', id=incidente_id))

# Ruta para limpiar archivos temporales
@app.route('/limpiar-sesion')
def limpiar_sesion():
    """Limpia los archivos de sesión"""
    if 'uploaded_files' in session:
        session.pop('uploaded_files')
    flash('Sesión limpiada correctamente', 'info')
    return redirect(url_for('index'))

# Inicializar base de datos
def init_db():
    with app.app_context():
        db.create_all()
        print("✅ Base de datos SQLite inicializada en: cyberincident.db")
        
        # Crear datos de prueba si la base de datos está vacía
        if Incidente.query.count() == 0:
            print("📝 Creando datos de prueba...")
            
            # Crear algunos incidentes de prueba
            incidentes_prueba = [
                Incidente(
                    titulo="Intento de phishing detectado",
                    descripcion="Se recibieron correos sospechosos solicitando credenciales",
                    tipo="phishing",
                    severidad="media",
                    usuario_reporta="admin",
                    estado="Abierto"
                ),
                Incidente(
                    titulo="Servidor web comprometido",
                    descripcion="Se detectó actividad inusual en el servidor web principal",
                    tipo="intrusion",
                    severidad="alta",
                    usuario_reporta="soporte",
                    estado="En Investigación"
                ),
                Incidente(
                    titulo="Malware en estación de trabajo",
                    descripcion="Antivirus detectó troyano en equipo de usuario",
                    tipo="malware",
                    severidad="critica",
                    usuario_reporta="usuario123",
                    estado="Resuelto"
                )
            ]
            
            for incidente in incidentes_prueba:
                db.session.add(incidente)
            
            db.session.commit()
            print("✅ Datos de prueba creados")

# Manejo de errores
@app.errorhandler(404)
def pagina_no_encontrada(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def error_servidor(e):
    return render_template('500.html'), 500

@app.errorhandler(413)
def too_large(e):
    flash('❌ El archivo es demasiado grande. Máximo 16MB por archivo.', 'danger')
    return redirect(request.referrer or url_for('nuevo_incidente'))

if __name__ == '__main__':
    # Inicializar base de datos
    init_db()
    
    print("\n" + "="*50)
    print("🚀 CYBERINCIDENT - Sistema de Gestión de Incidentes")
    print("="*50)
    print(f" Base de datos: sqlite:///cyberincident.db")
    print(f" Carpeta uploads: {app.config['UPLOAD_FOLDER']}")
    print(f"🔗 Acceso local: http://127.0.0.1:5000")
    print(f"📊 Estado: http://127.0.0.1:5000/status")
    print("="*50 + "\n")
    
    app.run(host='127.0.0.1', port=5000, debug=True)
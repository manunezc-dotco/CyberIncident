from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os

# Inicializar Flask
app = Flask(__name__)
app.config['SECRET_KEY'] = 'clave-secreta-temporal-para-desarrollo'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///incidentes.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Inicializar base de datos
db = SQLAlchemy(app)

# Modelo de Incidente
class Incidente(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(200), nullable=False)
    descripcion = db.Column(db.Text, nullable=False)
    tipo = db.Column(db.String(50), nullable=False)
    severidad = db.Column(db.String(20), nullable=False)
    estado = db.Column(db.String(20), default='Abierto')
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    usuario_reporta = db.Column(db.String(100), default='Anónimo')

# Crear tablas
with app.app_context():
    db.create_all()

# Ruta principal
@app.route('/')
def index():
    return render_template('index.html')

# Ruta para listar incidentes
@app.route('/incidentes')
def listar_incidentes():
    incidentes = Incidente.query.order_by(Incidente.fecha_creacion.desc()).all()
    return render_template('incidentes.html', incidentes=incidentes)

# Ruta para nuevo incidente
@app.route('/incidente/nuevo', methods=['GET', 'POST'])
def nuevo_incidente():
    if request.method == 'POST':
        # Crear nuevo incidente
        incidente = Incidente(
            titulo=request.form['titulo'],
            descripcion=request.form['descripcion'],
            tipo=request.form['tipo'],
            severidad=request.form['severidad'],
            usuario_reporta=request.form.get('usuario_reporta', 'Anónimo')
        )
        
        db.session.add(incidente)
        db.session.commit()
        
        flash('✅ Incidente registrado exitosamente!', 'success')
        return redirect(url_for('listar_incidentes'))
    
    return render_template('nuevo_incidente.html')

# Ruta para ver detalle
@app.route('/incidente/<int:id>')
def detalle_incidente(id):
    incidente = Incidente.query.get_or_404(id)
    return render_template('detalle.html', incidente=incidente)

# Ruta para cambiar estado
@app.route('/incidente/<int:id>/cambiar-estado', methods=['POST'])
def cambiar_estado(id):
    incidente = Incidente.query.get_or_404(id)
    nuevo_estado = request.form.get('estado')
    
    if nuevo_estado in ['Abierto', 'En Investigación', 'Resuelto', 'Cerrado']:
        incidente.estado = nuevo_estado
        db.session.commit()
        flash(f'Estado cambiado a {nuevo_estado}', 'success')
    
    return redirect(url_for('detalle_incidente', id=id))

if __name__ == '__main__':
    print("🚀 Servidor CyberIncident iniciando...")
    print("📌 Disponible en: http://localhost:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)
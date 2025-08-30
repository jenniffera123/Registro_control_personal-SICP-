from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

db = SQLAlchemy()

class Usuario(db.Model,UserMixin):
    id=db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)
    rol = db.Column(db.String(50), nullable=False, default='usuario') 
    
    def __repr__(self):
        return f'<Usuario {self.id} | {self.nombre} | {self.email} | {self.rol}>'

    
# Modelo para manejar datos del personal militar
class Personal(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombres = db.Column(db.LargeBinary)
    apellidos = db.Column(db.LargeBinary)
    identificacion = db.Column(db.LargeBinary)
    rango = db.Column(db.LargeBinary)
    unidad = db.Column(db.LargeBinary)
    areaVisita = db.Column(db.LargeBinary)
    propositoVisita = db.Column(db.LargeBinary)
    fecha_hora = db.Column(db.LargeBinary, nullable=False)
    codigo_verificacion = db.Column(db.LargeBinary)
    # Archivos: Firma Digital e Imagen
    firma_digital = db.Column(db.String(100), nullable=True)
    imagen = db.Column(db.String(100), nullable=True) 
    def __repr__(self):
        return f'<Personal {self.nombres}>'
    
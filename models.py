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

class Rango(db.Model):
    __tablename__ = 'rango'
    
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False, unique=True) 
    categoria = db.Column(db.String(50), nullable=False) 

    def __repr__(self):
        return f"<Rango {self.nombre} - {self.categoria}>"
    
class Unidad(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False, unique=True)
    
# Modelo para manejar datos del personal militar
class Personal(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombres = db.Column(db.LargeBinary)
    apellidos = db.Column(db.LargeBinary)
    identificacion = db.Column(db.LargeBinary)
    rango_id = db.Column(db.Integer, db.ForeignKey('rango.id'), nullable=False)
    rango = db.relationship('Rango', backref=db.backref('personales_rango', lazy=True))
    unidad_id = db.Column(db.Integer, db.ForeignKey('unidad.id'), nullable=False)
    unidad = db.relationship('Unidad', backref=db.backref('personales_unidad', lazy=True))
    #unidad = db.Column(db.LargeBinary)
    areaVisita = db.Column(db.LargeBinary)
    propositoVisita = db.Column(db.LargeBinary)
    fecha_hora = db.Column(db.LargeBinary, nullable=False)
    codigo_verificacion = db.Column(db.LargeBinary)
    # Archivos: Firma Digital e Imagen
    firma_digital = db.Column(db.String(100), nullable=True)
    imagen = db.Column(db.String(100), nullable=True) 
    def __repr__(self):
        return f'<Personal {self.nombres}>'
    
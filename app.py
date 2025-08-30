from functools import wraps
import os
import secrets
import string
from dotenv import load_dotenv
from flask import Flask, abort, flash, redirect, render_template, request, url_for
from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager,login_user,logout_user,login_required,current_user
from models import Personal, db,Usuario
from cryptography.fernet import Fernet
import re 
load_dotenv()
app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///usuarios.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Clave de cifrado (usa Fernet.generate_key())
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
FERNET_KEY = os.environ.get('FERNET_KEY').encode()
fernet = Fernet(FERNET_KEY)

db.init_app(app)
bcrypt= Bcrypt(app)
login_manager=LoginManager(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return Usuario.query.get(int(user_id))

@app.before_request
def crear_bd():
    db.create_all()

#Se crea un decorador propio para limitar acceso a algunas funcionalidades
def isAdmin(f):
    @wraps(f)
    def decorade(*args,**kwargs):
        #Si el usuario logueado no es de tipo admin se niega el acceso al modulo
        if not current_user.is_authenticated or current_user.rol != 'admin':
            abort(403)
        return f(*args, **kwargs)
    return decorade

@app.route('/')
def inicio():
    return render_template('login.html')
@app.route('/home')
def home():
    return render_template('home.html')
#funcion para validar que la contrase;a 
# elegida por el usuario cumpla con algunas condiciones
def validar_password(password):
    #validar que la contraseña ingresada cumpla con el tamaño requerido
    if len(password) < 8:
        return 'La contraseña debe contener como minimo 8 caracteres'
    
    #validar que contenga al menos una letra en mayuscula
    if not re.search(r'[A-Z]', password):
        return "La contraseña debe incluir al menos una letra mayúscula"
    
    #validar que contenga al menos un número
    if not re.search(r'[0-9]',password):
        return "La contraseña ingresada debe contener un número al menos"
    
    #validar que contenga por lo menos un caracter especial
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):  # Al menos un carácter especial
        return "La contraseña debe incluir al menos un carácter especial (!@#$%^&*)."
    
    return None
    

# Login de usuarios
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # lógica de login
        email =  request.form.get('email')
        password = request.form['password']
        usuario = Usuario.query.filter_by(email=email).first()
        # validación de usuario y contraseña
        if usuario and bcrypt.check_password_hash(usuario.password,password):
            login_user(usuario)
            flash('se ha iniciado sesión', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Los datos ingresados estan erroneos por favor valide e ingrese de nuevo','danger')    
    return render_template('login.html')

# deslogueo de usuarios
@app.route('/logOut', methods=['GET', 'POST'])
def logOut():
    logout_user()
    flash('Sesión Cerrada','info')
    return redirect(url_for('login'))

# Registro de usuarios
@app.route('/registro', methods=['GET', 'POST'])
def registro():
    if request.method == 'POST':
        # lógica de registro
        nombre = request.form['nombre']
        email = request.form['email']
        password = request.form.get('password')
        # Validamos la contraseña
        error = validar_password(password)
        if error:
            flash(error, 'danger')
            return redirect(url_for('registro'))
        
        #Se hashea la contrase;a usando hash Bcrypt
        password = bcrypt.generate_password_hash(request.form['password']).decode('utf-8')
        #Asignamos un rol por default
        rol = request.form.get('rol','usuario')
        # validación de correo ya registrado
        if Usuario.query.filter_by(email=email).first():
            flash('Este correo ya se encuentra registrado','danger')
            return redirect(url_for('registro'))
        nuevo_usuario=Usuario(nombre=nombre,email=email,password=password,rol=rol)
        db.session.add(nuevo_usuario)
        db.session.commit()
        flash('Registro exitoso', 'success')
        return redirect(url_for('dashboard'))
    return render_template('registro.html')

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html',current_user=current_user.nombre)

# registro de personala
@app.route('/personal', methods=['GET', 'POST'])
@login_required
def personal():
    if request.method == 'POST':
        nombreI=request.form.get('nombreI')
        apellidos=request.form.get('apellidos')
        identificacion=request.form.get('identificacion')
        gradoRango=request.form.get('grado-rango')
        unidad=request.form.get('unidad')
        areaVisita=request.form.get('areaVisita')
        propositoVisita=request.form.get('propositoVisita')
        fechaHora=request.form.get('fechaHora')
        # Código único generado aleatoriamente
        codigo =  generar_codigo_seguro()
        # paso para cifrar los datos
        nombre_m = fernet.encrypt(nombreI.encode())
        apellidos_m = fernet.encrypt(apellidos.encode())
        identi_m = fernet.encrypt(identificacion.encode())
        rango_m = fernet.encrypt(gradoRango.encode())
        unidad_m = fernet.encrypt(unidad.encode())
        areaVisita_m = fernet.encrypt(areaVisita.encode())
        propositoVisita_m = fernet.encrypt(propositoVisita.encode())
        fechaHora_m = fernet.encrypt(fechaHora.encode())
        codigo_m = fernet.encrypt(codigo.encode())

        # Creación de objeto
        nuevo_personal = Personal(
            nombres=nombre_m,
            apellidos=apellidos_m,
            identificacion=identi_m,
            rango=rango_m,
            unidad=unidad_m,
            areaVisita=areaVisita_m,
            propositoVisita=propositoVisita_m,
            fecha_hora=fechaHora_m,
            codigo_verificacion = codigo_m
        )
        # Guardar en la base de datos
        db.session.add(nuevo_personal)
        db.session.commit()

        flash(f'Personal registrado con código: {codigo} ,{identi_m}' , 'success')
        return render_template('registro-personal.html', codigo_generado=codigo)

    return render_template('registro-personal.html')

# Validar identidad
@app.route('/validar-identidad', methods=['GET', 'POST'])
@login_required
def validacion_Identidad():
    datos_desc = []
    proposito = None
    codigo_unico = None

    if request.method == 'POST':
        accion = request.form.get('accion')
        codigo_unico = request.form.get('codigoUnico') or request.form.get('codigo')
        cedula_I = request.form.get('identificacion')

        personal = Personal.query.all()
        persona_validada = None

        for p in personal:
            try:
                codigo_db = fernet.decrypt(p.codigo_verificacion).decode()

                # Validación por identidad
                if accion == 'identidad':
                    cedula_db = fernet.decrypt(p.identificacion).decode()
                    if cedula_I == cedula_db and codigo_unico == codigo_db:
                        persona_validada = p
                        break

                elif accion == 'proposito':
                    if current_user.rol == 'admin':
                        if codigo_unico == codigo_db:
                            persona_validada = p
                            break
                    else:
                        return redirect(url_for('home'))                        
            except Exception:
                continue

        if not persona_validada:
            flash('Verificación fallida. Datos incorrectos.', 'danger')
            return redirect(url_for('validacion_Identidad'))

        try:
            # Desencriptar datos para mostrar en la tabla
            datos_desc.append({
                'id': persona_validada.id,
                'nombre': fernet.decrypt(persona_validada.nombres).decode(),
                'apellidos': fernet.decrypt(persona_validada.apellidos).decode(),
                'identificacion': fernet.decrypt(persona_validada.identificacion).decode(),
                'unidad': fernet.decrypt(persona_validada.unidad).decode(),
                'proposito': fernet.decrypt(persona_validada.propositoVisita).decode(),
                'fecha_hora': fernet.decrypt(persona_validada.fecha_hora).decode()
            })

            if accion == 'identidad':
                flash('Identidad verificada correctamente.', 'success')

            elif accion == 'proposito':
                proposito = datos_desc[0]['proposito']
                flash('Propósito validado.', 'info')

        except Exception as e:
            flash('Error al desencriptar los datos.', 'danger')
            print("Error:", e)

        return render_template('validar-identidad.html',personalM=datos_desc,
                               proposito=proposito,codigo=codigo_unico)
    return render_template('validar-identidad.html')

@app.route('/gestion-admin',methods=['POST','GET'])
@isAdmin
@login_required
def gestion_admin():
    usuarios_list =Usuario.query.all()
    return render_template('gestion-admin.html',usuarios = usuarios_list)

@app.route('/editar-usuario/<int:id>', methods=['GET', 'POST'])
@isAdmin
@login_required
def editar_usuario(id):
    usuario = Usuario.query.get(id)
    
    if request.method == 'POST':
        nuevo_rol = request.form.get('rol')
        if nuevo_rol: 
            usuario.rol = nuevo_rol
            db.session.commit()
            flash('Rol actualizado con éxito', 'success')
            return redirect(url_for('gestion_admin'))
        else:
            flash('Debe seleccionar un rol válido', 'danger')
    
    return render_template('editar-usuario.html', usuario=usuario)

@app.route('/editar-contrasena/<int:id>', methods=['GET', 'POST'])
@isAdmin
@login_required
def editar_contrasena(id):
    usuario = Usuario.query.get(id)
    if request.method == 'POST':
        nuevo_cotraseña = request.form.get('password')
        if nuevo_cotraseña:
            # Validamos la contraseña
            error = validar_password(nuevo_cotraseña)
            if error:
                flash(error, 'danger')
            else:
                #Se hashea la contrase;a usando hash Bcrypt
                password = bcrypt.generate_password_hash(nuevo_cotraseña).decode('utf-8')
                usuario.password = password
                db.session.commit()
                flash('Se ha actualizado su contraseña', 'success')
                return redirect(url_for('gestion_admin'))
        else:
            flash('Debe ingresar una nueva contraseña', 'danger')    
        
    return render_template('editar-contrasena.html', usuario=usuario)
 
def generar_codigo_seguro(longitud=16):
    caracteres = string.ascii_letters + string.digits
    return ''.join(secrets.choice(caracteres) for _ in range(longitud))

if __name__ == '__main__':
    app.run(debug=True)

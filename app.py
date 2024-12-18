from flask import Flask, render_template, redirect, url_for, request, flash, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from helpers import login_required, cargar_pokemon, cargar_equipo, guardar_equipo
import pandas as pd
import re

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SECRET_KEY'] = 'your_secret_key'
db = SQLAlchemy(app)

# Cargar los datos del CSV
df = pd.read_csv('pokemon.csv')

# User model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(50), nullable=False)
    entrenador = db.Column(db.String(50), nullable=False)

def contraseña_valida(password):
    if len(password) < 8:
        return False
    if not re.search("[a-z]", password):
        return False
    if not re.search("[A-Z]", password):
        return False
    if not re.search("[0-9]", password):
        return False
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        return False
    return True

def validar_mail(username):
    # Expresion regular para validar el formato del mail
    regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    return re.match(regex, username) is not None

# Home route
@app.route('/')

def home():
    entrenador = None
    if 'user_id' in session:
        user = db.session.get(User, session['user_id'])
        entrenador = user.entrenador if user else None
    return render_template('home.html', entrenador=entrenador)

# Registration route
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        entrenador = request.form['entrenador']
        # Validar mail
        if not validar_mail(username):
            flash('El correo electrónico no es válido.')
            return render_template('register.html', username=username, password=password)
            
        # Validar la contraseña
        if not contraseña_valida(password):
            flash('La contraseña debe tener al menos 8 caracteres, incluyendo al menos 1 mayúscula, 1 numero y 1 carácter especial.')
            return render_template('register.html', username=username, password=password)

        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
        
        # Verificar si el usuario ya existe
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash('El usuario ya existe. Por favor, elija otro nombre de usuario.')
            return render_template('register.html', username=username)
        
        new_user = User(username=username, password=hashed_password, entrenador=entrenador)
        db.session.add(new_user)
        db.session.commit()
        flash('Registro completo. Por favor inicie sesion.')
        return redirect(url_for('login'))
    return render_template('register.html')

# Login route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            flash('Inicio de sesión exitoso.')
            return redirect(url_for('home'))
        else:
            flash('Error al iniciar sesión. Verifique su nombre de usuario y/o contraseña.')
    return render_template('login.html')

# Logout route
@app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash('Cerraste sesion con exito.')
    return redirect(url_for('home'))

@app.route('/actualizar-entrenador', methods=['GET', 'POST'])
@login_required
def actualizar_entrenador():
    if request.method == 'POST':
        nuevo_entrenador = request.form['entrenador']
        user = db.session.get(User, session['user_id'])

        if user:
            user.entrenador = nuevo_entrenador
            db.session.commit()
            flash('Información del entrenador actualizada con éxito.')
            return redirect(url_for('home'))

    return render_template('actualizar_entrenador.html')

@app.route('/eliminar-cuenta', methods=['GET', 'POST'])
@login_required
def eliminar_cuenta():
    user = db.session.get(User, session['user_id'])
    session.pop('user_id', None)
    db.session.delete(user)
    db.session.commit()
    
    flash('Eliminaste tu cuenta con exito.')
    return redirect(url_for('home'))

@app.route('/pokedex', methods=['GET', 'POST'])
def pokedex():
    if request.method == 'POST':
        tipo = request.form.get('tipo')
        if tipo:
            pokedex = filtrar_pokemon_por_tipo(tipo)
        else:
            pokedex = cargar_pokemon('pokemon.csv')
    else:
        pokedex = cargar_pokemon('pokemon.csv')
    return render_template('pokedex.html', pokedex=pokedex)

def filtrar_pokemon_por_tipo(tipo):
    todos_pokemon = cargar_pokemon('pokemon.csv')
    pokemon_filtrados = [pokemon for pokemon in todos_pokemon if tipo in (pokemon['tipo1'], pokemon['tipo2'])]
    return pokemon_filtrados

# Mi equipo Actual
@app.route('/mi-equipo')
@login_required
def mi_equipo():
    equipo_pokemon = []
    todos_pokemon = cargar_pokemon('pokemon.csv')
    equipo_usuario = cargar_equipo('equipos.csv', session['user_id'])

    if len(equipo_usuario) > 0:
        for pokemon in equipo_usuario:
            pokemon_data = [element for element in todos_pokemon if element['id'] == pokemon['id']]

            if pokemon_data:
                equipo_pokemon.append({
                    'id': pokemon_data[0]["id"],
                    'nombre': pokemon_data[0]["nombre"],
                    'tipo1': pokemon_data[0]["tipo1"],
                    'tipo2': pokemon_data[0]["tipo2"],
                    'ataque': pokemon_data[0]["ataque"],
                    'defensa': pokemon_data[0]["defensa"],
                    'hp': pokemon_data[0]["hp"],
                    'peso': pokemon_data[0]["peso"],
                    'altura': pokemon_data[0]["altura"],
                    'clasificacion': pokemon_data[0]["clasificacion"],
                    'debilidades': pokemon_data[0]["debilidades"],
                    'imagen': f"https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/{pokemon_data[0]['id']}.png"
                })
            else:
                print(f'Pokemon con ID {pokemon['id']} no encontrado en todos los Pokemon')

    return render_template("mi_equipo.html", pokemon=todos_pokemon, equipo=equipo_pokemon)

@app.route('/agregar-pokemon', methods=['POST'])
@login_required
def agregar_pokemon():
    pokemon_id = int(request.form.get("pokemon_id"))
    apodo = request.form.get("apodo")
    
    equipo_usuario = cargar_equipo('equipos.csv', session['user_id'])
    
    # Verificar si el equipo ya tiene 6 Pokémon
    if len(equipo_usuario) >= 7:
        flash("Tu equipo ya está completo")
        return redirect("/mi-equipo")
    
    # Verificar si el Pokémon ya está en el equipo
    for pokemon in equipo_usuario:
        if int(pokemon['id']) == pokemon_id:
            flash("Este Pokémon ya está en tu equipo.")
            return redirect("/mi-equipo")
    
    # Si no hay duplicados, añadir el nuevo Pokémon
    nuevo_pokemon = {"id": pokemon_id}
    equipo_usuario.append(nuevo_pokemon)
    guardar_equipo('equipos.csv', session['user_id'], equipo_usuario)
    flash("Pokémon añadido con exito.")
    
    return redirect("/mi-equipo")

@app.route('/eliminar-pokemon', methods=['POST'])
@login_required
def eliminar_pokemon():
	pokemon_id = int(request.form.get("pokemon_id"))
	equipo_usuario = cargar_equipo('equipos.csv', session['user_id'])
	equipo_usuario = [p for p in equipo_usuario if p['id'] != pokemon_id]
	guardar_equipo('equipos.csv', session['user_id'], equipo_usuario)
	
	flash("Pokémon removido del equipo con exito.")
	
	return redirect("/mi-equipo")

if __name__ == '__main__':
	with app.app_context():
		db.create_all()
	app.run(debug=True)
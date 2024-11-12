from flask import Flask, render_template, redirect, url_for, request, flash, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from helpers import login_required, cargar_pokemon, cargar_equipo, guardar_equipo
import pandas as pd

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SECRET_KEY'] = 'your_secret_key'
db = SQLAlchemy(app)

# Cargar los datos del CSV
df = pd.read_csv('pokemon.csv')

# User model
class User(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	username = db.Column(db.String(150), unique=True, nullable=False)
	password = db.Column(db.String(150), nullable=False)

# Home route
@app.route('/')
def home():
	username = None
	if 'user_id' in session:
		user = db.session.get(User, session['user_id'])
		username = user.username if user else None
	return render_template('home.html', username=username)

# Registration route
@app.route('/register', methods=['GET', 'POST'])
def register():
	if request.method == 'POST':
		username = request.form['username']
		password = request.form['password']
		hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
		
		# Verificar si el usuario ya existe
		existing_user = User.query.filter_by(username=username).first()
		if existing_user:
			flash('Username already exists. Please choose a different one.')
			return redirect(url_for('register'))
		
		new_user = User(username=username, password=hashed_password)
		db.session.add(new_user)
		db.session.commit()
		flash('Registration successful! Please log in.')
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
			flash('Login successful!')
			return redirect(url_for('pokedex'))
		else:
			flash('Login failed. Check your username and/or password.')
	return render_template('login.html')

# Logout route
@app.route('/logout')
def logout():
	session.pop('user_id', None)
	flash('You have been logged out.')
	return redirect(url_for('home'))

# Pokédex route
@app.route('/pokedex')
def pokedex():
	pokedex = cargar_pokemon('pokemon.csv')
	return render_template('pokedex.html', pokedex=pokedex)

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
			equipo_pokemon.append({
				'id': pokemon_data[0]["id"],
				'nombre': pokemon_data[0]["nombre"],
				'apodo': pokemon["apodo"],
				'tipo1': pokemon_data[0]["tipo1"],
				'tipo2': pokemon_data[0]["tipo2"],
				'imagen': f"https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/{pokemon_data[0]['id']}.png"
			})
	
	return render_template("mi_equipo.html", pokemon=todos_pokemon, equipo=equipo_pokemon)

@app.route('/agregar-pokemon', methods=['POST'])
@login_required
def agregar_pokemon():
	pokemon_id = request.form.get("pokemon_id")
	apodo = request.form.get("apodo")
	
	equipo_usuario = cargar_equipo('equipos.csv', session['user_id'])
	
	if len(equipo_usuario) >= 6:
		flash("Tu equipo ya está completo")
	else:
		nuevo_pokemon = {"id": pokemon_id, "apodo": apodo}
		equipo_usuario.append(nuevo_pokemon)
		guardar_equipo('equipos.csv', session['user_id'], equipo_usuario)
		flash("Pokémon successfully added")
	
	return redirect("/mi-equipo")

@app.route('/eliminar-pokemon', methods=['POST'])
@login_required
def eliminar_pokemon():
	pokemon_id = int(request.form.get("pokemon_id"))
	equipo_usuario = cargar_equipo('equipos.csv', session['user_id'])
	equipo_usuario = [p for p in equipo_usuario if p['id'] != pokemon_id]
	guardar_equipo('equipos.csv', session['user_id'], equipo_usuario)
	
	flash("Pokémon removed from the team.")
	
	return redirect("/mi-equipo")

if __name__ == '__main__':
	with app.app_context():
		db.create_all()
	app.run(debug=True)
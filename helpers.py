import csv
from functools import wraps
from flask import session, redirect
import os


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function

def cargar_pokemon(archivo_csv):
    pokemon = []
    with open(archivo_csv, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            try:
                pokemon.append({
                    'id': int(row['pokedex_number']),
                    'nombre': row['name'],
                    'tipo1': row['type1'],
                    'tipo2': row['type2'] if row['type2'] else None,
                    'hp': int(row['hp']),
                    'ataque': int(row['attack']),
                    'defensa': int(row['defense']),
                    'ataque_especial': int(row['sp_attack']),
                    'defensa_especial': int(row['sp_defense']),
                    'velocidad': int(row['speed']),
                    'generacion': int(row['generation']),
                    'legendario': bool(int(row['is_legendary'])),
                    'altura': float(row['height_m']) if row['height_m'] else None,
                    'peso': float(row['weight_kg']) if row['weight_kg'] else None,
                    'habilidades': row['abilities'].strip("[]").replace("'", "").split(', ') if row['abilities'] else [],
                    'clasificacion': row['classfication'],
                    'tasa_captura': int(row['capture_rate']),
                    'experiencia_base': int(row['base_total'])
                })
            except KeyError as e:
                print(f"Error: Falta la columna {e} en el archivo CSV.")
            except ValueError as e:
                print(f"Error al convertir un valor: {e}. Fila: {row}")
    return pokemon


def cargar_equipo(archivo_csv, user_id):
    if not os.path.exists(archivo_csv):
        # Crea el archivo con un encabezado si no existe
        with open(archivo_csv, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['user_id', 'pokemon_id', 'apodo'])
        return []  # Retorna una lista vacía ya que el archivo estaba vacío

    equipo = []
    try:
        with open(archivo_csv, newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                if int(row['user_id']) == user_id:
                    equipo.append({
                        'id': int(row['pokemon_id']),
                        'apodo': row['apodo']
                    })
    except IOError as e:
        print(f"Error al abrir el archivo: {e}")
    except Exception as e:
        print(f"Error inesperado: {e}")

    return equipo

def guardar_equipo(archivo_csv, user_id, equipo):
    # Primero, leemos todos los equipos existentes
    todos_equipos = []
    with open(archivo_csv, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            if row['user_id'] != str(user_id):
                todos_equipos.append(row)
    
    # Luego, agregamos el equipo actualizado del usuario
    for pokemon in equipo:
        todos_equipos.append({
            'user_id': str(user_id),
            'pokemon_id': pokemon['id'],
            'apodo': pokemon['apodo']
        })
    
    # Finalmente, escribimos todo de vuelta al archivo
    fieldnames = ['user_id', 'pokemon_id', 'apodo']
    with open(archivo_csv, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for row in todos_equipos:
            writer.writerow(row)
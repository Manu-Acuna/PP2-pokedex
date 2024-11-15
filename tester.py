import unittest
from app import app, db, User
from flask import session
import os

class FlaskTestCase(unittest.TestCase):
    
    # Configuración de la aplicación para pruebas
    def setUp(self):
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.client = app.test_client()
        with app.app_context():
            db.create_all()

    def tearDown(self):
        with app.app_context():
            db.session.remove()
            db.drop_all()
    
    def test_user_registration(self):
        # Prueba de registro exitoso
        response = self.client.post('/register', data=dict(username="testuser", password="testpass"))
        self.assertEqual(response.status_code, 302)  # Redirección después de registro exitoso
        self.assertIsNotNone(User.query.filter_by(username="testuser").first())

    def test_duplicate_user_registration(self):
        # Prueba de usuario duplicado
        self.client.post('/register', data=dict(username="testuser", password="testpass"))
        response = self.client.post('/register', data=dict(username="testuser", password="testpass"))
        self.assertIn(f'El usuario ya existe.', response.data)

    def test_login_success(self):
        # Prueba de inicio de sesión exitoso
        self.client.post('/register', data=dict(username="testuser", password="testpass"))
        response = self.client.post('/login', data=dict(username="testuser", password="testpass"))
        with self.client.session_transaction() as sess:
            self.assertIn('user_id', sess)

    def test_login_failure(self):
        # Prueba de error en inicio de sesión
        response = self.client.post('/login', data=dict(username="wronguser", password="wrongpass"))
        self.assertIn(f'Error al iniciar sesi', response.data)  # Verifica el mensaje de error en la página

    def test_login_redirect(self):
        # Prueba de redirección después de inicio de sesión
        self.client.post('/register', data=dict(username="testuser", password="testpass"))
        response = self.client.post('/login', data=dict(username="testuser", password="testpass"), follow_redirects=True)
        self.assertIn(f'Pokedex', response.data)  # Comprueba si se muestra la página de Pokédex

    def test_logout(self):
        # Prueba de cierre de sesión
        self.client.post('/register', data=dict(username="testuser", password="testpass"))
        self.client.post('/login', data=dict(username="testuser", password="testpass"))
        response = self.client.get('/logout', follow_redirects=True)
        with self.client.session_transaction() as sess:
            self.assertNotIn('user_id', sess)
        self.assertIn(f'Cerraste sesion con exito.', response.data)

    def test_pokedex_loading(self):
        # Prueba de carga de Pokédex
        response = self.client.get('/pokedex')
        self.assertEqual(response.status_code, 200)
        self.assertIn(f'Pokemon', response.data)

    def test_add_pokemon_to_team(self):
        # Prueba de agregar un Pokémon al equipo
        with self.client.session_transaction() as sess:
            sess['user_id'] = 1
        response = self.client.post('/agregar-pokemon', data=dict(pokemon_id=1, apodo="Pika"))
        self.assertIn(f'Pokemon añadido con exito.', response.data)

    def test_team_full(self):
        # Prueba de equipo completo
        with self.client.session_transaction() as sess:
            sess['user_id'] = 1
        for i in range(6):
            self.client.post('/agregar-pokemon', data=dict(pokemon_id=i, apodo=f"Pika{i}"))
        response = self.client.post('/agregar-pokemon', data=dict(pokemon_id=7, apodo="Pika7"))
        self.assertIn(f'Tu equipo ya está completo', response.data)

    def test_remove_pokemon_from_team(self):
        # Prueba de eliminación de Pokémon
        with self.client.session_transaction() as sess:
            sess['user_id'] = 1
        self.client.post('/agregar-pokemon', data=dict(pokemon_id=1, apodo="Pika"))
        response = self.client.post('/eliminar-pokemon', data=dict(pokemon_id=1))
        self.assertIn(f'Pokémon removido del equipo con exito.', response.data)

if __name__ == '__main__':
    unittest.main()

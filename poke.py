import unittest
from app import app

class PokedexViewTestCase(unittest.TestCase):

    # Configuración para pruebas
    def setUp(self):
        app.config['TESTING'] = True
        self.client = app.test_client()

    def test_pokedex_page_loads(self):
        # Prueba de carga de la página Pokédex
        response = self.client.get('/pokedex')
        self.assertEqual(response.status_code, 200)
        self.assertIn(f'Lista Pok\xc3\xa9mon', response.data)  # Verifica que el título esté presente en la página

    def test_pokemon_cards_display(self):
        # Prueba de que las tarjetas de Pokémon se muestran correctamente
        response = self.client.get('/pokedex')
        self.assertIn(f'pokemon-card', response.data)  # Verifica que las tarjetas de Pokémon tengan la clase esperada

    def test_type_badges(self):
        # Prueba de que las insignias de tipo de Pokémon se muestran
        response = self.client.get('/pokedex')
        self.assertIn(f'type-badge', response.data)  # Asegura que la insignia de tipo está presente

    def test_add_to_team_button(self):
        # Prueba de que el botón "Agregar al equipo" está presente
        response = self.client.get('/pokedex')
        self.assertIn(f'Agregar al equipo', response.data)  # Comprueba la presencia del botón

    def test_back_to_top_button(self):
        # Prueba de que el botón "Subir" está presente y es funcional
        response = self.client.get('/pokedex')
        self.assertIn(f'Subir', response.data)  # Verifica que el botón de volver arriba está presente

    def test_flash_messages_display(self):
        # Prueba de mensajes flash en la Pokédex
        with self.client.session_transaction() as session:
            session['_flashes'] = [('info', 'Mensaje de prueba')]
        response = self.client.get('/pokedex')
        self.assertIn(f'Mensaje de prueba', response.data)  # Comprueba que el mensaje flash se muestra

    def test_add_pokemon_form(self):
        # Prueba de que el formulario para agregar Pokémon tiene los elementos necesarios
        response = self.client.get('/pokedex')
        self.assertIn(f'<form action="/agregar-pokemon" method="post">', response.data)
        self.assertIn(f'<input class="form-control" type="text" name="apodo" id="apodo">', response.data)
        self.assertIn(f'<input type="hidden" name="pokemon_id"', response.data)  # Verifica que el ID esté presente

    def test_pokemon_image_display(self):
        # Prueba de que las imágenes de los Pokémon se cargan correctamente
        response = self.client.get('/pokedex')
        self.assertIn(f'pokemon-image', response.data)  # Verifica que la imagen tenga la clase correcta
        self.assertIn(f'https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/', response.data)  # URL de la imagen

    def test_pokedex_page_contains_bootstrap(self):
        # Prueba de que la página incluye Bootstrap
        response = self.client.get('/pokedex')
        self.assertIn(f'bootstrap.min.css', response.data)  # Verifica la presencia de Bootstrap

    def test_external_stylesheets_linked(self):
        # Prueba de que los estilos externos están vinculados
        response = self.client.get('/pokedex')
        self.assertIn(f'styles.css', response.data)
        self.assertIn(f'tipos.css', response.data)

if __name__ == '__main__':
    unittest.main()

from fastapi.testclient import TestClient
from map import app  # Asegúrate de que 'main' es el nombre del archivo donde está tu microservicio

client = TestClient(app)

def test_search_pokemon_card():
    response = client.get("/cards", params={"name": "Pikachu"})
    assert response.status_code == 200
    data = response.json()
    assert "data" in data  # Verifica que la respuesta contiene la clave "data"
    assert isinstance(data["data"], list)  # La respuesta debe ser una lista de cartas
    if data["data"]:  # Si hay resultados, verifica que contengan "name"
        assert "name" in data["data"][0]
        assert "Pikachu" in data["data"][0]["name"]
        


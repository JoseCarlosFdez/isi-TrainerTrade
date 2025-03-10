from fastapi import FastAPI, HTTPException, Query
import requests
from typing import Optional

app = FastAPI()

API_KEY = 'TU_API_KEY_AQUI”'  # Reemplaza con tu clave de API
BASE_URL = 'https://api.pokemontcg.io/v2/cards'

headers = {
    'X-Api-Key': API_KEY
}

@app.get("/")
def read_root():
    return {"message": "Bienvenido al microservicio de Pokémon TCG"}

@app.get("/cards")
def search_cards(
    name: Optional[str] = Query(None, description="Nombre de la carta"),
    id:Optional[str] = Query(None, description="ID de la carta"),
    set: Optional[str] = Query(None, description="ID del set"),
    rarity: Optional[str] = Query(None, description="Rareza de la carta"),
    page: int = Query(1, ge=1, description="Número de página"),
    page_size: int = Query(20, ge=1, le=250, description="Tamaño de la página")
):
    query_params = []
    if name:
        query_params.append(f'name:"{name}"')
    if set:
        query_params.append(f'set.id:"{set}"')
    if rarity:
        query_params.append(f'rarity:"{rarity}"')
    if id:
        query_params.append(f'id:"{id}"')
    
    q = ' '.join(query_params) if query_params else '*'
    params = {
        'q': q,
        'page': page,
        'pageSize': page_size
    }
    
    response = requests.get(BASE_URL, headers=headers, params=params)
    
    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail="Error al obtener datos de la API de Pokémon TCG")
    
    return response.json()


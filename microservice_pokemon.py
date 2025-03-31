from fastapi import FastAPI, HTTPException, Query, Request, Response
import io
import requests
from typing import Optional
import random
import logging

from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

from PIL import Image, ImageDraw, ImageFont

app = FastAPI()

# Set up template rendering
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")


API_KEY = 'API_KEY'  # Reemplaza con tu clave de API
BASE_URL = 'https://api.pokemontcg.io/v2/cards'

headers = {
    'X-Api-Key': API_KEY
}

def fetch_players():
    response = requests.get('http://127.0.0.1:8080/users/', headers=headers)
    if response.status_code != 200:
        raise ValueError("Failed to fetch user data")
    return response.json()

# Simulated markers with dynamic images
markers = [
    {"id": "dp3-1", "lat": 51.505, "lon": -0.09, "color": "red"},
    {"id": "dp3-1", "lat": 51.51, "lon": -0.1, "color": "blue"},
]

cards = [
    {"id": 0, "api_id": "dp3-1", "price": 2.39},
    {"id": 1, "api_id": "ex12-1", "price": 1.23},
    {"id": 2, "api_id": "ex7-1", "price": 6.53},
]

players = fetch_players()

# Function to generate marker image dynamically
def generate_marker(color: str):
    size = (40, 40)  # Image size
    img = Image.new("RGBA", size, (255, 255, 255, 0))  # Transparent background
    draw = ImageDraw.Draw(img)

    # Draw a colored circle
    draw.ellipse((5, 5, 35, 35), fill="blue", outline="black")

    # Convert image to bytes
    img_byte_array = io.BytesIO()
    img.save(img_byte_array, format="PNG")
    return img_byte_array.getvalue()

def search_player_by_id(id: int):
    for player in players:
        if player["id"] == id:
            return player
    return None

def generate_card_marker(player_id: int):

    player = search_player_by_id(player_id)
    player_cards = player["cards"]

    size = (775, 362)  # Image size
    img = Image.new("RGBA", size, (0, 0, 0, 255))  # Transparent background

    for i, card_id in enumerate(player_cards):

        card = cards[card_id]
        api_card_id = card["api_id"]
        image_url = search_card_by_id(api_card_id)['data']['images']['small']

        # Fetch image from URL
        response = requests.get(image_url)
        if response.status_code != 200:
            raise ValueError("Failed to fetch image from URL")

        # Open the image
        overlay = Image.open(io.BytesIO(response.content)).convert("RGBA")

        # Resize the image to fit within the marker
        # overlay = overlay.resize((30, 30), Image.LANCZOS)

        # Paste the overlay onto the transparent background
        img.paste(overlay, (10 + 255*i, 10), overlay)

    # Convert image to bytes
    img_byte_array = io.BytesIO()
    img.save(img_byte_array, format="PNG")
    return img_byte_array.getvalue()

# API to serve marker images dynamically
@app.get("/marker-image/{id}.png")
def get_marker_image(id: str):
    img_data = generate_card_marker(int(id))
    return Response(content=img_data, media_type="image/png")

# API to get marker data
@app.get("/markers/")
def get_markers():
    for player in players:
        player["icon"] = f"http://127.0.0.1:8000/marker-image/{player['id']}.png"
    return players

# API to update marker positions
@app.get("/update-markers/")
def update_markers():
    for player in players:
        player["lat"] += random.uniform(-0.001, 0.001)
        player["lon"] += random.uniform(-0.001, 0.001)
    return players


@app.get("/")
def home(request: Request):
    return templates.TemplateResponse("map.html", {"request": request})


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

def search_card_by_id(id: str):
    response = requests.get(f'{BASE_URL}/{id}', headers=headers)
    
    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail="Error al obtener datos de la API de Pokémon TCG")
    
    return response.json()

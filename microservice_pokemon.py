from fastapi import FastAPI, HTTPException, Query, Request, Response
import io
import requests
from typing import Optional
import random

from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

from PIL import Image, ImageDraw, ImageFont

app = FastAPI()

# Set up template rendering
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")


API_KEY = 'TU_API_KEY_AQUI”'  # Reemplaza con tu clave de API
BASE_URL = 'https://api.pokemontcg.io/v2/cards'

headers = {
    'X-Api-Key': API_KEY
}

# Simulated markers with dynamic images
markers = [
    {"id": 1, "lat": 51.505, "lon": -0.09, "color": "red"},
    {"id": 2, "lat": 51.51, "lon": -0.1, "color": "blue"},
]

# Function to generate marker image dynamically
def generate_marker(color: str):
    size = (40, 40)  # Image size
    img = Image.new("RGBA", size, (255, 255, 255, 0))  # Transparent background
    draw = ImageDraw.Draw(img)

    # Draw a colored circle
    draw.ellipse((5, 5, 35, 35), fill=color, outline="black")

    # Convert image to bytes
    img_byte_array = io.BytesIO()
    img.save(img_byte_array, format="PNG")
    return img_byte_array.getvalue()

# API to serve marker images dynamically
@app.get("/marker-image/{color}.png")
def get_marker_image(color: str):
    img_data = generate_marker(color)
    return Response(content=img_data, media_type="image/png")

# API to get marker data
@app.get("/markers/")
def get_markers():
    for marker in markers:
        marker["icon"] = f"http://127.0.0.1:8000/marker-image/{marker['color']}.png"
    return markers

# API to update marker positions
@app.get("/update-markers/")
def update_markers():
    for marker in markers:
        marker["lat"] += random.uniform(-0.001, 0.001)
        marker["lon"] += random.uniform(-0.001, 0.001)
    return markers


@app.get("/")
def home(request: Request):
    return templates.TemplateResponse("map.html", {"request": request})

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


from fastapi import FastAPI, HTTPException, Request, Depends, Query
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from jinja2 import Environment, FileSystemLoader
from typing import List
import json
import requests
import httpx

app = FastAPI()
app.mount("/trainer-trade/static", StaticFiles(directory="static"), name="static")

API_KEY = 'beda8eab-a3b7-4269-8d30-07b0367273c1'  # Reemplaza con tu clave de API
BASE_URL = 'https://api.pokemontcg.io/v2/cards'
DATABASE_URL = "http://database:8080"

headers = {
    'X-Api-Key': API_KEY
}

# Load templates
template_env = Environment(loader=FileSystemLoader("templates"))

# Mock database for user collections

all_cards = requests.get(f'{BASE_URL}', headers=headers).json()["data"]

@app.get("/", response_class=HTMLResponse)
def gallery_page(request: Request, token: str = Query(...)):
    template = template_env.get_template("gallery.html")
    return template.render(all_cards=all_cards, token=token)


@app.get("/user-cards/")
def user_cards(token: str = Query(...)):
    try:
        response = requests.get(
            f"{DATABASE_URL}/user-cards/",
            params={"token": token}  # Pass the token as a query parameter
        )
        response.raise_for_status()  # Raise an exception for HTTP errors
        return JSONResponse(content=response.json())  # Return the JSON response
    except requests.RequestException as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/user-cards/")
async def post_user_cards(request: Request):
    try:
        form_data = await request.json()  # Read the JSON body asynchronously

        response = requests.post(
            f"{DATABASE_URL}/user-cards/",
            json=form_data  # Forward the JSON payload
        )

        return response.json()  # Return the response from the database service

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
import jwt
import datetime
from fastapi import FastAPI, HTTPException, Request, Form
from pydantic import BaseModel
from starlette.responses import RedirectResponse
from typing import Optional
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import requests

from PIL import Image, ImageDraw, ImageFont
import logging


# Secret key to encode and decode JWT (make sure it's kept secure in production)
SECRET_KEY = "your_secret_key_here"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Create the FastAPI app
app = FastAPI()

# Set up template rendering
templates = Jinja2Templates(directory="templates")
app.mount("/trainer-trade/static", StaticFiles(directory="static"), name="static")

# A simple user database (In-memory for demo)
fake_users_db = {
    "user1": {
        "username": "user1",
        "password": "password123"
    },
    "user2": {
        "username": "user2",
        "password": "secret456"
    }
}

def check_user(username: str, password: str):
    """
    Envía un POST a la base de datos con las credenciales del usuario y espera la respuesta.
    """
    response = requests.post('http://database:8080/credentials/', json={"username": username, "password": password})
        
    return response.json()["val"]

def user_exists(username: str):
    """
    Envía un POST a la base de datos con las credenciales del usuario y espera la respuesta.
    """
    response = requests.post('http://database:8080/exists/', json={"username": username})
        
    return response.json()["val"]

def register_user(username: str, password: str, latitude: float, longitude: float):
    """
    Envía un POST a la base de datos con las credenciales del usuario y espera la respuesta.
    """
    response = requests.post('http://database:8080/users/', json={"username": username,
                                                                  "password": password,
                                                                  "cards": [],
                                                                  "lat": latitude,
                                                                  "lon": longitude})
        
    return response.json()
    

# Pydantic model to validate the input data (username & password)
class LoginRequest(BaseModel):
    username: str
    password: str

# Function to create a JWT token
def create_token(username: str):
    expiration = datetime.datetime.utcnow() + datetime.timedelta(hours=1)
    payload = {"sub": username, "exp": expiration}
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    return token



@app.get("/")
async def login_page(request: Request):
    """Render login page."""
    return templates.TemplateResponse("login.html", {"request": request})

@app.get("/register")
async def register_page(request: Request):
    """Render register page."""
    return templates.TemplateResponse("register.html", {"request": request})

@app.post("/")
async def login(
    request: Request,
    username: str = Form(...),
    password: str = Form(...)
):
    # Dummy authentication logic
    if check_user(username, password) is True:
        token = create_token(username)
        
        # Redirect user to the map microservice with the token in the URL
        response = RedirectResponse(url=f"http://127.0.0.1:8000/map?token={token}", status_code=303)
        return response
    else:
        return templates.TemplateResponse("login.html", {"request": request, "error": "Invalid credentials"})

@app.post("/register")
async def register(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    confirm_password: str = Form(...),
    latitude: float = Form(...),
    longitude: float = Form(...)
):
    if user_exists(username) is True:
        return templates.TemplateResponse("login.html", {"request": request, "error": "Invalid credentials"})
    elif password != confirm_password:
        return templates.TemplateResponse("register.html", {"request": request, "error": "Passwords don't match"})
    else:

        # Create a new user in the database
        register_user(username, password, latitude, longitude)

        token = create_token(username)
        
        # Redirect user to the map microservice with the token in the URL
        response = RedirectResponse(url=f"http://127.0.0.1:8000/map?token={token}", status_code=303)
        return response

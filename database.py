from fastapi import FastAPI, Depends, HTTPException, Query
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from pydantic import BaseModel
from typing import List
from fastapi.responses import HTMLResponse
from sqlalchemy.types import JSON, Float  # Import JSON type for better support
import jwt

from fastapi.responses import HTMLResponse
import io
import requests
# Configuración de la base de datos
DATABASE_URL = "sqlite:///database.db"
engine = create_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

API_KEY = 'beda8eab-a3b7-4269-8d30-07b0367273c1'  # Reemplaza con tu clave de API
BASE_URL = 'https://api.pokemontcg.io/v2/cards'

headers = {
    'X-Api-Key': API_KEY
}

# Modelo de Usuario en SQLAlchemy
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    password = Column(String, nullable=False)
    cards = Column(JSON, nullable=False, default=list)  # Store integer list as JSON
    lat = Column(Float, nullable=True)  # Latitude of the user
    lon = Column(Float, nullable=True)  # Longitude of the user

# Esquemas Pydantic para validación de datos
class UserLogin(BaseModel):
    username: str
    password: str

class UserExists(BaseModel):
    username: str

# Esquemas Pydantic para validación de datos
class UserCreate(BaseModel):
    username: str
    password: str
    cards: List[int]
    lat: float | None = None
    lon: float | None = None

class UserResponse(BaseModel):
    id: int
    username: str
    cards: List[int]
    lat: float | None
    lon: float | None

    class Config:
        from_attributes = True

class Card(Base):
    __tablename__ = "cards"
    id = Column(Integer, primary_key=True, index=True)
    api_id = Column(String, unique=False, nullable=False)
    price = Column(Float, nullable=False)

class PostCard(BaseModel):
    token: str
    cardId: str

# Crear la base de datos
Base.metadata.create_all(bind=engine)

# Dependencia para obtener la sesión de la base de datos
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

SECRET_KEY = "your_secret_key_here"
ALGORITHM = "HS256"

def verify_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload  # You can extract user data here
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

# Inicialización de la aplicación FastAPI
app = FastAPI()

@app.get("/user-cards/")
def get_user_cards(token: str = Query(...), db: Session = Depends(get_db)):
    user_info = verify_token(token)  # If token is valid, you'll get user info
    username = user_info["sub"]  # Get the username from the token
    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    card_list = []
    for card_id in user.cards:
        card = db.query(Card).filter(Card.id == card_id).first()
        if card is not None:
            card_list.append(card)
    return card_list

def search_card_by_id(id: str):
    response = requests.get(f'{BASE_URL}/{id}', headers=headers)
    
    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail="Error al obtener datos de la API de Pokémon TCG")
    
    return response.json()

@app.post("/user-cards/")
def add_user_card(post_card: PostCard, db: Session = Depends(get_db)):
    token = post_card.token
    card_id = post_card.cardId
    user_info = verify_token(token)  # If token is valid, you'll get user info
    username = user_info["sub"]  # Get the username from the token
    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    card_list = []
    # Check if the card already exists in the database
    # If the card does not exist, fetch it from the API
    # card_data = search_card_by_id(card_id)
    new_card = Card(
        api_id=card_id,
        price=0.0  # Set the price to 0.0 for now
    )
    db.add(new_card)
    db.commit()
    db.refresh(new_card)
    card_list.append(new_card.id)


    # Add the card ID to the user's card list
    user.cards = user.cards + card_list
    db.commit()
    return {"message": "Card added successfully"}

@app.post("/users/", response_model=UserResponse)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    # Verificar si el usuario ya existe por username
    existing_user = db.query(User).filter(User.username == user.username).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="El usuario ya está registrado")
    
    db_user = User(
        username=user.username,
        password=user.password,
        cards=user.cards,
        lat=user.lat,
        lon=user.lon
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@app.post("/credentials/", status_code=200)
def authenticate_user(user: UserLogin, db: Session = Depends(get_db)):
    """
    Verifica las credenciales del usuario en la base de datos sin cifrado.
    """
    db_user = db.query(User).filter(
        User.username == user.username, User.password == user.password
    ).first()

    if not db_user:
        return {"val": False}
    
    return {"val": True}


@app.post("/exists/", status_code=200)
def user_exists(user: UserExists, db: Session = Depends(get_db)):
    """
    Verifica las credenciales del usuario en la base de datos sin cifrado.
    """
    db_user = db.query(User).filter(
        User.username == user.username
    ).first()

    if not db_user:
        return {"val": False}
    
    return {"val": True}


@app.get("/users/{username}", response_model=UserResponse)
def get_user(username: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return user

@app.get("/users/", response_model=List[UserResponse])
def get_users(db: Session = Depends(get_db)):
    users = db.query(User).all()
    return users

@app.get("/cards/")
def get_cards(db: Session = Depends(get_db)):
    cards = db.query(Card).all()
    return cards

@app.put("/users/{user_id}", response_model=UserResponse)
def update_user(user_id: int, new_email: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    user.email = new_email  # This will cause an issue since `email` doesn't exist in the `User` model.
    db.commit()
    db.refresh(user)
    return user

@app.delete("/users/{user_id}", response_model=dict)
def delete_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    db.delete(user)
    db.commit()
    return {"message": "Usuario eliminado exitosamente"}

from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from pydantic import BaseModel
from typing import List
from fastapi.responses import HTMLResponse
from sqlalchemy.types import JSON, Float  # Import JSON type for better support

# Configuración de la base de datos
DATABASE_URL = "sqlite:///database.db"
engine = create_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Modelo de Usuario en SQLAlchemy
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    password = Column(String, nullable=False)
    cards = Column(JSON, nullable=False, default=list)  # Store integer list as JSON
    lat = Column(Float, nullable=True)  # Latitude of the user
    lon = Column(Float, nullable=True)  # Longitude of the user

# Crear la base de datos
Base.metadata.create_all(bind=engine)

# Esquemas Pydantic para validación de datos
class UserLogin(BaseModel):
    username: str
    password: str

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

# Dependencia para obtener la sesión de la base de datos
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Inicialización de la aplicación FastAPI
app = FastAPI()

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

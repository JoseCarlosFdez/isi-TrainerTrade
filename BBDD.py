from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from typing import Optional

# Configuración de la base de datos
DATABASE_URL = "sqlite:///users.db"  # Puedes cambiar a PostgreSQL, MySQL, etc.
engine = create_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

# Modelo de Usuario
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    password = Column(String, nullable=False)  # Asegúrate de encriptar las contraseñas

# Crear la base de datos y la tabla
Base.metadata.create_all(bind=engine)

def create_user(username, email, password, session):
    user = User(username=username, email=email, password=password)
    session.add(user)
    session.commit()  # Asegura que los cambios se guarden en la base de datos



def get_user(username, session):
    return session.query(User).filter(User.username == username).first()



# Función para modificar un usuario
def update_user(user_id, new_email, session):
    user = session.query(User).filter(User.id == user_id).first()
    if user:
        user.email = new_email
        session.commit()  # ¡IMPORTANTE!



# Función para eliminar un usuario
def delete_user(user_id, session):
    user = session.query(User).filter(User.id == user_id).first()
    if user:
        session.delete(user)
        session.commit()



import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database import Base, User, create_user, update_user, delete_user, get_user
import random
import string

# Configuración de la base de datos de pruebas (por ejemplo, SQLite en memoria)
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"  # Base de datos en memoria para pruebas
engine = create_engine(SQLALCHEMY_DATABASE_URL, echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Crear la base de datos y las tablas en la base de datos de prueba
Base.metadata.create_all(bind=engine)

# Fixture de sesión
@pytest.fixture()
def session():
    db_session = SessionLocal()
    # Limpiar usuarios antes de la prueba
    db_session.query(User).delete()
    db_session.commit()  # Asegúrate de que los cambios se persisten
    try:
        yield db_session
    finally:
        db_session.close()

# Función para generar un username y email únicos
def generate_unique_username():
    return "user_" + ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))

def generate_unique_email():
    return generate_unique_username() + "@example.com"

def test_create_user(session):
    username = generate_unique_username()
    email = generate_unique_email()
    password = "testpassword"

    create_user(username, email, password, session)  # Aquí se pasa session

    session.flush()  # Asegura que los cambios sean visibles en la misma transacción

    user = session.query(User).filter(User.username == username).first()
    print(f"Usuario recuperado: {user}")

    assert user is not None


def test_update_user(session):
    username = generate_unique_username()
    email = generate_unique_email()
    password = "testpassword"

    create_user(username, email, password, session)  # Aquí también

    user = session.query(User).filter(User.username == username).first()
    assert user is not None

    new_email = generate_unique_email()
    update_user(user.id, new_email, session)  # También asegurarse de que update_user use la sesión

    updated_user = session.query(User).filter(User.id == user.id).first()
    assert updated_user.email == new_email


def test_delete_user(session):
    username = generate_unique_username()
    email = generate_unique_email()
    password = "testpassword"

    create_user(username, email, password, session)

    user = session.query(User).filter(User.username == username).first()
    assert user is not None

    delete_user(user.id, session)  # Asegurar que delete_user también reciba la sesión

    deleted_user = session.query(User).filter(User.id == user.id).first()
    assert deleted_user is None


def test_get_user(session):
    # Usa un username único para la prueba de obtención
    username = generate_unique_username()
    email = generate_unique_email()
    password = "testpassword"
    
    create_user(username, email, password, session)
    
    user = get_user(username, session)
    assert user is not None
    assert user.username == username

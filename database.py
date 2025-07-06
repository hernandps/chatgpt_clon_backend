from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv
from sqlalchemy.orm import Session
from typing import Generator

# Carga las variables del archivo .env
load_dotenv()

# URL de la base de datos (viene desde .env)
DATABASE_URL = os.getenv("DATABASE_URL")

# Crea el engine de SQLAlchemy
engine = create_engine(DATABASE_URL)

# Crea el sessionmaker para generar sesiones con la base de datos
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base para los modelos
Base = declarative_base()



def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
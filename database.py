import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

load_dotenv() # Carrega o seu .env quando estiver no PC

# Ele vai tentar pegar a URL do Render. Se não achar, usa o SQLite do seu PC.
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./treino_app.db")

# O SQLite precisa de uma configuração extra que o Postgres não precisa
if SQLALCHEMY_DATABASE_URL.startswith("sqlite"):
    engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
else:
    engine = create_engine(SQLALCHEMY_DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
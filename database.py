import os
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# Carrega as senhas ocultas do arquivo .env (quando formos para a nuvem)
load_dotenv()

# Tenta conectar na nuvem. Se não existir link na nuvem, usa o SEU SQLite original!
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./treino_app.db")

# Correção obrigatória: Alguns servidores fornecem o link como "postgres://", 
# mas as versões novas do SQLAlchemy exigem "postgresql://"
if SQLALCHEMY_DATABASE_URL.startswith("postgres://"):
    SQLALCHEMY_DATABASE_URL = SQLALCHEMY_DATABASE_URL.replace("postgres://", "postgresql://", 1)

# O CÉREBRO DA CONEXÃO: Separa o que é local do que é nuvem
if SQLALCHEMY_DATABASE_URL.startswith("sqlite"):
    # Se for SQLite (Local), usa o check_same_thread
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
    )
else:
    # Se for PostgreSQL (Nuvem), conecta direto e reto
    engine = create_engine(SQLALCHEMY_DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
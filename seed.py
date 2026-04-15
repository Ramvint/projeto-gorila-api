import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import models  # <--- ESSA LINHA É A CHAVE!

# URL DO NEON PARA O BATISMO
URL_NUVEM = "postgresql://neondb_owner:npg_IcWaxwH3KvY4@ep-delicate-glitter-anobx8li.c-6.us-east-1.aws.neon.tech/neondb?sslmode=require"

engine = create_engine(URL_NUVEM)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
db = SessionLocal()

def inserir_treino(nome, exercicios):
    # Agora o Python sabe o que é 'models'
    treino = models.Treino(nome_rotina=nome)
    db.add(treino)
    db.commit()
    db.refresh(treino)
    
    # ... resto do seu código de repetição (for) continua igual abaixo ...
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import models

# URL DO NEON
URL_NUVEM = "postgresql://neondb_owner:npg_IcWaxwH3KvY4@ep-delicate-glitter-anobx8li.c-6.us-east-1.aws.neon.tech/neondb?sslmode=require"

engine = create_engine(URL_NUVEM)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
db = SessionLocal()

def resetar_e_popular():
    print("🧹 Limpando banco de dados na nuvem...")
    # Isso recria as tabelas do zero para limpar erros
    models.Base.metadata.drop_all(bind=engine)
    models.Base.metadata.create_all(bind=engine)

    print("🍎 Inserindo Catálogo de Alimentos...")
    alimentos = [
        models.Alimento(nome="Frango Grelhado", calorias=165, proteina=31, carboidrato=0, gordura=3.6),
        models.Alimento(nome="Arroz Branco Cozido", calorias=130, proteina=2.7, carboidrato=28, gordura=0.3),
        models.Alimento(nome="Ovo Cozido", calorias=155, proteina=13, carboidrato=1.1, gordura=11),
        models.Alimento(nome="Banana Prata", calorias=89, proteina=1.1, carboidrato=23, gordura=0.3),
    ]
    db.add_all(alimentos)

    print("💪 Inserindo Exercícios e Treino A...")
    treino_a = models.Treino(nome_rotina="A - Peito e Tríceps")
    db.add(treino_a)
    db.commit()
    db.refresh(treino_a)

    exs = [
        {"nome": "Supino Reto", "grupo": "Peito", "series": 4, "reps": "12"},
        {"nome": "Tríceps Corda", "grupo": "Tríceps", "series": 3, "reps": "15"}
    ]

    for item in exs:
        ex_obj = models.Exercicio(nome=item["nome"], grupo_muscular=item["grupo"])
        db.add(ex_obj)
        db.commit()
        db.refresh(ex_obj)
        
        relacao = models.TreinoExercicio(
            treino_id=treino_a.id, 
            exercicio_id=ex_obj.id, 
            series=item["series"], 
            reps=item["reps"]
        )
        db.add(relacao)

    db.commit()
    print("✅ Banco de dados RESETADO e POPULADO com sucesso!")

if __name__ == "__main__":
    resetar_e_popular()
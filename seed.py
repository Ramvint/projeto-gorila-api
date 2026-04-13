from database import SessionLocal
import models

db = SessionLocal()

def inserir_treino(nome, exercicios):
    treino = models.Treino(nome_rotina=nome)
    db.add(treino)
    db.commit()
    db.refresh(treino)

    for ex in exercicios:
        novo_ex = models.Exercicio(nome=ex["nome"], grupo_muscular=ex["grupo"])
        db.add(novo_ex)
        db.commit()
        db.refresh(novo_ex)
        
        treino_ex = models.TreinoExercicio(
            treino_id=treino.id, 
            exercicio_id=novo_ex.id, 
            series=ex["series"], 
            reps=ex["reps"]
        )
        db.add(treino_ex)
    db.commit()

# Dados do Treino A [cite: 6, 8, 9, 12, 13, 15, 16, 19, 20, 22, 23, 25, 26]
treino_a = [
    {"nome": "Crucifixo Máquina", "grupo": "Peito", "series": 4, "reps": "12-10"},
    {"nome": "Banco Supino Reto", "grupo": "Peito", "series": 4, "reps": "12-10"},
    {"nome": "Supino Inclinado com Halteres", "grupo": "Peito", "series": 3, "reps": "10"},
    {"nome": "Desenvolvimento Arnold Sentado", "grupo": "Ombro", "series": 3, "reps": "12"},
    {"nome": "Elevação Lateral com Halteres", "grupo": "Ombro", "series": 3, "reps": "12"},
    {"nome": "Tríceps na Polia com Corda", "grupo": "Tríceps", "series": 3, "reps": "12"},
    {"nome": "Tríceps Francês Unilateral", "grupo": "Tríceps", "series": 3, "reps": "12"}
]
inserir_treino("A", treino_a)

# Dados do Treino B [cite: 33, 34, 36, 37, 39, 40, 42, 43, 45, 46, 48, 49, 51, 52]
treino_b = [
    {"nome": "Puxada Aberta Barra reta", "grupo": "Costas", "series": 4, "reps": "10"},
    {"nome": "Puxada Neutra triangulo", "grupo": "Costas", "series": 4, "reps": "10"},
    {"nome": "Remada Máquina (Pegada Pronada)", "grupo": "Costas", "series": 4, "reps": "10"},
    {"nome": "Remada Cavalinho (Pegada Neutra)", "grupo": "Costas", "series": 4, "reps": "10"},
    {"nome": "Crucifixo Inverso Sentado", "grupo": "Costas", "series": 4, "reps": "10"},
    {"nome": "Rosca Direta com Halteres", "grupo": "Bíceps", "series": 4, "reps": "12"},
    {"nome": "Rosca Concentrada", "grupo": "Bíceps", "series": 4, "reps": "12"}
]
inserir_treino("B", treino_b)

# Dados do Treino C [cite: 60, 61, 63, 64, 66, 67, 69, 70, 72, 73]
treino_c = [
    {"nome": "Agachamento Livre", "grupo": "Pernas", "series": 4, "reps": "10"},
    {"nome": "Cadeira Extensora", "grupo": "Pernas", "series": 4, "reps": "12"},
    {"nome": "Cadeira Flexora", "grupo": "Pernas", "series": 4, "reps": "10"},
    {"nome": "Leg Press 45", "grupo": "Pernas", "series": 4, "reps": "10"},
    {"nome": "Panturrilha Sentado", "grupo": "Panturrilha", "series": 4, "reps": "10"}
]
inserir_treino("C", treino_c)

print("Ficha de treinos inserida com sucesso no Projeto Gorila!")
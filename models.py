from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey, DateTime
from sqlalchemy.sql import func
from database import Base

class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, index=True)
    peso_atual = Column(Float, default=55.0)
    meta_peso = Column(Float)

class Exercicio(Base):
    __tablename__ = "exercicios"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, index=True)
    grupo_muscular = Column(String)

class Treino(Base):
    __tablename__ = "treinos"

    id = Column(Integer, primary_key=True, index=True)
    nome_rotina = Column(String) # Ex: Treino A, Treino B
    foco = Column(String, default="Hipertrofia")
    nivel = Column(String, default="Iniciante")

class TreinoExercicio(Base):
    __tablename__ = "treino_exercicios"

    id = Column(Integer, primary_key=True, index=True)
    treino_id = Column(Integer, ForeignKey("treinos.id"))
    exercicio_id = Column(Integer, ForeignKey("exercicios.id"))
    series = Column(Integer)
    reps = Column(String) 
    carga_base = Column(Float, default=0.0) 

# --- NOVAS TABELAS DE RASTREAMENTO REAL ---

class SessaoTreino(Base):
    __tablename__ = "sessoes_treino"

    id = Column(Integer, primary_key=True, index=True)
    treino_id = Column(Integer, ForeignKey("treinos.id"))
    data_inicio = Column(DateTime(timezone=True), server_default=func.now())
    data_fim = Column(DateTime(timezone=True), nullable=True)
    status = Column(String, default='em_andamento')  # 'em_andamento' ou 'finalizada'

class SerieRegistrada(Base):
    __tablename__ = 'series_registradas'
    __table_args__ = {'extend_existing': True}
    id = Column(Integer, primary_key=True, index=True)
    sessao_id = Column(Integer, ForeignKey("sessoes_treino.id"))
    exercicio_id = Column(Integer, ForeignKey("exercicios.id"))
    carga = Column(Float, nullable=True)
    repeticoes = Column(Integer)
    data_registro = Column(DateTime(timezone=True), server_default=func.now())

    # --- TABELA DE ALIMENTOS ---
class Alimento(Base):
    __tablename__ = "alimentos"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, index=True)
    calorias = Column(Float)
    proteina = Column(Float)
    carboidrato = Column(Float)
    gordura = Column(Float)
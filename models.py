from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey, DateTime
from sqlalchemy.sql import func
from database import Base

class Usuario(Base):
    __tablename__ = "usuarios"
    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, index=True)
    peso_atual = Column(Float, default=55.0)
    meta_peso = Column(Float)

# --- 1. CATÁLOGO NASM ---
class CatalogoExercicio(Base):
    __tablename__ = 'catalogo_exercicios'
    id = Column(Integer, primary_key=True, index=True)
    nome_padrao = Column(String, unique=True)
    nome_exibicao = Column(String)
    grupo_muscular_principal = Column(String)
    grupos_musculares_secundarios = Column(String)
    categoria_movimento = Column(String)
    tipo_exercicio = Column(String)
    equipamento = Column(String)
    unilateral_ou_bilateral = Column(String)
    faixa_reps_padrao = Column(String)
    incremento_padrao_carga = Column(Float)
    observacoes = Column(String, nullable=True)
    ativo = Column(Boolean, default=True)
    usa_carga = Column(Boolean, default=True)

# --- 2. FICHAS DE TREINO ---
class FichaTreino(Base):
    __tablename__ = 'fichas_treino'
    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, default=1)
    nome = Column(String)
    foco = Column(String)

class FichaExercicio(Base):
    __tablename__ = 'fichas_exercicios'
    id = Column(Integer, primary_key=True, index=True)
    ficha_id = Column(Integer, ForeignKey("fichas_treino.id"))
    catalogo_id = Column(Integer, ForeignKey("catalogo_exercicios.id"))
    series = Column(Integer)
    reps = Column(String)
    descanso = Column(Integer)
    observacao = Column(String, nullable=True)

# --- 3. RASTREAMENTO REAL (Sessões e Histórico) ---
class SessaoTreino(Base):
    __tablename__ = "sessoes_treino"
    id = Column(Integer, primary_key=True, index=True)
    treino_id = Column(Integer, ForeignKey("fichas_treino.id"))
    data_inicio = Column(DateTime(timezone=True), server_default=func.now())
    data_fim = Column(DateTime(timezone=True), nullable=True)
    status = Column(String, default='em_andamento')

class SerieRegistrada(Base):
    __tablename__ = 'series_registradas'
    id = Column(Integer, primary_key=True, index=True)
    sessao_id = Column(Integer, ForeignKey("sessoes_treino.id"))
    exercicio_id = Column(Integer, ForeignKey("catalogo_exercicios.id")) # 🔥 BOMBA DESARMADA: Agora aponta pro Catálogo Novo!
    carga = Column(Float, nullable=True)
    repeticoes = Column(Integer)
    data_registro = Column(DateTime(timezone=True), server_default=func.now())

# --- 4. NUTRIÇÃO ---
class RegistroNutricao(Base):
    __tablename__ = 'registro_nutricao'
    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, default=1)
    refeicao = Column(String)
    nome_alimento = Column(String)
    kcal = Column(Float)
    proteina = Column(Float)
    carbo = Column(Float)
    gordura = Column(Float)
    data_registro = Column(String)

class MetaNutricao(Base):
    __tablename__ = 'metas_nutricao'
    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, unique=True, default=1)
    kcal = Column(Float, default=2800.0)
    proteina = Column(Float, default=160.0)
    carbo = Column(Float, default=350.0)
    gordura = Column(Float, default=80.0)

class AlimentoPersonalizado(Base):
    __tablename__ = 'alimentos_personalizados'
    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, default=1)
    nome = Column(String)
    porcao_g = Column(Float)
    kcal = Column(Float)
    proteina = Column(Float)
    carbo = Column(Float)
    gordura = Column(Float)
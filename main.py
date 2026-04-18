from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import Column, Integer, String, Float, Boolean, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import func
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime, timedelta
import models
from database import SessionLocal, engine
from typing import Optional
from sqlalchemy import text
import json
# --- TABELAS DE NUTRIÇÃO ---
class RegistroNutricao(models.Base):
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

class MetaNutricao(models.Base):
    __tablename__ = 'metas_nutricao'
    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, unique=True, default=1)
    kcal = Column(Float, default=2800.0)
    proteina = Column(Float, default=160.0)
    carbo = Column(Float, default=350.0)
    gordura = Column(Float, default=80.0)

class AlimentoPersonalizado(models.Base):
    __tablename__ = 'alimentos_personalizados'
    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, default=1)
    nome = Column(String)
    porcao_g = Column(Float)
    kcal = Column(Float)
    proteina = Column(Float)
    carbo = Column(Float)
    gordura = Column(Float)

# --- TABELA DE CATÁLOGO NASM ---
class CatalogoExercicio(models.Base):
    __tablename__ = 'catalogo_exercicios'
    __table_args__ = {'extend_existing': True}
    id = Column(Integer, primary_key=True, index=True)
    nome_padrao = Column(String, unique=True); nome_exibicao = Column(String); grupo_muscular_principal = Column(String); grupos_musculares_secundarios = Column(String)
    categoria_movimento = Column(String); tipo_exercicio = Column(String); equipamento = Column(String); unilateral_ou_bilateral = Column(String) 
    faixa_reps_padrao = Column(String); incremento_padrao_carga = Column(Float); observacoes = Column(String, nullable=True)
    ativo = Column(Boolean, default=True)
    usa_carga = Column(Boolean, default=True) 

class FichaTreino(models.Base):
    __tablename__ = 'fichas_treino'
    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, default=1)
    nome = Column(String) 
    foco = Column(String)

class FichaExercicio(models.Base):
    __tablename__ = 'fichas_exercicios'
    id = Column(Integer, primary_key=True, index=True)
    ficha_id = Column(Integer)
    catalogo_id = Column(Integer)
    series = Column(Integer)
    reps = Column(String) # Aceita "8-12"
    descanso = Column(Integer)
    observacao = Column(String, nullable=True)

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Gorila App API - Master Edition")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

def get_db():
    db = SessionLocal()
    try: yield db
    finally: db.close()

# --- SEED DE DADOS: O CATÁLOGO DE ELITE ---
def semear_catalogo_exercicios(db: Session):
    
    if db.query(CatalogoExercicio).count() >= 150:
        return 
    
    db.query(CatalogoExercicio).delete()
    db.commit()

    exercicios = [
        # === PEITO (23 Exercícios) ===
        {"nome_padrao": "supino_reto_barra", "nome_exibicao": "Supino Reto com Barra", "grupo": "Peito", "secundario": "Tríceps, Ombros", "movimento": "Empurrar", "tipo": "composto", "equipamento": "barra", "uni_bi": "bilateral", "reps": "8-10", "inc": 2.0},
        {"nome_padrao": "supino_reto_halteres", "nome_exibicao": "Supino Reto com Halteres", "grupo": "Peito", "secundario": "Tríceps, Ombros", "movimento": "Empurrar", "tipo": "composto", "equipamento": "halteres", "uni_bi": "bilateral", "reps": "8-12", "inc": 2.0},
        {"nome_padrao": "supino_reto_maquina", "nome_exibicao": "Supino Reto na Máquina", "grupo": "Peito", "secundario": "Tríceps, Ombros", "movimento": "Empurrar", "tipo": "composto", "equipamento": "maquina", "uni_bi": "bilateral", "reps": "8-12", "inc": 2.0},
        {"nome_padrao": "supino_reto_smith", "nome_exibicao": "Supino Reto no Smith", "grupo": "Peito", "secundario": "Tríceps, Ombros", "movimento": "Empurrar", "tipo": "composto", "equipamento": "smith", "uni_bi": "bilateral", "reps": "8-10", "inc": 2.0},
        {"nome_padrao": "supino_inclinado_barra", "nome_exibicao": "Supino Inclinado com Barra", "grupo": "Peito", "secundario": "Tríceps, Ombros", "movimento": "Empurrar", "tipo": "composto", "equipamento": "barra", "uni_bi": "bilateral", "reps": "8-10", "inc": 2.0},
        {"nome_padrao": "supino_inclinado_halteres", "nome_exibicao": "Supino Inclinado com Halteres", "grupo": "Peito", "secundario": "Tríceps, Ombros", "movimento": "Empurrar", "tipo": "composto", "equipamento": "halteres", "uni_bi": "bilateral", "reps": "8-12", "inc": 2.0},
        {"nome_padrao": "supino_inclinado_maquina", "nome_exibicao": "Supino Inclinado na Máquina", "grupo": "Peito", "secundario": "Tríceps, Ombros", "movimento": "Empurrar", "tipo": "composto", "equipamento": "maquina", "uni_bi": "bilateral", "reps": "8-12", "inc": 2.0},
        {"nome_padrao": "supino_inclinado_smith", "nome_exibicao": "Supino Inclinado no Smith", "grupo": "Peito", "secundario": "Tríceps, Ombros", "movimento": "Empurrar", "tipo": "composto", "equipamento": "smith", "uni_bi": "bilateral", "reps": "8-10", "inc": 2.0},
        {"nome_padrao": "supino_declinado_barra", "nome_exibicao": "Supino Declinado com Barra", "grupo": "Peito", "secundario": "Tríceps, Ombros", "movimento": "Empurrar", "tipo": "composto", "equipamento": "barra", "uni_bi": "bilateral", "reps": "8-10", "inc": 2.0},
        {"nome_padrao": "supino_declinado_halteres", "nome_exibicao": "Supino Declinado com Halteres", "grupo": "Peito", "secundario": "Tríceps, Ombros", "movimento": "Empurrar", "tipo": "composto", "equipamento": "halteres", "uni_bi": "bilateral", "reps": "8-12", "inc": 2.0},
        {"nome_padrao": "crucifixo_reto_halteres", "nome_exibicao": "Crucifixo Reto com Halteres", "grupo": "Peito", "secundario": "Ombros", "movimento": "Adução Horizontal", "tipo": "isolado", "equipamento": "halteres", "uni_bi": "bilateral", "reps": "10-12", "inc": 2.0},
        {"nome_padrao": "crucifixo_reto_polia", "nome_exibicao": "Crucifixo Reto na Polia", "grupo": "Peito", "secundario": "Ombros", "movimento": "Adução Horizontal", "tipo": "isolado", "equipamento": "polia", "uni_bi": "bilateral", "reps": "10-12", "inc": 1.0},
        {"nome_padrao": "crucifixo_inclinado_halteres", "nome_exibicao": "Crucifixo Inclinado com Halteres", "grupo": "Peito", "secundario": "Ombros", "movimento": "Adução Horizontal", "tipo": "isolado", "equipamento": "halteres", "uni_bi": "bilateral", "reps": "10-12", "inc": 2.0},
        {"nome_padrao": "crucifixo_inclinado_polia", "nome_exibicao": "Crucifixo Inclinado na Polia", "grupo": "Peito", "secundario": "Ombros", "movimento": "Adução Horizontal", "tipo": "isolado", "equipamento": "polia", "uni_bi": "bilateral", "reps": "10-12", "inc": 1.0},
        {"nome_padrao": "crossover_polia_alta", "nome_exibicao": "Crossover na Polia Alta (Foco Inferior)", "grupo": "Peito", "secundario": "Ombros", "movimento": "Adução Horizontal", "tipo": "isolado", "equipamento": "polia", "uni_bi": "bilateral", "reps": "10-12", "inc": 1.0},
        {"nome_padrao": "crossover_polia_media", "nome_exibicao": "Crossover na Polia Média (Foco Medial)", "grupo": "Peito", "secundario": "Ombros", "movimento": "Adução Horizontal", "tipo": "isolado", "equipamento": "polia", "uni_bi": "bilateral", "reps": "10-12", "inc": 1.0},
        {"nome_padrao": "crossover_polia_baixa", "nome_exibicao": "Crossover na Polia Baixa (Foco Superior)", "grupo": "Peito", "secundario": "Ombros", "movimento": "Adução Horizontal", "tipo": "isolado", "equipamento": "polia", "uni_bi": "bilateral", "reps": "10-12", "inc": 1.0},
        {"nome_padrao": "voador_maquina", "nome_exibicao": "Voador na Máquina (Peck Deck)", "grupo": "Peito", "secundario": "Ombros", "movimento": "Adução Horizontal", "tipo": "isolado", "equipamento": "maquina", "uni_bi": "bilateral", "reps": "10-12", "inc": 2.0},
        {"nome_padrao": "pullover_halteres", "nome_exibicao": "Pullover com Halter", "grupo": "Peito", "secundario": "Dorsais, Tríceps", "movimento": "Extensão", "tipo": "composto", "equipamento": "halteres", "uni_bi": "bilateral", "reps": "10-12", "inc": 2.0},
        {"nome_padrao": "pullover_polia", "nome_exibicao": "Pullover na Polia", "grupo": "Peito", "secundario": "Dorsais", "movimento": "Extensão", "tipo": "isolado", "equipamento": "polia", "uni_bi": "bilateral", "reps": "10-12", "inc": 1.0},
        {"nome_padrao": "flexao_braco_solo", "nome_exibicao": "Flexão de Braço Tradicional", "grupo": "Peito", "secundario": "Tríceps, Core", "movimento": "Empurrar", "tipo": "composto", "equipamento": "peso corporal", "uni_bi": "bilateral", "reps": "10-20", "inc": 0.0},
        {"nome_padrao": "flexao_braco_declinada", "nome_exibicao": "Flexão de Braço Declinada (Pés Elevados)", "grupo": "Peito", "secundario": "Tríceps, Ombros", "movimento": "Empurrar", "tipo": "composto", "equipamento": "peso corporal", "uni_bi": "bilateral", "reps": "10-20", "inc": 0.0},
        {"nome_padrao": "mergulho_paralelas_peito", "nome_exibicao": "Mergulho nas Paralelas (Tronco Inclinado)", "grupo": "Peito", "secundario": "Tríceps, Ombros", "movimento": "Empurrar", "tipo": "composto", "equipamento": "peso corporal", "uni_bi": "bilateral", "reps": "8-12", "inc": 0.0},

        # === COSTAS (26 Exercícios) ===
        {"nome_padrao": "puxada_frontal_pronada", "nome_exibicao": "Puxada Frontal com Pegada Pronada", "grupo": "Costas", "secundario": "Bíceps", "movimento": "Puxar", "tipo": "composto", "equipamento": "polia", "uni_bi": "bilateral", "reps": "8-12", "inc": 2.0},
        {"nome_padrao": "puxada_frontal_supinada", "nome_exibicao": "Puxada Frontal com Pegada Supinada", "grupo": "Costas", "secundario": "Bíceps", "movimento": "Puxar", "tipo": "composto", "equipamento": "polia", "uni_bi": "bilateral", "reps": "8-12", "inc": 2.0},
        {"nome_padrao": "puxada_frontal_triangulo", "nome_exibicao": "Puxada Frontal com Triângulo (Pegada Neutra)", "grupo": "Costas", "secundario": "Bíceps", "movimento": "Puxar", "tipo": "composto", "equipamento": "polia", "uni_bi": "bilateral", "reps": "8-12", "inc": 2.0},
        {"nome_padrao": "puxada_articulada_maquina", "nome_exibicao": "Puxada Articulada na Máquina", "grupo": "Costas", "secundario": "Bíceps", "movimento": "Puxar", "tipo": "composto", "equipamento": "maquina", "uni_bi": "bilateral", "reps": "8-12", "inc": 2.0},
        {"nome_padrao": "puxada_unilateral_polia", "nome_exibicao": "Puxada Unilateral na Polia Alta", "grupo": "Costas", "secundario": "Bíceps", "movimento": "Puxar", "tipo": "composto", "equipamento": "polia", "uni_bi": "unilateral", "reps": "8-12", "inc": 1.0},
        {"nome_padrao": "remada_curvada_pronada", "nome_exibicao": "Remada Curvada com Barra (Pegada Pronada)", "grupo": "Costas", "secundario": "Bíceps, Lombar", "movimento": "Puxar", "tipo": "composto", "equipamento": "barra", "uni_bi": "bilateral", "reps": "8-10", "inc": 2.0},
        {"nome_padrao": "remada_curvada_supinada", "nome_exibicao": "Remada Curvada com Barra (Pegada Supinada)", "grupo": "Costas", "secundario": "Bíceps, Lombar", "movimento": "Puxar", "tipo": "composto", "equipamento": "barra", "uni_bi": "bilateral", "reps": "8-10", "inc": 2.0},
        {"nome_padrao": "remada_curvada_smith", "nome_exibicao": "Remada Curvada no Smith", "grupo": "Costas", "secundario": "Bíceps", "movimento": "Puxar", "tipo": "composto", "equipamento": "smith", "uni_bi": "bilateral", "reps": "8-12", "inc": 2.0},
        {"nome_padrao": "remada_cavalinho_barra", "nome_exibicao": "Remada Cavalinho com Barra (T-Bar)", "grupo": "Costas", "secundario": "Bíceps, Lombar", "movimento": "Puxar", "tipo": "composto", "equipamento": "barra", "uni_bi": "bilateral", "reps": "8-12", "inc": 2.0},
        {"nome_padrao": "remada_cavalinho_maquina", "nome_exibicao": "Remada Cavalinho na Máquina", "grupo": "Costas", "secundario": "Bíceps", "movimento": "Puxar", "tipo": "composto", "equipamento": "maquina", "uni_bi": "bilateral", "reps": "8-12", "inc": 2.0},
        {"nome_padrao": "remada_unilateral_halter", "nome_exibicao": "Remada Unilateral com Halter (Serrote)", "grupo": "Costas", "secundario": "Bíceps", "movimento": "Puxar", "tipo": "composto", "equipamento": "halteres", "uni_bi": "unilateral", "reps": "8-12", "inc": 2.0},
        {"nome_padrao": "remada_baixa_triangulo", "nome_exibicao": "Remada Baixa na Polia com Triângulo", "grupo": "Costas", "secundario": "Bíceps", "movimento": "Puxar", "tipo": "composto", "equipamento": "polia", "uni_bi": "bilateral", "reps": "8-12", "inc": 2.0},
        {"nome_padrao": "remada_baixa_barra", "nome_exibicao": "Remada Baixa na Polia com Barra (Pegada Larga)", "grupo": "Costas", "secundario": "Bíceps", "movimento": "Puxar", "tipo": "composto", "equipamento": "polia", "uni_bi": "bilateral", "reps": "8-12", "inc": 2.0},
        {"nome_padrao": "remada_articulada_maquina", "nome_exibicao": "Remada Articulada na Máquina", "grupo": "Costas", "secundario": "Bíceps", "movimento": "Puxar", "tipo": "composto", "equipamento": "maquina", "uni_bi": "bilateral", "reps": "8-12", "inc": 2.0},
        {"nome_padrao": "pulldown_polia_corda", "nome_exibicao": "Pulldown na Polia com Corda", "grupo": "Costas", "secundario": "Tríceps Longo", "movimento": "Puxar", "tipo": "isolado", "equipamento": "polia", "uni_bi": "bilateral", "reps": "10-12", "inc": 1.0},
        {"nome_padrao": "pulldown_polia_barra", "nome_exibicao": "Pulldown na Polia com Barra Reta", "grupo": "Costas", "secundario": "Tríceps Longo", "movimento": "Puxar", "tipo": "isolado", "equipamento": "polia", "uni_bi": "bilateral", "reps": "10-12", "inc": 1.0},
        {"nome_padrao": "barra_fixa_pronada", "nome_exibicao": "Barra Fixa Pronada", "grupo": "Costas", "secundario": "Bíceps", "movimento": "Puxar", "tipo": "composto", "equipamento": "peso corporal", "uni_bi": "bilateral", "reps": "6-12", "inc": 0.0},
        {"nome_padrao": "barra_fixa_supinada", "nome_exibicao": "Barra Fixa Supinada (Chin-Up)", "grupo": "Costas", "secundario": "Bíceps", "movimento": "Puxar", "tipo": "composto", "equipamento": "peso corporal", "uni_bi": "bilateral", "reps": "6-12", "inc": 0.0},
        {"nome_padrao": "barra_fixa_neutra", "nome_exibicao": "Barra Fixa com Pegada Neutra", "grupo": "Costas", "secundario": "Bíceps", "movimento": "Puxar", "tipo": "composto", "equipamento": "peso corporal", "uni_bi": "bilateral", "reps": "6-12", "inc": 0.0},
        {"nome_padrao": "graviton_puxada", "nome_exibicao": "Puxada no Graviton", "grupo": "Costas", "secundario": "Bíceps", "movimento": "Puxar", "tipo": "composto", "equipamento": "maquina", "uni_bi": "bilateral", "reps": "8-12", "inc": 2.0},
        {"nome_padrao": "extensao_lombar_banco", "nome_exibicao": "Extensão Lombar no Banco Romano", "grupo": "Costas", "secundario": "Glúteos, Posteriores", "movimento": "Extensão", "tipo": "isolado", "equipamento": "banco", "uni_bi": "bilateral", "reps": "10-12", "inc": 0.0},
        {"nome_padrao": "extensao_lombar_maquina", "nome_exibicao": "Extensão Lombar na Máquina", "grupo": "Costas", "secundario": "Nenhum", "movimento": "Extensão", "tipo": "isolado", "equipamento": "maquina", "uni_bi": "bilateral", "reps": "10-12", "inc": 2.0},
        {"nome_padrao": "levantamento_terra_tradicional", "nome_exibicao": "Levantamento Terra Tradicional", "grupo": "Costas", "secundario": "Glúteos, Posteriores, Core", "movimento": "Puxar", "tipo": "composto", "equipamento": "barra", "uni_bi": "bilateral", "reps": "5-8", "inc": 5.0},
        {"nome_padrao": "levantamento_terra_sumo", "nome_exibicao": "Levantamento Terra Sumô", "grupo": "Costas", "secundario": "Glúteos, Adutores, Core", "movimento": "Puxar", "tipo": "composto", "equipamento": "barra", "uni_bi": "bilateral", "reps": "5-8", "inc": 5.0},
        {"nome_padrao": "meio_terra_rack_pull", "nome_exibicao": "Meio Terra (Rack Pull)", "grupo": "Costas", "secundario": "Lombar, Trapézio", "movimento": "Puxar", "tipo": "composto", "equipamento": "barra", "uni_bi": "bilateral", "reps": "6-10", "inc": 5.0},
        {"nome_padrao": "encolhimento_ombros_barra", "nome_exibicao": "Encolhimento de Ombros com Barra (Trapézio)", "grupo": "Costas", "secundario": "Pescoço", "movimento": "Elevação", "tipo": "isolado", "equipamento": "barra", "uni_bi": "bilateral", "reps": "10-12", "inc": 2.0},
        {"nome_padrao": "encolhimento_ombros_halteres", "nome_exibicao": "Encolhimento de Ombros com Halteres (Trapézio)", "grupo": "Costas", "secundario": "Pescoço", "movimento": "Elevação", "tipo": "isolado", "equipamento": "halteres", "uni_bi": "bilateral", "reps": "10-12", "inc": 2.0},

        # === OMBROS (20 Exercícios) ===
        {"nome_padrao": "desenvolvimento_barra_frente", "nome_exibicao": "Desenvolvimento Frontal com Barra", "grupo": "Ombros", "secundario": "Tríceps, Peito Superior", "movimento": "Empurrar", "tipo": "composto", "equipamento": "barra", "uni_bi": "bilateral", "reps": "8-10", "inc": 2.0},
        {"nome_padrao": "desenvolvimento_halteres", "nome_exibicao": "Desenvolvimento com Halteres", "grupo": "Ombros", "secundario": "Tríceps", "movimento": "Empurrar", "tipo": "composto", "equipamento": "halteres", "uni_bi": "bilateral", "reps": "8-12", "inc": 2.0},
        {"nome_padrao": "desenvolvimento_arnold", "nome_exibicao": "Desenvolvimento Arnold", "grupo": "Ombros", "secundario": "Tríceps", "movimento": "Empurrar", "tipo": "composto", "equipamento": "halteres", "uni_bi": "bilateral", "reps": "8-12", "inc": 2.0},
        {"nome_padrao": "desenvolvimento_maquina", "nome_exibicao": "Desenvolvimento na Máquina", "grupo": "Ombros", "secundario": "Tríceps", "movimento": "Empurrar", "tipo": "composto", "equipamento": "maquina", "uni_bi": "bilateral", "reps": "8-12", "inc": 2.0},
        {"nome_padrao": "desenvolvimento_smith", "nome_exibicao": "Desenvolvimento no Smith", "grupo": "Ombros", "secundario": "Tríceps", "movimento": "Empurrar", "tipo": "composto", "equipamento": "smith", "uni_bi": "bilateral", "reps": "8-12", "inc": 2.0},
        {"nome_padrao": "elevacao_lateral_halteres", "nome_exibicao": "Elevação Lateral com Halteres", "grupo": "Ombros", "secundario": "Nenhum", "movimento": "Abdução", "tipo": "isolado", "equipamento": "halteres", "uni_bi": "bilateral", "reps": "10-12", "inc": 1.0},
        {"nome_padrao": "elevacao_lateral_polia", "nome_exibicao": "Elevação Lateral na Polia", "grupo": "Ombros", "secundario": "Nenhum", "movimento": "Abdução", "tipo": "isolado", "equipamento": "polia", "uni_bi": "unilateral", "reps": "10-12", "inc": 1.0},
        {"nome_padrao": "elevacao_lateral_maquina", "nome_exibicao": "Elevação Lateral na Máquina", "grupo": "Ombros", "secundario": "Nenhum", "movimento": "Abdução", "tipo": "isolado", "equipamento": "maquina", "uni_bi": "bilateral", "reps": "10-12", "inc": 1.0},
        {"nome_padrao": "elevacao_lateral_banco_inclinado", "nome_exibicao": "Elevação Lateral no Banco Inclinado", "grupo": "Ombros", "secundario": "Nenhum", "movimento": "Abdução", "tipo": "isolado", "equipamento": "halteres", "uni_bi": "unilateral", "reps": "10-12", "inc": 1.0},
        {"nome_padrao": "elevacao_frontal_halteres", "nome_exibicao": "Elevação Frontal com Halteres", "grupo": "Ombros", "secundario": "Peito Superior", "movimento": "Flexão", "tipo": "isolado", "equipamento": "halteres", "uni_bi": "bilateral", "reps": "10-12", "inc": 1.0},
        {"nome_padrao": "elevacao_frontal_barra", "nome_exibicao": "Elevação Frontal com Barra", "grupo": "Ombros", "secundario": "Peito Superior", "movimento": "Flexão", "tipo": "isolado", "equipamento": "barra", "uni_bi": "bilateral", "reps": "10-12", "inc": 2.0},
        {"nome_padrao": "elevacao_frontal_polia", "nome_exibicao": "Elevação Frontal na Polia (Corda ou Barra)", "grupo": "Ombros", "secundario": "Peito Superior", "movimento": "Flexão", "tipo": "isolado", "equipamento": "polia", "uni_bi": "bilateral", "reps": "10-12", "inc": 1.0},
        {"nome_padrao": "elevacao_frontal_anilha", "nome_exibicao": "Elevação Frontal com Anilha", "grupo": "Ombros", "secundario": "Peito Superior", "movimento": "Flexão", "tipo": "isolado", "equipamento": "outro", "uni_bi": "bilateral", "reps": "10-12", "inc": 1.0},
        {"nome_padrao": "crucifixo_inverso_halteres", "nome_exibicao": "Crucifixo Inverso com Halteres (Curvado)", "grupo": "Ombros", "secundario": "Trapézio, Romboides", "movimento": "Abdução Horizontal", "tipo": "isolado", "equipamento": "halteres", "uni_bi": "bilateral", "reps": "10-12", "inc": 1.0},
        {"nome_padrao": "crucifixo_inverso_maquina", "nome_exibicao": "Crucifixo Inverso na Máquina", "grupo": "Ombros", "secundario": "Trapézio, Romboides", "movimento": "Abdução Horizontal", "tipo": "isolado", "equipamento": "maquina", "uni_bi": "bilateral", "reps": "10-12", "inc": 2.0},
        {"nome_padrao": "crucifixo_inverso_polia", "nome_exibicao": "Crucifixo Inverso na Polia", "grupo": "Ombros", "secundario": "Trapézio", "movimento": "Abdução Horizontal", "tipo": "isolado", "equipamento": "polia", "uni_bi": "bilateral", "reps": "10-12", "inc": 1.0},
        {"nome_padrao": "face_pull_polia", "nome_exibicao": "Face Pull na Polia", "grupo": "Ombros", "secundario": "Trapézio Superior, Manguito", "movimento": "Puxar", "tipo": "composto", "equipamento": "polia", "uni_bi": "bilateral", "reps": "12-15", "inc": 1.0},
        {"nome_padrao": "remada_alta_barra", "nome_exibicao": "Remada Alta com Barra", "grupo": "Ombros", "secundario": "Trapézio, Bíceps", "movimento": "Puxar", "tipo": "composto", "equipamento": "barra", "uni_bi": "bilateral", "reps": "8-12", "inc": 2.0},
        {"nome_padrao": "remada_alta_polia", "nome_exibicao": "Remada Alta na Polia", "grupo": "Ombros", "secundario": "Trapézio", "movimento": "Puxar", "tipo": "composto", "equipamento": "polia", "uni_bi": "bilateral", "reps": "8-12", "inc": 1.0},
        {"nome_padrao": "rotacao_externa_polia", "nome_exibicao": "Rotação Externa na Polia (Manguito)", "grupo": "Ombros", "secundario": "Nenhum", "movimento": "Rotação", "tipo": "isolado", "equipamento": "polia", "uni_bi": "unilateral", "reps": "12-20", "inc": 1.0},

        # === BÍCEPS E ANTEBRAÇO (18 Exercícios) ===
        {"nome_padrao": "rosca_direta_barra_reta", "nome_exibicao": "Rosca Direta com Barra Reta", "grupo": "Bíceps", "secundario": "Antebraço", "movimento": "Flexão", "tipo": "isolado", "equipamento": "barra", "uni_bi": "bilateral", "reps": "8-12", "inc": 2.0},
        {"nome_padrao": "rosca_direta_barra_w", "nome_exibicao": "Rosca Direta com Barra W", "grupo": "Bíceps", "secundario": "Antebraço", "movimento": "Flexão", "tipo": "isolado", "equipamento": "barra", "uni_bi": "bilateral", "reps": "8-12", "inc": 2.0},
        {"nome_padrao": "rosca_direta_polia", "nome_exibicao": "Rosca Direta na Polia", "grupo": "Bíceps", "secundario": "Antebraço", "movimento": "Flexão", "tipo": "isolado", "equipamento": "polia", "uni_bi": "bilateral", "reps": "10-12", "inc": 1.0},
        {"nome_padrao": "rosca_alternada_halteres", "nome_exibicao": "Rosca Alternada com Halteres", "grupo": "Bíceps", "secundario": "Antebraço", "movimento": "Flexão", "tipo": "isolado", "equipamento": "halteres", "uni_bi": "unilateral", "reps": "8-12", "inc": 1.0},
        {"nome_padrao": "rosca_simultanea_halteres", "nome_exibicao": "Rosca Simultânea com Halteres", "grupo": "Bíceps", "secundario": "Antebraço", "movimento": "Flexão", "tipo": "isolado", "equipamento": "halteres", "uni_bi": "bilateral", "reps": "8-12", "inc": 2.0},
        {"nome_padrao": "rosca_martelo_halteres", "nome_exibicao": "Rosca Martelo com Halteres", "grupo": "Bíceps", "secundario": "Braquiorradial", "movimento": "Flexão", "tipo": "isolado", "equipamento": "halteres", "uni_bi": "bilateral", "reps": "8-12", "inc": 2.0},
        {"nome_padrao": "rosca_martelo_polia_corda", "nome_exibicao": "Rosca Martelo na Polia com Corda", "grupo": "Bíceps", "secundario": "Braquiorradial", "movimento": "Flexão", "tipo": "isolado", "equipamento": "polia", "uni_bi": "bilateral", "reps": "10-12", "inc": 1.0},
        {"nome_padrao": "rosca_scott_barra", "nome_exibicao": "Rosca Scott com Barra W", "grupo": "Bíceps", "secundario": "Nenhum", "movimento": "Flexão", "tipo": "isolado", "equipamento": "barra", "uni_bi": "bilateral", "reps": "8-12", "inc": 2.0},
        {"nome_padrao": "rosca_scott_maquina", "nome_exibicao": "Rosca Scott na Máquina", "grupo": "Bíceps", "secundario": "Nenhum", "movimento": "Flexão", "tipo": "isolado", "equipamento": "maquina", "uni_bi": "bilateral", "reps": "10-12", "inc": 2.0},
        {"nome_padrao": "rosca_concentrada_halter", "nome_exibicao": "Rosca Concentrada com Halter", "grupo": "Bíceps", "secundario": "Nenhum", "movimento": "Flexão", "tipo": "isolado", "equipamento": "halteres", "uni_bi": "unilateral", "reps": "10-12", "inc": 1.0},
        {"nome_padrao": "rosca_aranha_halteres", "nome_exibicao": "Rosca Aranha com Halteres (Banco Inclinado)", "grupo": "Bíceps", "secundario": "Nenhum", "movimento": "Flexão", "tipo": "isolado", "equipamento": "halteres", "uni_bi": "bilateral", "reps": "10-12", "inc": 2.0},
        {"nome_padrao": "rosca_inclinada_halteres", "nome_exibicao": "Rosca no Banco Inclinado com Halteres", "grupo": "Bíceps", "secundario": "Nenhum", "movimento": "Flexão", "tipo": "isolado", "equipamento": "halteres", "uni_bi": "bilateral", "reps": "10-12", "inc": 2.0},
        {"nome_padrao": "rosca_inversa_barra", "nome_exibicao": "Rosca Inversa com Barra", "grupo": "Bíceps", "secundario": "Antebraço (Braquiorradial)", "movimento": "Flexão", "tipo": "isolado", "equipamento": "barra", "uni_bi": "bilateral", "reps": "10-12", "inc": 2.0},
        {"nome_padrao": "rosca_inversa_polia", "nome_exibicao": "Rosca Inversa na Polia", "grupo": "Bíceps", "secundario": "Antebraço", "movimento": "Flexão", "tipo": "isolado", "equipamento": "polia", "uni_bi": "bilateral", "reps": "10-12", "inc": 1.0},
        {"nome_padrao": "flexao_punho_barra", "nome_exibicao": "Flexão de Punho com Barra (Antebraço)", "grupo": "Antebraço", "secundario": "Nenhum", "movimento": "Flexão", "tipo": "isolado", "equipamento": "barra", "uni_bi": "bilateral", "reps": "12-15", "inc": 1.0},
        {"nome_padrao": "flexao_punho_halteres", "nome_exibicao": "Flexão de Punho com Halteres", "grupo": "Antebraço", "secundario": "Nenhum", "movimento": "Flexão", "tipo": "isolado", "equipamento": "halteres", "uni_bi": "bilateral", "reps": "12-15", "inc": 1.0},
        {"nome_padrao": "extensao_punho_barra", "nome_exibicao": "Extensão de Punho com Barra", "grupo": "Antebraço", "secundario": "Nenhum", "movimento": "Extensão", "tipo": "isolado", "equipamento": "barra", "uni_bi": "bilateral", "reps": "12-15", "inc": 1.0},
        {"nome_padrao": "farmer_walk", "nome_exibicao": "Caminhada do Fazendeiro (Farmer's Walk)", "grupo": "Antebraço", "secundario": "Core, Trapézio", "movimento": "Isometria", "tipo": "composto", "equipamento": "halteres", "uni_bi": "bilateral", "reps": "N/A", "inc": 5.0},

        # === TRÍCEPS (16 Exercícios) ===
        {"nome_padrao": "triceps_pulley_barra_reta", "nome_exibicao": "Tríceps Pulley com Barra Reta", "grupo": "Tríceps", "secundario": "Nenhum", "movimento": "Extensão", "tipo": "isolado", "equipamento": "polia", "uni_bi": "bilateral", "reps": "10-12", "inc": 1.0},
        {"nome_padrao": "triceps_pulley_barra_v", "nome_exibicao": "Tríceps Pulley com Barra V", "grupo": "Tríceps", "secundario": "Nenhum", "movimento": "Extensão", "tipo": "isolado", "equipamento": "polia", "uni_bi": "bilateral", "reps": "10-12", "inc": 1.0},
        {"nome_padrao": "triceps_corda_polia", "nome_exibicao": "Tríceps Corda na Polia", "grupo": "Tríceps", "secundario": "Nenhum", "movimento": "Extensão", "tipo": "isolado", "equipamento": "polia", "uni_bi": "bilateral", "reps": "10-12", "inc": 1.0},
        {"nome_padrao": "triceps_unilateral_polia_supinada", "nome_exibicao": "Tríceps Unilateral na Polia (Pegada Inversa/Supinada)", "grupo": "Tríceps", "secundario": "Nenhum", "movimento": "Extensão", "tipo": "isolado", "equipamento": "polia", "uni_bi": "unilateral", "reps": "10-12", "inc": 1.0},
        {"nome_padrao": "triceps_unilateral_polia_pronada", "nome_exibicao": "Tríceps Unilateral na Polia (Pegada Pronada)", "grupo": "Tríceps", "secundario": "Nenhum", "movimento": "Extensão", "tipo": "isolado", "equipamento": "polia", "uni_bi": "unilateral", "reps": "10-12", "inc": 1.0},
        {"nome_padrao": "triceps_testa_barra_w", "nome_exibicao": "Tríceps Testa com Barra W", "grupo": "Tríceps", "secundario": "Nenhum", "movimento": "Extensão", "tipo": "isolado", "equipamento": "barra", "uni_bi": "bilateral", "reps": "8-12", "inc": 2.0},
        {"nome_padrao": "triceps_testa_halteres", "nome_exibicao": "Tríceps Testa com Halteres", "grupo": "Tríceps", "secundario": "Nenhum", "movimento": "Extensão", "tipo": "isolado", "equipamento": "halteres", "uni_bi": "bilateral", "reps": "8-12", "inc": 2.0},
        {"nome_padrao": "triceps_testa_polia", "nome_exibicao": "Tríceps Testa na Polia", "grupo": "Tríceps", "secundario": "Nenhum", "movimento": "Extensão", "tipo": "isolado", "equipamento": "polia", "uni_bi": "bilateral", "reps": "10-12", "inc": 1.0},
        {"nome_padrao": "triceps_frances_halter_bilateral", "nome_exibicao": "Tríceps Francês com 1 Halter (Bilateral)", "grupo": "Tríceps", "secundario": "Nenhum", "movimento": "Extensão", "tipo": "isolado", "equipamento": "halteres", "uni_bi": "bilateral", "reps": "8-12", "inc": 2.0},
        {"nome_padrao": "triceps_frances_halter_unilateral", "nome_exibicao": "Tríceps Francês Unilateral com Halter", "grupo": "Tríceps", "secundario": "Nenhum", "movimento": "Extensão", "tipo": "isolado", "equipamento": "halteres", "uni_bi": "unilateral", "reps": "10-12", "inc": 1.0},
        {"nome_padrao": "triceps_frances_polia_corda", "nome_exibicao": "Tríceps Francês na Polia com Corda", "grupo": "Tríceps", "secundario": "Nenhum", "movimento": "Extensão", "tipo": "isolado", "equipamento": "polia", "uni_bi": "bilateral", "reps": "10-12", "inc": 1.0},
        {"nome_padrao": "triceps_coice_halter", "nome_exibicao": "Tríceps Coice com Halter (Kickback)", "grupo": "Tríceps", "secundario": "Nenhum", "movimento": "Extensão", "tipo": "isolado", "equipamento": "halteres", "uni_bi": "unilateral", "reps": "10-12", "inc": 1.0},
        {"nome_padrao": "triceps_coice_polia", "nome_exibicao": "Tríceps Coice na Polia", "grupo": "Tríceps", "secundario": "Nenhum", "movimento": "Extensão", "tipo": "isolado", "equipamento": "polia", "uni_bi": "unilateral", "reps": "10-12", "inc": 1.0},
        {"nome_padrao": "mergulho_banco", "nome_exibicao": "Mergulho no Banco (Tríceps Banco)", "grupo": "Tríceps", "secundario": "Ombros, Peito", "movimento": "Empurrar", "tipo": "composto", "equipamento": "peso corporal", "uni_bi": "bilateral", "reps": "10-20", "inc": 0.0},
        {"nome_padrao": "mergulho_paralelas_triceps", "nome_exibicao": "Mergulho nas Paralelas (Tronco Reto)", "grupo": "Tríceps", "secundario": "Ombros, Peito", "movimento": "Empurrar", "tipo": "composto", "equipamento": "peso corporal", "uni_bi": "bilateral", "reps": "8-12", "inc": 0.0},
        {"nome_padrao": "supino_fechado_barra", "nome_exibicao": "Supino Fechado com Barra", "grupo": "Tríceps", "secundario": "Peito, Ombros", "movimento": "Empurrar", "tipo": "composto", "equipamento": "barra", "uni_bi": "bilateral", "reps": "8-10", "inc": 2.0},

        # === QUADRÍCEPS (16 Exercícios) ===
        {"nome_padrao": "agachamento_livre_barra", "nome_exibicao": "Agachamento Livre com Barra (Back Squat)", "grupo": "Quadríceps", "secundario": "Glúteos, Posteriores, Core", "movimento": "Agachar", "tipo": "composto", "equipamento": "barra", "uni_bi": "bilateral", "reps": "8-10", "inc": 2.0},
        {"nome_padrao": "agachamento_frontal_barra", "nome_exibicao": "Agachamento Frontal com Barra (Front Squat)", "grupo": "Quadríceps", "secundario": "Core", "movimento": "Agachar", "tipo": "composto", "equipamento": "barra", "uni_bi": "bilateral", "reps": "8-10", "inc": 2.0},
        {"nome_padrao": "agachamento_smith", "nome_exibicao": "Agachamento no Smith", "grupo": "Quadríceps", "secundario": "Glúteos", "movimento": "Agachar", "tipo": "composto", "equipamento": "smith", "uni_bi": "bilateral", "reps": "8-12", "inc": 2.0},
        {"nome_padrao": "agachamento_hack", "nome_exibicao": "Agachamento Hack Machine", "grupo": "Quadríceps", "secundario": "Glúteos", "movimento": "Agachar", "tipo": "composto", "equipamento": "maquina", "uni_bi": "bilateral", "reps": "8-12", "inc": 5.0},
        {"nome_padrao": "agachamento_pendulo", "nome_exibicao": "Agachamento Pêndulo", "grupo": "Quadríceps", "secundario": "Glúteos", "movimento": "Agachar", "tipo": "composto", "equipamento": "maquina", "uni_bi": "bilateral", "reps": "8-12", "inc": 5.0},
        {"nome_padrao": "agachamento_goblet", "nome_exibicao": "Agachamento Goblet (com Halter ou Kettlebell)", "grupo": "Quadríceps", "secundario": "Core", "movimento": "Agachar", "tipo": "composto", "equipamento": "halteres", "uni_bi": "bilateral", "reps": "10-12", "inc": 2.0},
        {"nome_padrao": "agachamento_sumo_halter", "nome_exibicao": "Agachamento Sumô com Halter", "grupo": "Quadríceps", "secundario": "Adutores, Glúteos", "movimento": "Agachar", "tipo": "composto", "equipamento": "halteres", "uni_bi": "bilateral", "reps": "10-12", "inc": 2.0},
        {"nome_padrao": "agachamento_bulgaro_halteres", "nome_exibicao": "Agachamento Búlgaro com Halteres", "grupo": "Quadríceps", "secundario": "Glúteos", "movimento": "Agachar", "tipo": "composto", "equipamento": "halteres", "uni_bi": "unilateral", "reps": "8-12", "inc": 2.0},
        {"nome_padrao": "agachamento_bulgaro_smith", "nome_exibicao": "Agachamento Búlgaro no Smith", "grupo": "Quadríceps", "secundario": "Glúteos", "movimento": "Agachar", "tipo": "composto", "equipamento": "smith", "uni_bi": "unilateral", "reps": "8-12", "inc": 2.0},
        {"nome_padrao": "leg_press_45", "nome_exibicao": "Leg Press 45 Graus", "grupo": "Quadríceps", "secundario": "Glúteos, Posteriores", "movimento": "Agachar", "tipo": "composto", "equipamento": "maquina", "uni_bi": "bilateral", "reps": "8-12", "inc": 5.0},
        {"nome_padrao": "leg_press_horizontal", "nome_exibicao": "Leg Press Horizontal", "grupo": "Quadríceps", "secundario": "Glúteos, Posteriores", "movimento": "Agachar", "tipo": "composto", "equipamento": "maquina", "uni_bi": "bilateral", "reps": "10-12", "inc": 5.0},
        {"nome_padrao": "leg_press_unilateral", "nome_exibicao": "Leg Press Unilateral", "grupo": "Quadríceps", "secundario": "Glúteos", "movimento": "Agachar", "tipo": "composto", "equipamento": "maquina", "uni_bi": "unilateral", "reps": "8-12", "inc": 5.0},
        {"nome_padrao": "passada_avanco_halteres", "nome_exibicao": "Passada / Avanço com Halteres", "grupo": "Quadríceps", "secundario": "Glúteos", "movimento": "Agachar", "tipo": "composto", "equipamento": "halteres", "uni_bi": "unilateral", "reps": "10-20", "inc": 2.0},
        {"nome_padrao": "afundo_smith", "nome_exibicao": "Afundo no Smith", "grupo": "Quadríceps", "secundario": "Glúteos", "movimento": "Agachar", "tipo": "composto", "equipamento": "smith", "uni_bi": "unilateral", "reps": "8-12", "inc": 2.0},
        {"nome_padrao": "cadeira_extensora", "nome_exibicao": "Cadeira Extensora", "grupo": "Quadríceps", "secundario": "Nenhum", "movimento": "Extensão", "tipo": "isolado", "equipamento": "maquina", "uni_bi": "bilateral", "reps": "10-12", "inc": 2.0},
        {"nome_padrao": "cadeira_extensora_unilateral", "nome_exibicao": "Cadeira Extensora Unilateral", "grupo": "Quadríceps", "secundario": "Nenhum", "movimento": "Extensão", "tipo": "isolado", "equipamento": "maquina", "uni_bi": "unilateral", "reps": "10-12", "inc": 2.0},

        # === POSTERIORES E GLÚTEOS (17 Exercícios) ===
        {"nome_padrao": "mesa_flexora", "nome_exibicao": "Mesa Flexora (Deitado)", "grupo": "Posteriores de coxa", "secundario": "Panturrilhas", "movimento": "Flexão", "tipo": "isolado", "equipamento": "maquina", "uni_bi": "bilateral", "reps": "10-12", "inc": 2.0},
        {"nome_padrao": "cadeira_flexora", "nome_exibicao": "Cadeira Flexora (Sentado)", "grupo": "Posteriores de coxa", "secundario": "Panturrilhas", "movimento": "Flexão", "tipo": "isolado", "equipamento": "maquina", "uni_bi": "bilateral", "reps": "10-12", "inc": 2.0},
        {"nome_padrao": "flexora_em_pe_unilateral", "nome_exibicao": "Flexora em Pé Unilateral", "grupo": "Posteriores de coxa", "secundario": "Panturrilhas", "movimento": "Flexão", "tipo": "isolado", "equipamento": "maquina", "uni_bi": "unilateral", "reps": "10-12", "inc": 2.0},
        {"nome_padrao": "stiff_barra", "nome_exibicao": "Stiff com Barra", "grupo": "Posteriores de coxa", "secundario": "Glúteos, Lombar", "movimento": "Dobrar", "tipo": "composto", "equipamento": "barra", "uni_bi": "bilateral", "reps": "8-12", "inc": 2.0},
        {"nome_padrao": "stiff_halteres", "nome_exibicao": "Stiff com Halteres", "grupo": "Posteriores de coxa", "secundario": "Glúteos, Lombar", "movimento": "Dobrar", "tipo": "composto", "equipamento": "halteres", "uni_bi": "bilateral", "reps": "8-12", "inc": 2.0},
        {"nome_padrao": "romanian_deadlift_barra", "nome_exibicao": "Romanian Deadlift (RDL) com Barra", "grupo": "Posteriores de coxa", "secundario": "Glúteos, Lombar", "movimento": "Dobrar", "tipo": "composto", "equipamento": "barra", "uni_bi": "bilateral", "reps": "8-12", "inc": 2.0},
        {"nome_padrao": "elevacao_pelvica_barra", "nome_exibicao": "Elevação Pélvica com Barra", "grupo": "Glúteos", "secundario": "Posteriores", "movimento": "Extensão do Quadril", "tipo": "composto", "equipamento": "barra", "uni_bi": "bilateral", "reps": "8-12", "inc": 5.0},
        {"nome_padrao": "elevacao_pelvica_maquina", "nome_exibicao": "Elevação Pélvica na Máquina", "grupo": "Glúteos", "secundario": "Posteriores", "movimento": "Extensão do Quadril", "tipo": "composto", "equipamento": "maquina", "uni_bi": "bilateral", "reps": "8-12", "inc": 5.0},
        {"nome_padrao": "elevacao_pelvica_smith", "nome_exibicao": "Elevação Pélvica no Smith", "grupo": "Glúteos", "secundario": "Posteriores", "movimento": "Extensão do Quadril", "tipo": "composto", "equipamento": "smith", "uni_bi": "bilateral", "reps": "8-12", "inc": 5.0},
        {"nome_padrao": "cadeira_abdutora", "nome_exibicao": "Cadeira Abdutora", "grupo": "Glúteos", "secundario": "Nenhum", "movimento": "Abdução", "tipo": "isolado", "equipamento": "maquina", "uni_bi": "bilateral", "reps": "12-15", "inc": 2.0},
        {"nome_padrao": "abducao_quadril_polia", "nome_exibicao": "Abdução de Quadril na Polia", "grupo": "Glúteos", "secundario": "Nenhum", "movimento": "Abdução", "tipo": "isolado", "equipamento": "polia", "uni_bi": "unilateral", "reps": "12-15", "inc": 1.0},
        {"nome_padrao": "extensao_quadril_polia", "nome_exibicao": "Glúteo na Polia (Extensão de Quadril)", "grupo": "Glúteos", "secundario": "Posteriores", "movimento": "Extensão do Quadril", "tipo": "isolado", "equipamento": "polia", "uni_bi": "unilateral", "reps": "12-15", "inc": 1.0},
        {"nome_padrao": "gluteo_maquina", "nome_exibicao": "Glúteo na Máquina (Coice)", "grupo": "Glúteos", "secundario": "Posteriores", "movimento": "Extensão do Quadril", "tipo": "isolado", "equipamento": "maquina", "uni_bi": "unilateral", "reps": "12-15", "inc": 2.0},
        {"nome_padrao": "gluteo_4_apoios", "nome_exibicao": "Glúteo 4 Apoios com Caneleira", "grupo": "Glúteos", "secundario": "Posteriores", "movimento": "Extensão do Quadril", "tipo": "isolado", "equipamento": "peso corporal", "uni_bi": "unilateral", "reps": "12-20", "inc": 1.0},
        {"nome_padrao": "cadeira_adutora", "nome_exibicao": "Cadeira Adutora", "grupo": "Adutores", "secundario": "Nenhum", "movimento": "Adução", "tipo": "isolado", "equipamento": "maquina", "uni_bi": "bilateral", "reps": "12-15", "inc": 2.0},
        {"nome_padrao": "aducao_quadril_polia", "nome_exibicao": "Adução de Quadril na Polia", "grupo": "Adutores", "secundario": "Nenhum", "movimento": "Adução", "tipo": "isolado", "equipamento": "polia", "uni_bi": "unilateral", "reps": "12-15", "inc": 1.0},
        {"nome_padrao": "bom_dia_barra", "nome_exibicao": "Bom Dia (Good Morning) com Barra", "grupo": "Posteriores de coxa", "secundario": "Glúteos, Lombar", "movimento": "Dobrar", "tipo": "composto", "equipamento": "barra", "uni_bi": "bilateral", "reps": "10-12", "inc": 2.0},

        # === PANTURRILHAS (8 Exercícios) ===
        {"nome_padrao": "panturrilha_em_pe_maquina", "nome_exibicao": "Panturrilha em Pé na Máquina", "grupo": "Panturrilhas", "secundario": "Nenhum", "movimento": "Flexão Plantar", "tipo": "isolado", "equipamento": "maquina", "uni_bi": "bilateral", "reps": "12-20", "inc": 2.0},
        {"nome_padrao": "panturrilha_em_pe_smith", "nome_exibicao": "Panturrilha em Pé no Smith", "grupo": "Panturrilhas", "secundario": "Nenhum", "movimento": "Flexão Plantar", "tipo": "isolado", "equipamento": "smith", "uni_bi": "bilateral", "reps": "12-20", "inc": 2.0},
        {"nome_padrao": "panturrilha_em_pe_livre", "nome_exibicao": "Panturrilha em Pé com Halteres (Degrau)", "grupo": "Panturrilhas", "secundario": "Nenhum", "movimento": "Flexão Plantar", "tipo": "isolado", "equipamento": "halteres", "uni_bi": "bilateral", "reps": "12-15", "inc": 2.0},
        {"nome_padrao": "panturrilha_sentado_maquina", "nome_exibicao": "Panturrilha Sentado na Máquina (Burrinho)", "grupo": "Panturrilhas", "secundario": "Sóleo", "movimento": "Flexão Plantar", "tipo": "isolado", "equipamento": "maquina", "uni_bi": "bilateral", "reps": "12-20", "inc": 2.0},
        {"nome_padrao": "panturrilha_leg_press", "nome_exibicao": "Panturrilha no Leg Press", "grupo": "Panturrilhas", "secundario": "Nenhum", "movimento": "Flexão Plantar", "tipo": "isolado", "equipamento": "maquina", "uni_bi": "bilateral", "reps": "12-20", "inc": 5.0},
        {"nome_padrao": "panturrilha_hack", "nome_exibicao": "Panturrilha no Hack Machine", "grupo": "Panturrilhas", "secundario": "Nenhum", "movimento": "Flexão Plantar", "tipo": "isolado", "equipamento": "maquina", "uni_bi": "bilateral", "reps": "12-20", "inc": 5.0},
        {"nome_padrao": "panturrilha_unilateral_degrau", "nome_exibicao": "Panturrilha Unilateral no Degrau", "grupo": "Panturrilhas", "secundario": "Nenhum", "movimento": "Flexão Plantar", "tipo": "isolado", "equipamento": "peso corporal", "uni_bi": "unilateral", "reps": "12-15", "inc": 0.0},
        {"nome_padrao": "tibial_anterior_maquina", "nome_exibicao": "Tibial Anterior na Máquina / Elástico", "grupo": "Panturrilhas", "secundario": "Nenhum", "movimento": "Dorsiflexão", "tipo": "isolado", "equipamento": "outro", "uni_bi": "bilateral", "reps": "12-15", "inc": 1.0},

        # === ABDÔMEN / CORE (18 Exercícios) ===
        {"nome_padrao": "abdominal_crunch_solo", "nome_exibicao": "Abdominal Crunch Tradicional (Solo)", "grupo": "Abdômen", "secundario": "Nenhum", "movimento": "Flexão Tronco", "tipo": "isolado", "equipamento": "peso corporal", "uni_bi": "bilateral", "reps": "15-25", "inc": 0.0},
        {"nome_padrao": "abdominal_maquina", "nome_exibicao": "Abdominal na Máquina", "grupo": "Abdômen", "secundario": "Nenhum", "movimento": "Flexão Tronco", "tipo": "isolado", "equipamento": "maquina", "uni_bi": "bilateral", "reps": "12-20", "inc": 2.0},
        {"nome_padrao": "abdominal_polia_corda", "nome_exibicao": "Abdominal na Polia Alta com Corda", "grupo": "Abdômen", "secundario": "Nenhum", "movimento": "Flexão Tronco", "tipo": "isolado", "equipamento": "polia", "uni_bi": "bilateral", "reps": "12-20", "inc": 1.0},
        {"nome_padrao": "abdominal_declinado", "nome_exibicao": "Abdominal no Banco Declinado", "grupo": "Abdômen", "secundario": "Nenhum", "movimento": "Flexão Tronco", "tipo": "isolado", "equipamento": "banco", "uni_bi": "bilateral", "reps": "12-15", "inc": 0.0},
        {"nome_padrao": "elevacao_pernas_solo", "nome_exibicao": "Elevação de Pernas no Solo (Infra)", "grupo": "Abdômen", "secundario": "Flexores de Quadril", "movimento": "Flexão Quadril", "tipo": "composto", "equipamento": "peso corporal", "uni_bi": "bilateral", "reps": "12-15", "inc": 0.0},
        {"nome_padrao": "elevacao_pernas_paralela", "nome_exibicao": "Elevação de Pernas na Paralela (Infra)", "grupo": "Abdômen", "secundario": "Flexores de Quadril", "movimento": "Flexão Quadril", "tipo": "composto", "equipamento": "peso corporal", "uni_bi": "bilateral", "reps": "12-20", "inc": 0.0},
        {"nome_padrao": "elevacao_pernas_pendurado", "nome_exibicao": "Elevação de Pernas Pendurado na Barra", "grupo": "Abdômen", "secundario": "Flexores de Quadril", "movimento": "Flexão Quadril", "tipo": "composto", "equipamento": "peso corporal", "uni_bi": "bilateral", "reps": "10-12", "inc": 0.0},
        {"nome_padrao": "abdominal_obliquo_solo", "nome_exibicao": "Abdominal Oblíquo no Solo", "grupo": "Abdômen", "secundario": "Nenhum", "movimento": "Rotação Tronco", "tipo": "isolado", "equipamento": "peso corporal", "uni_bi": "unilateral", "reps": "12-15", "inc": 0.0},
        {"nome_padrao": "russian_twist", "nome_exibicao": "Torção Russa (Russian Twist)", "grupo": "Abdômen", "secundario": "Oblíquos", "movimento": "Rotação Tronco", "tipo": "composto", "equipamento": "peso corporal", "uni_bi": "bilateral", "reps": "20-30", "inc": 0.0},
        {"nome_padrao": "woodchopper_polia", "nome_exibicao": "Lenhador na Polia (Woodchopper)", "grupo": "Abdômen", "secundario": "Oblíquos", "movimento": "Rotação Tronco", "tipo": "composto", "equipamento": "polia", "uni_bi": "unilateral", "reps": "12-15", "inc": 1.0},
        {"nome_padrao": "prancha_isometrica", "nome_exibicao": "Prancha Isométrica Frontal", "grupo": "Abdômen", "secundario": "Core", "movimento": "Isometria", "tipo": "composto", "equipamento": "peso corporal", "uni_bi": "bilateral", "reps": "N/A", "inc": 0.0},
        {"nome_padrao": "prancha_lateral", "nome_exibicao": "Prancha Isométrica Lateral", "grupo": "Abdômen", "secundario": "Oblíquos", "movimento": "Isometria", "tipo": "composto", "equipamento": "peso corporal", "uni_bi": "unilateral", "reps": "N/A", "inc": 0.0},
        {"nome_padrao": "roda_abdominal", "nome_exibicao": "Roda Abdominal (Ab Wheel)", "grupo": "Abdômen", "secundario": "Lombar, Ombros", "movimento": "Flexão Tronco", "tipo": "composto", "equipamento": "outro", "uni_bi": "bilateral", "reps": "8-15", "inc": 0.0},
        {"nome_padrao": "abdominal_remador", "nome_exibicao": "Abdominal Remador", "grupo": "Abdômen", "secundario": "Flexores Quadril", "movimento": "Flexão Tronco", "tipo": "composto", "equipamento": "peso corporal", "uni_bi": "bilateral", "reps": "15-25", "inc": 0.0},
        {"nome_padrao": "abdominal_bicicleta", "nome_exibicao": "Abdominal Bicicleta (Bicycle Crunch)", "grupo": "Abdômen", "secundario": "Oblíquos", "movimento": "Rotação Tronco", "tipo": "composto", "equipamento": "peso corporal", "uni_bi": "bilateral", "reps": "20-30", "inc": 0.0},
        {"nome_padrao": "v_sit_up", "nome_exibicao": "Abdominal em V (V-Up)", "grupo": "Abdômen", "secundario": "Flexores Quadril", "movimento": "Flexão Tronco", "tipo": "composto", "equipamento": "peso corporal", "uni_bi": "bilateral", "reps": "10-20", "inc": 0.0},
        {"nome_padrao": "hollow_body_hold", "nome_exibicao": "Isometria em Canoa (Hollow Body Hold)", "grupo": "Abdômen", "secundario": "Core", "movimento": "Isometria", "tipo": "composto", "equipamento": "peso corporal", "uni_bi": "bilateral", "reps": "N/A", "inc": 0.0},
        {"nome_padrao": "vacuum_abdominal", "nome_exibicao": "Stomach Vacuum (Vácuo Abdominal)", "grupo": "Abdômen", "secundario": "Transverso do Abdômen", "movimento": "Isometria", "tipo": "isolado", "equipamento": "peso corporal", "uni_bi": "bilateral", "reps": "N/A", "inc": 0.0},
    ]

    for ex in exercicios:
        # LÓGICA DE CLASSIFICAÇÃO AUTOMÁTICA
        usa_c = True
        
        # Se for peso corporal ou isometria (como Prancha), desativa a carga
        if ex.get("equipamento") == "peso corporal" or ex.get("movimento") == "Isometria":
            usa_c = False
            
        # Abdominais só usam carga se forem em aparelhos (máquina/polia)
        if ex.get("grupo") == "Abdômen" and ex.get("equipamento") not in ["maquina", "polia"]:
            usa_c = False

        novo_ex = CatalogoExercicio(
            nome_padrao=ex["nome_padrao"], 
            nome_exibicao=ex["nome_exibicao"],
            grupo_muscular_principal=ex["grupo"], 
            grupos_musculares_secundarios=ex["secundario"],
            categoria_movimento=ex["movimento"], 
            tipo_exercicio=ex["tipo"],
            equipamento=ex["equipamento"], 
            unilateral_ou_bilateral=ex["uni_bi"],
            faixa_reps_padrao=ex["reps"], 
            incremento_padrao_carga=ex["inc"],
            usa_carga=usa_c 
        )
        db.add(novo_ex)
    db.commit()

# --- INICIALIZAÇÃO AUTOMÁTICA ---
@app.on_event("startup")
def startup_event():
    db = SessionLocal()
    semear_catalogo_exercicios(db)
    db.close()

# --- SCHEMAS ---
class SessaoIniciarReq(BaseModel): treino_id: int
class SerieRegistrarReq(BaseModel): exercicio_id: int; carga: Optional[float] = None; repeticoes: int
class AtualizarPesoReq(BaseModel): peso_atual: float; meta_peso: float
class AdicionarAlimentoReq(BaseModel): refeicao: str; nome_alimento: str; kcal: float; proteina: float; carbo: float; gordura: float
class AtualizarRegistroReq(BaseModel): nome_alimento: str; kcal: float; proteina: float; carbo: float; gordura: float
class AtualizarMetasReq(BaseModel): kcal: float; proteina: float; carbo: float; gordura: float
class AlimentoPersonalizadoReq(BaseModel): nome: str; porcao_g: float; kcal: float; proteina: float; carbo: float; gordura: float
class ExercicioFichaReq(BaseModel): catalogo_id: int; series: int; reps: str; descanso: int; observacao: str = ""
class CriarFichaReq(BaseModel): nome: str; foco: str; exercicios: list[ExercicioFichaReq]
class SessaoIniciarReq(BaseModel): treino_id: int
# --- LÓGICA DE DATA (01:00 AM) ---
def obter_data_diario():
    agora = datetime.now()
    if agora.hour < 1:
        return (agora - timedelta(days=1)).strftime("%Y-%m-%d")
    return agora.strftime("%Y-%m-%d")

CATALOGO_ALIMENTOS_SIMPLES = [
    # === CEREAIS, RAÍZES E TUBÉRCULOS (Carboidratos) ===
    {"id": 1, "nome": "Arroz Branco (Cozido)", "porcao": "100g", "ref_g": 100.0, "kcal": 130.0, "p": 2.5, "c": 28.1, "g": 0.2},
    {"id": 2, "nome": "Arroz Integral (Cozido)", "porcao": "100g", "ref_g": 100.0, "kcal": 124.0, "p": 2.6, "c": 25.8, "g": 1.0},
    {"id": 3, "nome": "Feijão Carioca (Cozido)", "porcao": "100g", "ref_g": 100.0, "kcal": 76.0, "p": 4.8, "c": 13.6, "g": 0.5},
    {"id": 4, "nome": "Feijão Preto (Cozido)", "porcao": "100g", "ref_g": 100.0, "kcal": 77.0, "p": 4.5, "c": 14.0, "g": 0.5},
    {"id": 5, "nome": "Batata Doce (Cozida)", "porcao": "100g", "ref_g": 100.0, "kcal": 86.0, "p": 1.6, "c": 20.1, "g": 0.1},
    {"id": 6, "nome": "Batata Inglesa (Cozida)", "porcao": "100g", "ref_g": 100.0, "kcal": 87.0, "p": 1.9, "c": 20.1, "g": 0.1},
    {"id": 7, "nome": "Mandioca / Macaxeira (Cozida)", "porcao": "100g", "ref_g": 100.0, "kcal": 125.0, "p": 0.8, "c": 30.1, "g": 0.3},
    {"id": 8, "nome": "Inhame (Cozido)", "porcao": "100g", "ref_g": 100.0, "kcal": 97.0, "p": 2.1, "c": 23.2, "g": 0.2},
    {"id": 9, "nome": "Macarrão de Trigo (Cozido)", "porcao": "100g", "ref_g": 100.0, "kcal": 158.0, "p": 5.8, "c": 30.9, "g": 0.9},
    {"id": 10, "nome": "Macarrão Integral (Cozido)", "porcao": "100g", "ref_g": 100.0, "kcal": 124.0, "p": 5.3, "c": 26.5, "g": 0.5},
    {"id": 11, "nome": "Aveia em Flocos", "porcao": "100g", "ref_g": 100.0, "kcal": 394.0, "p": 14.3, "c": 66.6, "g": 7.3},
    {"id": 12, "nome": "Farinha de Tapioca / Goma", "porcao": "100g", "ref_g": 100.0, "kcal": 336.0, "p": 1.3, "c": 81.1, "g": 0.3},
    {"id": 13, "nome": "Pão Francês", "porcao": "100g", "ref_g": 100.0, "kcal": 300.0, "p": 8.0, "c": 58.6, "g": 3.1},
    {"id": 14, "nome": "Pão de Forma Tradicional", "porcao": "100g", "ref_g": 100.0, "kcal": 253.0, "p": 8.3, "c": 49.9, "g": 1.5},
    {"id": 15, "nome": "Pão de Forma Integral", "porcao": "100g", "ref_g": 100.0, "kcal": 253.0, "p": 9.4, "c": 49.9, "g": 3.7},
    {"id": 16, "nome": "Farinha de Mandioca", "porcao": "100g", "ref_g": 100.0, "kcal": 361.0, "p": 1.2, "c": 87.9, "g": 0.3},
    {"id": 17, "nome": "Milho Verde (Enlatado)", "porcao": "100g", "ref_g": 100.0, "kcal": 98.0, "p": 3.2, "c": 17.1, "g": 2.4},
    {"id": 18, "nome": "Grão-de-bico (Cozido)", "porcao": "100g", "ref_g": 100.0, "kcal": 164.0, "p": 8.8, "c": 27.4, "g": 2.5},
    {"id": 19, "nome": "Lentilha (Cozida)", "porcao": "100g", "ref_g": 100.0, "kcal": 116.0, "p": 9.0, "c": 20.1, "g": 0.4},

    # === CARNES, AVES E PEIXES (Proteínas) ===
    {"id": 20, "nome": "Peito de Frango (Grelhado)", "porcao": "100g", "ref_g": 100.0, "kcal": 159.0, "p": 32.0, "c": 0.0, "g": 2.5},
    {"id": 21, "nome": "Sobrecoxa de Frango (Assada s/ pele)", "porcao": "100g", "ref_g": 100.0, "kcal": 233.0, "p": 26.0, "c": 0.0, "g": 13.5},
    {"id": 22, "nome": "Patinho Bovino (Grelhado/Moído)", "porcao": "100g", "ref_g": 100.0, "kcal": 219.0, "p": 35.9, "c": 0.0, "g": 7.3},
    {"id": 23, "nome": "Coxão Mole Bovino (Grelhado)", "porcao": "100g", "ref_g": 100.0, "kcal": 226.0, "p": 32.4, "c": 0.0, "g": 9.8},
    {"id": 24, "nome": "Contrafilé Bovino (Grelhado)", "porcao": "100g", "ref_g": 100.0, "kcal": 278.0, "p": 29.9, "c": 0.0, "g": 16.6},
    {"id": 25, "nome": "Alcatra Bovina (Grelhada)", "porcao": "100g", "ref_g": 100.0, "kcal": 241.0, "p": 31.9, "c": 0.0, "g": 11.6},
    {"id": 26, "nome": "Fígado Bovino (Grelhado)", "porcao": "100g", "ref_g": 100.0, "kcal": 225.0, "p": 29.9, "c": 4.2, "g": 9.0},
    {"id": 27, "nome": "Lombo Suíno (Assado)", "porcao": "100g", "ref_g": 100.0, "kcal": 210.0, "p": 35.7, "c": 0.0, "g": 6.3},
    {"id": 28, "nome": "Filé de Tilápia (Grelhado)", "porcao": "100g", "ref_g": 100.0, "kcal": 128.0, "p": 26.1, "c": 0.0, "g": 2.6},
    {"id": 29, "nome": "Salmão (Grelhado)", "porcao": "100g", "ref_g": 100.0, "kcal": 220.0, "p": 23.4, "c": 0.0, "g": 13.3},
    {"id": 30, "nome": "Atum em Conserva (Óleo, escorrido)", "porcao": "100g", "ref_g": 100.0, "kcal": 166.0, "p": 26.2, "c": 0.0, "g": 6.0},
    {"id": 31, "nome": "Atum em Conserva (Água)", "porcao": "100g", "ref_g": 100.0, "kcal": 113.0, "p": 25.5, "c": 0.0, "g": 0.8},
    {"id": 32, "nome": "Sardinha em Conserva (Óleo)", "porcao": "100g", "ref_g": 100.0, "kcal": 285.0, "p": 23.8, "c": 0.0, "g": 20.3},

    # === OVOS E LATICÍNIOS ===
    {"id": 33, "nome": "Ovo de Galinha Inteiro (Cozido)", "porcao": "100g (Aprox. 2 un)", "ref_g": 100.0, "kcal": 146.0, "p": 13.3, "c": 0.6, "g": 9.5},
    {"id": 34, "nome": "Clara de Ovo (Cozida)", "porcao": "100g", "ref_g": 100.0, "kcal": 54.0, "p": 13.0, "c": 0.0, "g": 0.0},
    {"id": 35, "nome": "Gema de Ovo (Cozida)", "porcao": "100g", "ref_g": 100.0, "kcal": 322.0, "p": 15.9, "c": 3.6, "g": 26.5},
    {"id": 36, "nome": "Leite Integral (Fluido)", "porcao": "100ml", "ref_g": 100.0, "kcal": 60.0, "p": 3.0, "c": 4.7, "g": 3.0},
    {"id": 37, "nome": "Leite Desnatado (Fluido)", "porcao": "100ml", "ref_g": 100.0, "kcal": 35.0, "p": 3.4, "c": 5.0, "g": 0.0},
    {"id": 38, "nome": "Iogurte Natural Integral", "porcao": "100g", "ref_g": 100.0, "kcal": 61.0, "p": 3.5, "c": 4.7, "g": 3.3},
    {"id": 39, "nome": "Iogurte Natural Desnatado", "porcao": "100g", "ref_g": 100.0, "kcal": 41.0, "p": 3.8, "c": 5.8, "g": 0.3},
    {"id": 40, "nome": "Queijo Mussarela", "porcao": "100g", "ref_g": 100.0, "kcal": 330.0, "p": 22.6, "c": 3.0, "g": 25.2},
    {"id": 41, "nome": "Queijo Prato", "porcao": "100g", "ref_g": 100.0, "kcal": 360.0, "p": 22.7, "c": 1.9, "g": 29.1},
    {"id": 42, "nome": "Queijo Minas Frescal", "porcao": "100g", "ref_g": 100.0, "kcal": 264.0, "p": 17.4, "c": 3.2, "g": 20.2},
    {"id": 43, "nome": "Requeijão Cremoso", "porcao": "100g", "ref_g": 100.0, "kcal": 257.0, "p": 9.6, "c": 2.4, "g": 23.4},
    {"id": 44, "nome": "Creme de Leite", "porcao": "100g", "ref_g": 100.0, "kcal": 221.0, "p": 2.0, "c": 3.5, "g": 22.5},

    # === FRUTAS ===
    {"id": 45, "nome": "Banana Prata (Crua)", "porcao": "100g", "ref_g": 100.0, "kcal": 98.0, "p": 1.3, "c": 26.0, "g": 0.1},
    {"id": 46, "nome": "Banana Nanica (Crua)", "porcao": "100g", "ref_g": 100.0, "kcal": 92.0, "p": 1.4, "c": 23.8, "g": 0.1},
    {"id": 47, "nome": "Maçã Fuji (com casca)", "porcao": "100g", "ref_g": 100.0, "kcal": 52.0, "p": 0.3, "c": 15.2, "g": 0.0},
    {"id": 48, "nome": "Laranja Pera", "porcao": "100g", "ref_g": 100.0, "kcal": 37.0, "p": 1.0, "c": 8.9, "g": 0.1},
    {"id": 49, "nome": "Mamão Papaia", "porcao": "100g", "ref_g": 100.0, "kcal": 40.0, "p": 0.5, "c": 10.4, "g": 0.1},
    {"id": 50, "nome": "Mamão Formosa", "porcao": "100g", "ref_g": 100.0, "kcal": 45.0, "p": 0.8, "c": 11.6, "g": 0.1},
    {"id": 51, "nome": "Melancia", "porcao": "100g", "ref_g": 100.0, "kcal": 33.0, "p": 0.9, "c": 8.1, "g": 0.0},
    {"id": 52, "nome": "Melão", "porcao": "100g", "ref_g": 100.0, "kcal": 29.0, "p": 0.7, "c": 7.5, "g": 0.0},
    {"id": 53, "nome": "Abacaxi", "porcao": "100g", "ref_g": 100.0, "kcal": 48.0, "p": 0.9, "c": 12.3, "g": 0.1},
    {"id": 54, "nome": "Manga Palmer", "porcao": "100g", "ref_g": 100.0, "kcal": 72.0, "p": 0.4, "c": 19.4, "g": 0.0},
    {"id": 55, "nome": "Uva Itália", "porcao": "100g", "ref_g": 100.0, "kcal": 53.0, "p": 0.7, "c": 13.6, "g": 0.2},
    {"id": 56, "nome": "Morango", "porcao": "100g", "ref_g": 100.0, "kcal": 30.0, "p": 0.9, "c": 6.8, "g": 0.3},
    {"id": 57, "nome": "Abacate", "porcao": "100g", "ref_g": 100.0, "kcal": 96.0, "p": 1.2, "c": 6.0, "g": 8.4},
    {"id": 58, "nome": "Goiaba", "porcao": "100g", "ref_g": 100.0, "kcal": 54.0, "p": 1.1, "c": 13.0, "g": 0.4},
    {"id": 59, "nome": "Pera", "porcao": "100g", "ref_g": 100.0, "kcal": 53.0, "p": 0.3, "c": 14.0, "g": 0.1},

    # === VEGETAIS E HORTALIÇAS ===
    {"id": 60, "nome": "Alface (Crespa/Lisa)", "porcao": "100g", "ref_g": 100.0, "kcal": 11.0, "p": 1.3, "c": 1.7, "g": 0.2},
    {"id": 61, "nome": "Tomate", "porcao": "100g", "ref_g": 100.0, "kcal": 15.0, "p": 1.1, "c": 3.1, "g": 0.2},
    {"id": 62, "nome": "Cebola (Crua)", "porcao": "100g", "ref_g": 100.0, "kcal": 39.0, "p": 1.7, "c": 8.9, "g": 0.1},
    {"id": 63, "nome": "Alho (Cru)", "porcao": "100g", "ref_g": 100.0, "kcal": 113.0, "p": 7.0, "c": 23.9, "g": 0.2},
    {"id": 64, "nome": "Cenoura (Crua)", "porcao": "100g", "ref_g": 100.0, "kcal": 34.0, "p": 1.3, "c": 7.7, "g": 0.2},
    {"id": 65, "nome": "Cenoura (Cozida)", "porcao": "100g", "ref_g": 100.0, "kcal": 30.0, "p": 0.8, "c": 6.7, "g": 0.2},
    {"id": 66, "nome": "Beterraba (Crua)", "porcao": "100g", "ref_g": 100.0, "kcal": 49.0, "p": 1.9, "c": 11.1, "g": 0.1},
    {"id": 67, "nome": "Brócolis (Cozido)", "porcao": "100g", "ref_g": 100.0, "kcal": 25.0, "p": 2.1, "c": 4.4, "g": 0.5},
    {"id": 68, "nome": "Couve-flor (Cozida)", "porcao": "100g", "ref_g": 100.0, "kcal": 23.0, "p": 1.2, "c": 5.2, "g": 0.2},
    {"id": 69, "nome": "Abobrinha (Cozida)", "porcao": "100g", "ref_g": 100.0, "kcal": 15.0, "p": 1.1, "c": 3.0, "g": 0.2},
    {"id": 70, "nome": "Abóbora Cabotiá (Cozida)", "porcao": "100g", "ref_g": 100.0, "kcal": 48.0, "p": 1.4, "c": 10.8, "g": 0.7},
    {"id": 71, "nome": "Chuchu (Cozido)", "porcao": "100g", "ref_g": 100.0, "kcal": 11.0, "p": 0.4, "c": 2.4, "g": 0.0},
    {"id": 72, "nome": "Pepino (Cru)", "porcao": "100g", "ref_g": 100.0, "kcal": 10.0, "p": 0.9, "c": 2.0, "g": 0.0},
    {"id": 73, "nome": "Pimentão (Verde/Vermelho)", "porcao": "100g", "ref_g": 100.0, "kcal": 21.0, "p": 1.1, "c": 4.9, "g": 0.2},
    {"id": 74, "nome": "Couve Manteiga (Refogada)", "porcao": "100g", "ref_g": 100.0, "kcal": 90.0, "p": 3.3, "c": 8.7, "g": 5.5},

    # === ÓLEOS, GORDURAS E OLEAGINOSAS ===
    {"id": 75, "nome": "Azeite de Oliva Extra Virgem", "porcao": "100ml", "ref_g": 100.0, "kcal": 884.0, "p": 0.0, "c": 0.0, "g": 100.0},
    {"id": 76, "nome": "Óleo de Soja", "porcao": "100ml", "ref_g": 100.0, "kcal": 884.0, "p": 0.0, "c": 0.0, "g": 100.0},
    {"id": 77, "nome": "Manteiga (Com Sal)", "porcao": "100g", "ref_g": 100.0, "kcal": 726.0, "p": 0.4, "c": 0.1, "g": 82.0},
    {"id": 78, "nome": "Margarina (Com Sal)", "porcao": "100g", "ref_g": 100.0, "kcal": 717.0, "p": 0.1, "c": 0.0, "g": 81.0},
    {"id": 79, "nome": "Pasta de Amendoim Integral", "porcao": "100g", "ref_g": 100.0, "kcal": 598.0, "p": 28.0, "c": 20.0, "g": 49.0},
    {"id": 80, "nome": "Amendoim Torrado", "porcao": "100g", "ref_g": 100.0, "kcal": 606.0, "p": 22.5, "c": 21.3, "g": 54.0},

    # === AÇÚCARES, DOCES E BEBIDAS ===
    {"id": 81, "nome": "Açúcar Refinado", "porcao": "100g", "ref_g": 100.0, "kcal": 387.0, "p": 0.0, "c": 99.9, "g": 0.0},
    {"id": 82, "nome": "Açúcar Mascavo", "porcao": "100g", "ref_g": 100.0, "kcal": 369.0, "p": 0.8, "c": 94.9, "g": 0.0},
    {"id": 83, "nome": "Mel de Abelha", "porcao": "100g", "ref_g": 100.0, "kcal": 304.0, "p": 0.3, "c": 82.4, "g": 0.0},
    {"id": 84, "nome": "Chocolate ao Leite", "porcao": "100g", "ref_g": 100.0, "kcal": 540.0, "p": 6.8, "c": 57.3, "g": 31.7},
    {"id": 85, "nome": "Chocolate Amargo (Meio Amargo)", "porcao": "100g", "ref_g": 100.0, "kcal": 519.0, "p": 4.9, "c": 59.8, "g": 29.8},
    {"id": 86, "nome": "Café (Infusão/Sem Açúcar)", "porcao": "100ml", "ref_g": 100.0, "kcal": 1.0, "p": 0.1, "c": 0.0, "g": 0.0},
    {"id": 87, "nome": "Suco de Laranja (Natural)", "porcao": "100ml", "ref_g": 100.0, "kcal": 41.0, "p": 0.7, "c": 9.3, "g": 0.1},
    {"id": 88, "nome": "Whey Protein Concentrado", "porcao": "100g", "ref_g": 100.0, "kcal": 400.0, "p": 80.0, "c": 10.0, "g": 5.0},
    {"id": 89, "nome": "Presunto Cozido", "porcao": "100g", "ref_g": 100.0, "kcal": 107.0, "p": 14.1, "c": 1.5, "g": 4.5},
    {"id": 90, "nome": "Peito de Peru Defumado", "porcao": "100g", "ref_g": 100.0, "kcal": 104.0, "p": 21.0, "c": 1.0, "g": 1.5},
]

# --- ROTA DO CATÁLOGO DE EXERCÍCIOS ---
@app.get("/catalogo/exercicios")
def buscar_catalogo_exercicios(q: str = "", grupo: str = "", db: Session = Depends(get_db)):
    query = db.query(CatalogoExercicio).filter(CatalogoExercicio.ativo == True)
    if q: query = query.filter(CatalogoExercicio.nome_exibicao.ilike(f"%{q}%"))
    if grupo: query = query.filter(CatalogoExercicio.grupo_muscular_principal == grupo)
    
    resultados = query.order_by(CatalogoExercicio.grupo_muscular_principal, CatalogoExercicio.nome_exibicao).all()
    return [{"id": r.id, "nome": r.nome_exibicao, "grupo": r.grupo_muscular_principal, "tipo": r.tipo_exercicio, "equipamento": r.equipamento, "reps_padrao": r.faixa_reps_padrao, "inc_padrao": r.incremento_padrao_carga, "usa_carga": r.usa_carga} for r in resultados]
# --- ROTAS GERAIS DE TREINO, PERFIL E NUTRIÇÃO ---
@app.post("/fichas")
def criar_ficha(req: CriarFichaReq, db: Session = Depends(get_db)):
    nova_ficha = FichaTreino(usuario_id=1, nome=req.nome, foco=req.foco)
    db.add(nova_ficha); db.commit(); db.refresh(nova_ficha)
    for ex in req.exercicios:
        db.add(FichaExercicio(ficha_id=nova_ficha.id, catalogo_id=ex.catalogo_id, series=ex.series, reps=ex.reps, descanso=ex.descanso, observacao=ex.observacao))
    db.commit()
    return {"status": "sucesso"}
@app.get("/treinos")
def listar_treinos(db: Session = Depends(get_db)):
    fichas = db.query(FichaTreino).filter(FichaTreino.usuario_id == 1).all()
    resultado = []
    for f in fichas:
        exs = db.query(FichaExercicio, CatalogoExercicio).join(CatalogoExercicio, FichaExercicio.catalogo_id == CatalogoExercicio.id).filter(FichaExercicio.ficha_id == f.id).all()
        
        lista_ex = [{"id": ce.id, "nome": ce.nome_exibicao, "series": fe.series, "reps": fe.reps, "grupo": ce.grupo_muscular_principal, "usa_carga": ce.usa_carga} for fe, ce in exs]
        
        resultado.append({"id": f.id, "treino": f.nome, "foco": f.foco, "nivel": "Personalizado", "exercicios": lista_ex})

    return resultado
@app.post("/sessao/iniciar")
def iniciar_sessao(req: SessaoIniciarReq, db: Session = Depends(get_db)): nova_sessao = models.SessaoTreino(treino_id=req.treino_id, data_inicio=datetime.now(), status='em_andamento'); db.add(nova_sessao); db.commit(); db.refresh(nova_sessao); return {"sessao_id": nova_sessao.id}
@app.post("/sessao/{sessao_id}/registrar_serie")
def registrar_serie(sessao_id: int, req: SerieRegistrarReq, db: Session = Depends(get_db)):
    ex_catalogo = db.query(CatalogoExercicio).filter(CatalogoExercicio.id == req.exercicio_id).first()
    if not ex_catalogo: raise HTTPException(404, "Exercicio nao encontrado")
    
    if ex_catalogo.usa_carga and req.carga is None:
        raise HTTPException(400, "Este exercício exige o registro de carga (kg).")
    
    carga_final = req.carga if ex_catalogo.usa_carga else None

    # Salva a série nova
    db.add(models.SerieRegistrada(sessao_id=sessao_id, exercicio_id=req.exercicio_id, carga=carga_final, repeticoes=req.repeticoes))
    db.commit()
    series_do_ex = db.query(models.SerieRegistrada).filter(
        models.SerieRegistrada.exercicio_id == req.exercicio_id
    ).order_by(models.SerieRegistrada.id.desc()).all()
    
    if len(series_do_ex) > 4:
        for s_del in series_do_ex[4:]:
            db.delete(s_del)
        db.commit()

    return {"status": "sucesso"}

@app.get("/exercicio/{exercicio_id}/historico")
def buscar_historico(exercicio_id: int, db: Session = Depends(get_db)): 
    return list(reversed([{"carga": s.carga, "repeticoes": s.repeticoes} for s in db.query(models.SerieRegistrada).filter(models.SerieRegistrada.exercicio_id == exercicio_id).order_by(models.SerieRegistrada.id.desc()).limit(4).all()]))
@app.post("/sessao/{sessao_id}/finalizar")
def finalizar_sessao(sessao_id: int, db: Session = Depends(get_db)): sessao = db.query(models.SessaoTreino).filter(models.SessaoTreino.id == sessao_id).first(); sessao.status = 'finalizada'; db.commit(); return {"status": "sucesso"}
@app.get("/perfil/{usuario_id}")
def obter_perfil(usuario_id: int, db: Session = Depends(get_db)): user = db.query(models.Usuario).filter(models.Usuario.id == usuario_id).first(); return {"nome": user.nome, "peso_atual": user.peso_atual, "meta_peso": user.meta_peso} if user else {"nome": "Markin", "peso_atual": 70.0, "meta_peso": 80.0}
@app.put("/perfil/{usuario_id}/peso")
def atualizar_peso(usuario_id: int, req: AtualizarPesoReq, db: Session = Depends(get_db)): user = db.query(models.Usuario).filter(models.Usuario.id == usuario_id).first(); user.peso_atual = req.peso_atual if user else req.peso_atual; user.meta_peso = req.meta_peso if user else req.meta_peso; db.commit() if user else db.add(models.Usuario(id=usuario_id, nome="Markin", peso_atual=req.peso_atual, meta_peso=req.meta_peso)); db.commit(); return {"status": "sucesso"}
@app.get("/perfil/{usuario_id}/recordes")
def obter_recordes(usuario_id: int, db: Session = Depends(get_db)):
    recordes = db.query(CatalogoExercicio.id, CatalogoExercicio.nome_exibicao, func.max(models.SerieRegistrada.carga)).join(models.SerieRegistrada, CatalogoExercicio.id == models.SerieRegistrada.exercicio_id).filter(CatalogoExercicio.usa_carga == True).group_by(CatalogoExercicio.id, CatalogoExercicio.nome_exibicao).all()
    return [{"exercicio_id": r[0], "exercicio": r[1], "carga": r[2]} for r in recordes if r[2] is not None]
@app.get("/exercicio/{exercicio_id}/evolucao")
def obter_evolucao_exercicio(exercicio_id: int, db: Session = Depends(get_db)): historico = db.query(models.SerieRegistrada.carga, models.SerieRegistrada.repeticoes, models.SessaoTreino.data_inicio).join(models.SessaoTreino, models.SerieRegistrada.sessao_id == models.SessaoTreino.id).filter(models.SerieRegistrada.exercicio_id == exercicio_id).order_by(models.SessaoTreino.data_inicio.desc()).all(); return {"pr": max([h.carga for h in historico]) if historico else 0, "historico": [{"data": h.data_inicio.strftime("%d/%m/%Y"), "carga": h.carga, "repeticoes": h.repeticoes} for h in historico]}
@app.get("/alimentos/buscar")
def buscar_alimentos(q: str = ""): return [a for a in CATALOGO_ALIMENTOS_SIMPLES if q.lower() in a["nome"].lower()] if q else CATALOGO_ALIMENTOS_SIMPLES
@app.get("/nutricao/{usuario_id}/hoje")
def obter_diario_nutricao(usuario_id: int, db: Session = Depends(get_db)):
    hoje = obter_data_diario()
    registros = db.query(RegistroNutricao).filter(RegistroNutricao.usuario_id == usuario_id, RegistroNutricao.data_registro == hoje).all()
    meta_db = db.query(MetaNutricao).filter(MetaNutricao.usuario_id == usuario_id).first()
    metas = {"kcal": meta_db.kcal, "proteina": meta_db.proteina, "carbo": meta_db.carbo, "gordura": meta_db.gordura} if meta_db else {"kcal": 2800, "proteina": 160, "carbo": 350, "gordura": 80}
    consumido = {"kcal": 0, "proteina": 0, "carbo": 0, "gordura": 0}; refeicoes = {"Cafe da Manha": [], "Almoco": [], "Lanche": [], "Jantar": [], "Ceia": []}
    for r in registros:
        consumido["kcal"] += r.kcal; consumido["proteina"] += r.proteina; consumido["carbo"] += r.carbo; consumido["gordura"] += r.gordura
        if r.refeicao in refeicoes: refeicoes[r.refeicao].append({"id": r.id, "nome": r.nome_alimento, "kcal": r.kcal, "p": r.proteina, "c": r.carbo, "g": r.gordura})
    return {"metas": metas, "consumido": consumido, "refeicoes": refeicoes}
@app.put("/nutricao/{usuario_id}/metas")
def atualizar_metas(usuario_id: int, req: AtualizarMetasReq, db: Session = Depends(get_db)): meta = db.query(MetaNutricao).filter(MetaNutricao.usuario_id == usuario_id).first(); meta.kcal = req.kcal if meta else None; meta.proteina = req.proteina if meta else None; meta.carbo = req.carbo if meta else None; meta.gordura = req.gordura if meta else None; db.add(MetaNutricao(usuario_id=usuario_id, kcal=req.kcal, proteina=req.proteina, carbo=req.carbo, gordura=req.gordura)) if not meta else None; db.commit(); return {"status": "sucesso"}
@app.post("/nutricao/{usuario_id}/adicionar")
def adicionar_alimento(usuario_id: int, req: AdicionarAlimentoReq, db: Session = Depends(get_db)): db.add(RegistroNutricao(usuario_id=usuario_id, refeicao=req.refeicao, nome_alimento=req.nome_alimento, kcal=req.kcal, proteina=req.proteina, carbo=req.carbo, gordura=req.gordura, data_registro=obter_data_diario())); db.commit(); return {"status": "sucesso"}
@app.delete("/nutricao/registro/{registro_id}")
def deletar_registro(registro_id: int, db: Session = Depends(get_db)): reg = db.query(RegistroNutricao).filter(RegistroNutricao.id == registro_id).first(); db.delete(reg) if reg else None; db.commit(); return {"status": "sucesso"}
@app.put("/nutricao/registro/{registro_id}")
def editar_registro(registro_id: int, req: AtualizarRegistroReq, db: Session = Depends(get_db)): reg = db.query(RegistroNutricao).filter(RegistroNutricao.id == registro_id).first(); reg.nome_alimento = req.nome_alimento if reg else None; reg.kcal = req.kcal if reg else None; reg.proteina = req.proteina if reg else None; reg.carbo = req.carbo if reg else None; reg.gordura = req.gordura if reg else None; db.commit(); return {"status": "sucesso"}
@app.get("/nutricao/{usuario_id}/historico")
def historico_nutricao(usuario_id: int, db: Session = Depends(get_db)):
    registros = db.query(RegistroNutricao).filter(RegistroNutricao.usuario_id == usuario_id).all(); hist = {}
    for r in registros:
        if r.data_registro not in hist: hist[r.data_registro] = {"kcal": 0, "p": 0, "c": 0, "g": 0}
        hist[r.data_registro]["kcal"] += r.kcal; hist[r.data_registro]["p"] += r.proteina; hist[r.data_registro]["c"] += r.carbo; hist[r.data_registro]["g"] += r.gordura
    return sorted([{"data": k, "kcal": v["kcal"], "p": v["p"], "c": v["c"], "g": v["g"]} for k, v in hist.items()], key=lambda x: x["data"], reverse=True)
@app.get("/nutricao/{usuario_id}/personalizados")
def listar_personalizados(usuario_id: int, db: Session = Depends(get_db)): return db.query(AlimentoPersonalizado).filter(AlimentoPersonalizado.usuario_id == usuario_id).all()
@app.post("/nutricao/{usuario_id}/personalizados")
def criar_personalizado(usuario_id: int, req: AlimentoPersonalizadoReq, db: Session = Depends(get_db)): db.add(AlimentoPersonalizado(usuario_id=usuario_id, nome=req.nome, porcao_g=req.porcao_g, kcal=req.kcal, proteina=req.proteina, carbo=req.carbo, gordura=req.gordura)); db.commit(); return {"status": "sucesso"}
@app.put("/nutricao/personalizados/{item_id}")
def editar_personalizado(item_id: int, req: AlimentoPersonalizadoReq, db: Session = Depends(get_db)): item = db.query(AlimentoPersonalizado).filter(AlimentoPersonalizado.id == item_id).first(); item.nome = req.nome if item else None; item.porcao_g = req.porcao_g if item else None; item.kcal = req.kcal if item else None; item.proteina = req.proteina if item else None; item.carbo = req.carbo if item else None; item.gordura = req.gordura if item else None; db.commit(); return {"status": "sucesso"}
@app.delete("/nutricao/personalizados/{item_id}")
def deletar_personalizado(item_id: int, db: Session = Depends(get_db)): item = db.query(AlimentoPersonalizado).filter(AlimentoPersonalizado.id == item_id).first(); db.delete(item) if item else None; db.commit(); return {"status": "sucesso"}
@app.post("/treinos")
def criar_treino(treino: dict, db: Session = Depends(get_db)):
    
    # === TRAVA DE SEGURANÇA===
    from sqlalchemy import text
    usuario_mestre = db.query(models.Usuario).filter(models.Usuario.id == 1).first()
    if not usuario_mestre:
        novo_usuario = models.Usuario(id=1, nome="Mestre Gorila")
        db.add(novo_usuario)
        db.commit()
    db.commit()
    # ===================================

    nova_ficha = FichaTreino(
        usuario_id=1,  
        nome=treino.get("nome", "Novo Treino"), 
        foco=treino.get("foco", "Geral")
       
    )
    db.add(nova_ficha)
    db.commit()
    db.refresh(nova_ficha)
    
    for ex in treino.get("exercicios", []):
        novo_ex = FichaExercicio(
            ficha_id=nova_ficha.id,
            catalogo_id=ex["id"], 
            series=ex["series"],
            reps=str(ex["reps"])
        )
        db.add(novo_ex)
    db.commit()
    return {"msg": "Treino criado com sucesso", "id": nova_ficha.id}
@app.put("/treinos/{ficha_id}")
def editar_treino(ficha_id: int, treino: dict, db: Session = Depends(get_db)):
    ficha = db.query(FichaTreino).filter(FichaTreino.id == ficha_id).first()
    if not ficha:
        return {"erro": "Treino não encontrado"}
        
    ficha.nome = treino.get("nome", ficha.nome)
    ficha.foco = treino.get("foco", ficha.foco)
    
    db.query(FichaExercicio).filter(FichaExercicio.ficha_id == ficha_id).delete()
    
    for ex in treino.get("exercicios", []):
        novo_ex = FichaExercicio(
            ficha_id=ficha.id,
            catalogo_id=ex["id"],
            series=ex["series"],
            reps=str(ex["reps"])
        )
        db.add(novo_ex)
        
    db.commit()
    return {"msg": "Treino atualizado com sucesso"}

@app.delete("/treinos/{ficha_id}")
def deletar_treino(ficha_id: int, db: Session = Depends(get_db)):
    # Apaga os exercícios vinculados primeiro (regra de banco de dados)
    db.query(FichaExercicio).filter(FichaExercicio.ficha_id == ficha_id).delete()
    # Apaga a ficha
    db.query(FichaTreino).filter(FichaTreino.id == ficha_id).delete()
    db.commit()
    return {"msg": "Treino deletado com sucesso"}

@app.get("/recordes")
def listar_recordes(db: Session = Depends(get_db)):
    # Busca todas as séries já registradas junto com a info do catálogo
    series = db.query(models.SerieRegistrada, CatalogoExercicio).join(CatalogoExercicio, models.SerieRegistrada.exercicio_id == CatalogoExercicio.id).all()
    
    recordes_dict = {}
    for serie, cat in series:
        ex_id = cat.id
        if ex_id not in recordes_dict:
            recordes_dict[ex_id] = {
                "serie_id": serie.id, 
                "nome": cat.nome_exibicao, 
                "carga": serie.carga, 
                "reps": serie.repeticoes, 
                "usa_carga": cat.usa_carga,
                # Formata a data se existir
                "data": serie.data_registro.strftime("%d/%m/%Y") if serie.data_registro else ""
            }
        else:
            atual = recordes_dict[ex_id]
            if cat.usa_carga:
                # Exercícios com Carga: Maior Carga ganha. Desempate: Mais reps.
                carga_atual = atual["carga"] or 0
                carga_nova = serie.carga or 0
                if carga_nova > carga_atual or (carga_nova == carga_atual and serie.repeticoes > atual["reps"]):
                    recordes_dict[ex_id] = {"serie_id": serie.id, "nome": cat.nome_exibicao, "carga": serie.carga, "reps": serie.repeticoes, "usa_carga": True, "data": serie.data_registro.strftime("%d/%m/%Y") if hasattr(serie, 'data_registro') and serie.data_registro else ""}
            else:
                # Exercícios de Peso Corporal: Mais Repetições ganha.
                if (serie.repeticoes or 0) > (atual["reps"] or 0):
                    recordes_dict[ex_id] = {"serie_id": serie.id, "nome": cat.nome_exibicao, "carga": None, "reps": serie.repeticoes, "usa_carga": False, "data": serie.data_registro.strftime("%d/%m/%Y") if hasattr(serie, 'data_registro') and serie.data_registro else ""}
                    
    lista_recordes = list(recordes_dict.values())
    lista_recordes.sort(key=lambda x: x["nome"])
    return lista_recordes

@app.delete("/recordes/{serie_id}")
def deletar_recorde(serie_id: int, db: Session = Depends(get_db)):
    serie = db.query(models.SerieRegistrada).filter(models.SerieRegistrada.id == serie_id).first()
    if serie:
        db.delete(serie)
        db.commit()
        return {"msg": "Recorde apagado com sucesso!"}
    raise HTTPException(status_code=404, detail="Registro não encontrado")

# Schema para validar a lista de sincronização
class AcaoOfflineReq(BaseModel):
    id: int
    endpoint: str
    metodo: str
    payload: str
    data_criacao: str

@app.post("/sincronizar_offline")
def sincronizar_offline(acoes: list[AcaoOfflineReq], db: Session = Depends(get_db)):
    # Este mapa vai traduzir o ID temporário do celular para o ID real do Banco
    mapa_sessoes = {} 

    for acao in acoes:
        payload = json.loads(acao.payload)

        # 1. TRADUZIR O INÍCIO DO TREINO
        if acao.endpoint == "/sessao/iniciar":
            nova_sessao = models.SessaoTreino(
                treino_id=payload["treino_id"], 
                data_inicio=datetime.fromisoformat(acao.data_criacao), 
                status='em_andamento'
            )
            db.add(nova_sessao)
            db.commit()
            db.refresh(nova_sessao)
            mapa_sessoes[payload["local_sessao_id"]] = nova_sessao.id

        # 2. TRADUZIR O REGISTRO DE SÉRIES E RECORDES
        elif acao.endpoint == "/sessao/registrar_serie_offline":
            real_sessao_id = mapa_sessoes.get(payload["local_sessao_id"])
            if real_sessao_id:
                nova_serie = models.SerieRegistrada(
                    sessao_id=real_sessao_id,
                    exercicio_id=payload["exercicio_id"],
                    carga=payload["carga"],
                    repeticoes=payload["repeticoes"],
                    data_registro=datetime.fromisoformat(acao.data_criacao)
                )
                db.add(nova_serie)
                db.commit()

                # Garbage Collector: Mantém o histórico leve no servidor (limite de 4)
                series_do_ex = db.query(models.SerieRegistrada).filter(
                    models.SerieRegistrada.exercicio_id == payload["exercicio_id"]
                ).order_by(models.SerieRegistrada.id.desc()).all()
                if len(series_do_ex) > 4:
                    for s_del in series_do_ex[4:]:
                        db.delete(s_del)
                    db.commit()

        # 3. TRADUZIR A FINALIZAÇÃO
        elif acao.endpoint == "/sessao/finalizar_offline":
            real_sessao_id = mapa_sessoes.get(payload["local_sessao_id"])
            if real_sessao_id:
                sessao = db.query(models.SessaoTreino).filter(models.SessaoTreino.id == real_sessao_id).first()
                if sessao:
                    sessao.status = 'finalizada'
                    sessao.data_fim = datetime.fromisoformat(acao.data_criacao)
                    db.commit()

    return {"msg": "Sincronização de Elite concluída e recordes atualizados!"}
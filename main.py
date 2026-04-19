from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime, timedelta
from typing import Optional
import json

# Importando o banco e as nossas tabelas unificadas
from database import SessionLocal, engine
from models import (
    Base, Usuario, CatalogoExercicio, FichaTreino, FichaExercicio, 
    SessaoTreino, SerieRegistrada, RegistroNutricao, MetaNutricao, AlimentoPersonalizado
)

# Cria as tabelas no banco de dados baseado no models.py
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Gorila App API - Master Edition")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

def get_db():
    db = SessionLocal()
    try: 
        yield db
    finally: 
        db.close()

# --- SCHEMAS (Pydantic) ---
class SessaoIniciarReq(BaseModel): treino_id: int
class SerieRegistrarReq(BaseModel): exercicio_id: int; carga: Optional[float] = None; repeticoes: int
class AtualizarPesoReq(BaseModel): peso_atual: float; meta_peso: float
class AdicionarAlimentoReq(BaseModel): refeicao: str; nome_alimento: str; kcal: float; proteina: float; carbo: float; gordura: float
class AtualizarRegistroReq(BaseModel): nome_alimento: str; kcal: float; proteina: float; carbo: float; gordura: float
class AtualizarMetasReq(BaseModel): kcal: float; proteina: float; carbo: float; gordura: float
class AlimentoPersonalizadoReq(BaseModel): nome: str; porcao_g: float; kcal: float; proteina: float; carbo: float; gordura: float
class ExercicioFichaReq(BaseModel): catalogo_id: int; series: int; reps: str; descanso: int; observacao: str = ""
class CriarFichaReq(BaseModel): nome: str; foco: str; exercicios: list[ExercicioFichaReq]

# Schema para validar a lista de sincronização
class AcaoOfflineReq(BaseModel):
    id: int
    endpoint: str
    metodo: str
    payload: str
    data_criacao: str

# --- LÓGICA DE DATA (01:00 AM) ---
def obter_data_diario():
    agora = datetime.now()
    if agora.hour < 1:
        return (agora - timedelta(days=1)).strftime("%Y-%m-%d")
    return agora.strftime("%Y-%m-%d")

# --- SEED DE DADOS: O CATÁLOGO DE ELITE ---
def semear_catalogo_exercicios(db: Session):
    if db.query(CatalogoExercicio).count() >= 150:
        return 
    
    db.query(CatalogoExercicio).delete()
    db.commit()

    # Deixei apenas alguns como exemplo para não poluir, 
    # VOCÊ PODE COLAR A SUA LISTA GIGANTE DE EXERCÍCIOS AQUI NOVAMENTE!
    exercicios = [
        {"nome_padrao": "supino_reto_barra", "nome_exibicao": "Supino Reto com Barra", "grupo": "Peito", "secundario": "Tríceps, Ombros", "movimento": "Empurrar", "tipo": "composto", "equipamento": "barra", "uni_bi": "bilateral", "reps": "8-10", "inc": 2.0},
        {"nome_padrao": "puxada_frontal_pronada", "nome_exibicao": "Puxada Frontal com Pegada Pronada", "grupo": "Costas", "secundario": "Bíceps", "movimento": "Puxar", "tipo": "composto", "equipamento": "polia", "uni_bi": "bilateral", "reps": "8-12", "inc": 2.0},
        {"nome_padrao": "agachamento_livre_barra", "nome_exibicao": "Agachamento Livre com Barra", "grupo": "Quadríceps", "secundario": "Glúteos, Posteriores", "movimento": "Agachar", "tipo": "composto", "equipamento": "barra", "uni_bi": "bilateral", "reps": "8-10", "inc": 2.0},
    ]

    for ex in exercicios:
        usa_c = True
        if ex.get("equipamento") == "peso corporal" or ex.get("movimento") == "Isometria":
            usa_c = False
        if ex.get("grupo") == "Abdômen" and ex.get("equipamento") not in ["maquina", "polia"]:
            usa_c = False

        novo_ex = CatalogoExercicio(
            nome_padrao=ex["nome_padrao"], nome_exibicao=ex["nome_exibicao"],
            grupo_muscular_principal=ex["grupo"], grupos_musculares_secundarios=ex["secundario"],
            categoria_movimento=ex["movimento"], tipo_exercicio=ex["tipo"],
            equipamento=ex["equipamento"], unilateral_ou_bilateral=ex["uni_bi"],
            faixa_reps_padrao=ex["reps"], incremento_padrao_carga=ex["inc"], usa_carga=usa_c 
        )
        db.add(novo_ex)
    db.commit()

@app.on_event("startup")
def startup_event():
    db = SessionLocal()
    semear_catalogo_exercicios(db)
    db.close()


CATALOGO_ALIMENTOS_SIMPLES = [
    {"id": 1, "nome": "Arroz Branco (Cozido)", "porcao": "100g", "ref_g": 100.0, "kcal": 130.0, "p": 2.5, "c": 28.1, "g": 0.2},
    {"id": 20, "nome": "Peito de Frango (Grelhado)", "porcao": "100g", "ref_g": 100.0, "kcal": 159.0, "p": 32.0, "c": 0.0, "g": 2.5},
    # COLE A SUA LISTA DE ALIMENTOS AQUI TAMBÉM
]

# === ROTAS DA API ===

@app.get("/catalogo/exercicios")
def buscar_catalogo_exercicios(q: str = "", grupo: str = "", db: Session = Depends(get_db)):
    query = db.query(CatalogoExercicio).filter(CatalogoExercicio.ativo == True)
    if q: query = query.filter(CatalogoExercicio.nome_exibicao.ilike(f"%{q}%"))
    if grupo: query = query.filter(CatalogoExercicio.grupo_muscular_principal == grupo)
    resultados = query.order_by(CatalogoExercicio.grupo_muscular_principal, CatalogoExercicio.nome_exibicao).all()
    return [{"id": r.id, "nome": r.nome_exibicao, "grupo": r.grupo_muscular_principal, "tipo": r.tipo_exercicio, "equipamento": r.equipamento, "reps_padrao": r.faixa_reps_padrao, "inc_padrao": r.incremento_padrao_carga, "usa_carga": r.usa_carga} for r in resultados]

@app.post("/treinos")
def criar_treino(treino: dict, db: Session = Depends(get_db)):
    usuario_mestre = db.query(Usuario).filter(Usuario.id == 1).first()
    if not usuario_mestre:
        db.add(Usuario(id=1, nome="Mestre Gorila"))
        db.commit()

    nova_ficha = FichaTreino(usuario_id=1, nome=treino.get("nome", "Novo Treino"), foco=treino.get("foco", "Geral"))
    db.add(nova_ficha); db.commit(); db.refresh(nova_ficha)
    
    for ex in treino.get("exercicios", []):
        db.add(FichaExercicio(ficha_id=nova_ficha.id, catalogo_id=ex["id"], series=ex["series"], reps=str(ex["reps"])))
    db.commit()
    return {"msg": "Treino criado com sucesso", "id": nova_ficha.id}

@app.get("/treinos")
def listar_treinos(db: Session = Depends(get_db)):
    fichas = db.query(FichaTreino).filter(FichaTreino.usuario_id == 1).all()
    resultado = []
    for f in fichas:
        exs = db.query(FichaExercicio, CatalogoExercicio).join(CatalogoExercicio, FichaExercicio.catalogo_id == CatalogoExercicio.id).filter(FichaExercicio.ficha_id == f.id).all()
        lista_ex = [{"id": ce.id, "nome": ce.nome_exibicao, "series": fe.series, "reps": fe.reps, "grupo": ce.grupo_muscular_principal, "usa_carga": ce.usa_carga} for fe, ce in exs]
        resultado.append({"id": f.id, "treino": f.nome, "foco": f.foco, "nivel": "Personalizado", "exercicios": lista_ex})
    return resultado

@app.put("/treinos/{ficha_id}")
def editar_treino(ficha_id: int, treino: dict, db: Session = Depends(get_db)):
    ficha = db.query(FichaTreino).filter(FichaTreino.id == ficha_id).first()
    if not ficha: return {"erro": "Treino não encontrado"}
    ficha.nome = treino.get("nome", ficha.nome); ficha.foco = treino.get("foco", ficha.foco)
    db.query(FichaExercicio).filter(FichaExercicio.ficha_id == ficha_id).delete()
    for ex in treino.get("exercicios", []): db.add(FichaExercicio(ficha_id=ficha.id, catalogo_id=ex["id"], series=ex["series"], reps=str(ex["reps"])))
    db.commit()
    return {"msg": "Treino atualizado com sucesso"}

@app.delete("/treinos/{ficha_id}")
def deletar_treino(ficha_id: int, db: Session = Depends(get_db)):
    db.query(FichaExercicio).filter(FichaExercicio.ficha_id == ficha_id).delete()
    db.query(FichaTreino).filter(FichaTreino.id == ficha_id).delete()
    db.commit()
    return {"msg": "Treino deletado com sucesso"}

@app.post("/sessao/iniciar")
def iniciar_sessao(req: SessaoIniciarReq, db: Session = Depends(get_db)): 
    nova_sessao = SessaoTreino(treino_id=req.treino_id, data_inicio=datetime.now(), status='em_andamento')
    db.add(nova_sessao); db.commit(); db.refresh(nova_sessao)
    return {"sessao_id": nova_sessao.id}

@app.post("/sessao/{sessao_id}/registrar_serie")
def registrar_serie(sessao_id: int, req: SerieRegistrarReq, db: Session = Depends(get_db)):
    ex_catalogo = db.query(CatalogoExercicio).filter(CatalogoExercicio.id == req.exercicio_id).first()
    if not ex_catalogo: raise HTTPException(404, "Exercicio nao encontrado")
    if ex_catalogo.usa_carga and req.carga is None: raise HTTPException(400, "Este exercício exige o registro de carga (kg).")
    
    db.add(SerieRegistrada(sessao_id=sessao_id, exercicio_id=req.exercicio_id, carga=req.carga if ex_catalogo.usa_carga else None, repeticoes=req.repeticoes))
    db.commit()
    
    series_do_ex = db.query(SerieRegistrada).filter(SerieRegistrada.exercicio_id == req.exercicio_id).order_by(SerieRegistrada.id.desc()).all()
    if len(series_do_ex) > 4:
        for s_del in series_do_ex[4:]: db.delete(s_del)
        db.commit()
    return {"status": "sucesso"}

@app.get("/exercicio/{exercicio_id}/historico")
def buscar_historico(exercicio_id: int, db: Session = Depends(get_db)): 
    return list(reversed([{"carga": s.carga, "repeticoes": s.repeticoes} for s in db.query(SerieRegistrada).filter(SerieRegistrada.exercicio_id == exercicio_id).order_by(SerieRegistrada.id.desc()).limit(4).all()]))

@app.post("/sessao/{sessao_id}/finalizar")
def finalizar_sessao(sessao_id: int, db: Session = Depends(get_db)): 
    sessao = db.query(SessaoTreino).filter(SessaoTreino.id == sessao_id).first()
    if sessao: sessao.status = 'finalizada'; db.commit()
    return {"status": "sucesso"}

@app.get("/perfil/{usuario_id}")
def obter_perfil(usuario_id: int, db: Session = Depends(get_db)): 
    user = db.query(Usuario).filter(Usuario.id == usuario_id).first()
    return {"nome": user.nome, "peso_atual": user.peso_atual, "meta_peso": user.meta_peso} if user else {"nome": "Markin", "peso_atual": 70.0, "meta_peso": 80.0}

@app.put("/perfil/{usuario_id}/peso")
def atualizar_peso(usuario_id: int, req: AtualizarPesoReq, db: Session = Depends(get_db)): 
    user = db.query(Usuario).filter(Usuario.id == usuario_id).first()
    if user: user.peso_atual = req.peso_atual; user.meta_peso = req.meta_peso
    else: db.add(Usuario(id=usuario_id, nome="Markin", peso_atual=req.peso_atual, meta_peso=req.meta_peso))
    db.commit(); return {"status": "sucesso"}

@app.get("/recordes")
def listar_recordes(db: Session = Depends(get_db)):
    series = db.query(SerieRegistrada, CatalogoExercicio).join(CatalogoExercicio, SerieRegistrada.exercicio_id == CatalogoExercicio.id).all()
    recordes_dict = {}
    for serie, cat in series:
        ex_id = cat.id
        data_str = serie.data_registro.strftime("%d/%m/%Y") if serie.data_registro else ""
        if ex_id not in recordes_dict:
            recordes_dict[ex_id] = {"serie_id": serie.id, "nome": cat.nome_exibicao, "carga": serie.carga, "reps": serie.repeticoes, "usa_carga": cat.usa_carga, "data": data_str}
        else:
            atual = recordes_dict[ex_id]
            carga_nova, carga_atual = serie.carga or 0, atual["carga"] or 0
            if cat.usa_carga and (carga_nova > carga_atual or (carga_nova == carga_atual and serie.repeticoes > atual["reps"])):
                recordes_dict[ex_id] = {"serie_id": serie.id, "nome": cat.nome_exibicao, "carga": serie.carga, "reps": serie.repeticoes, "usa_carga": True, "data": data_str}
            elif not cat.usa_carga and ((serie.repeticoes or 0) > (atual["reps"] or 0)):
                recordes_dict[ex_id] = {"serie_id": serie.id, "nome": cat.nome_exibicao, "carga": None, "reps": serie.repeticoes, "usa_carga": False, "data": data_str}
    
    lista_recordes = list(recordes_dict.values())
    lista_recordes.sort(key=lambda x: x["nome"])
    return lista_recordes

@app.delete("/recordes/{serie_id}")
def deletar_recorde(serie_id: int, db: Session = Depends(get_db)):
    serie = db.query(SerieRegistrada).filter(SerieRegistrada.id == serie_id).first()
    if serie: db.delete(serie); db.commit(); return {"msg": "Recorde apagado com sucesso!"}
    raise HTTPException(status_code=404, detail="Registro não encontrado")

# === ROTAS DE NUTRIÇÃO ===
@app.get("/alimentos/buscar")
def buscar_alimentos(q: str = ""): 
    return [a for a in CATALOGO_ALIMENTOS_SIMPLES if q.lower() in a["nome"].lower()] if q else CATALOGO_ALIMENTOS_SIMPLES

@app.get("/nutricao/{usuario_id}/hoje")
def obter_diario_nutricao(usuario_id: int, db: Session = Depends(get_db)):
    hoje = obter_data_diario()
    registros = db.query(RegistroNutricao).filter(RegistroNutricao.usuario_id == usuario_id, RegistroNutricao.data_registro == hoje).all()
    meta_db = db.query(MetaNutricao).filter(MetaNutricao.usuario_id == usuario_id).first()
    metas = {"kcal": meta_db.kcal, "proteina": meta_db.proteina, "carbo": meta_db.carbo, "gordura": meta_db.gordura} if meta_db else {"kcal": 2800, "proteina": 160, "carbo": 350, "gordura": 80}
    consumido = {"kcal": 0, "proteina": 0, "carbo": 0, "gordura": 0}
    refeicoes = {"Cafe da Manha": [], "Almoco": [], "Lanche": [], "Jantar": [], "Ceia": []}
    for r in registros:
        consumido["kcal"] += r.kcal; consumido["proteina"] += r.proteina; consumido["carbo"] += r.carbo; consumido["gordura"] += r.gordura
        if r.refeicao in refeicoes: refeicoes[r.refeicao].append({"id": r.id, "nome": r.nome_alimento, "kcal": r.kcal, "p": r.proteina, "c": r.carbo, "g": r.gordura})
    return {"metas": metas, "consumido": consumido, "refeicoes": refeicoes}

@app.put("/nutricao/{usuario_id}/metas")
def atualizar_metas(usuario_id: int, req: AtualizarMetasReq, db: Session = Depends(get_db)): 
    meta = db.query(MetaNutricao).filter(MetaNutricao.usuario_id == usuario_id).first()
    if meta:
        meta.kcal = req.kcal; meta.proteina = req.proteina; meta.carbo = req.carbo; meta.gordura = req.gordura
    else: 
        db.add(MetaNutricao(usuario_id=usuario_id, kcal=req.kcal, proteina=req.proteina, carbo=req.carbo, gordura=req.gordura))
    db.commit(); return {"status": "sucesso"}

@app.post("/nutricao/{usuario_id}/adicionar")
def adicionar_alimento(usuario_id: int, req: AdicionarAlimentoReq, db: Session = Depends(get_db)): 
    db.add(RegistroNutricao(usuario_id=usuario_id, refeicao=req.refeicao, nome_alimento=req.nome_alimento, kcal=req.kcal, proteina=req.proteina, carbo=req.carbo, gordura=req.gordura, data_registro=obter_data_diario()))
    db.commit(); return {"status": "sucesso"}

@app.delete("/nutricao/registro/{registro_id}")
def deletar_registro(registro_id: int, db: Session = Depends(get_db)): 
    reg = db.query(RegistroNutricao).filter(RegistroNutricao.id == registro_id).first()
    if reg: db.delete(reg); db.commit()
    return {"status": "sucesso"}

@app.get("/nutricao/{usuario_id}/personalizados")
def listar_personalizados(usuario_id: int, db: Session = Depends(get_db)): 
    return db.query(AlimentoPersonalizado).filter(AlimentoPersonalizado.usuario_id == usuario_id).all()

# === ROTA DE SINCRONIZAÇÃO OFFLINE ===
@app.post("/sincronizar_offline")
def sincronizar_offline(acoes: list[AcaoOfflineReq], db: Session = Depends(get_db)):
    mapa_sessoes = {} 
    for acao in acoes:
        payload = json.loads(acao.payload)
        if acao.endpoint == "/sessao/iniciar":
            nova_sessao = SessaoTreino(treino_id=payload["treino_id"], data_inicio=datetime.fromisoformat(acao.data_criacao), status='em_andamento')
            db.add(nova_sessao); db.commit(); db.refresh(nova_sessao)
            mapa_sessoes[payload["local_sessao_id"]] = nova_sessao.id

        elif acao.endpoint == "/sessao/registrar_serie_offline":
            real_sessao_id = mapa_sessoes.get(payload["local_sessao_id"])
            if real_sessao_id:
                db.add(SerieRegistrada(sessao_id=real_sessao_id, exercicio_id=payload["exercicio_id"], carga=payload["carga"], repeticoes=payload["repeticoes"], data_registro=datetime.fromisoformat(acao.data_criacao)))
                db.commit()

        elif acao.endpoint == "/sessao/finalizar_offline":
            real_sessao_id = mapa_sessoes.get(payload["local_sessao_id"])
            if real_sessao_id:
                sessao = db.query(SessaoTreino).filter(SessaoTreino.id == real_sessao_id).first()
                if sessao: sessao.status = 'finalizada'; sessao.data_fim = datetime.fromisoformat(acao.data_criacao); db.commit()

    return {"msg": "Sincronização concluída!"}
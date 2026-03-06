from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, BackgroundTasks
from utils.auth import get_current_user, get_db
from sqlalchemy.orm import Session
from model.usuario_model import Usuario
from model.documentacao_model import Projeto
from schemas.documentacao_schemas import ProjetoUpdate, ProjetoCriar
from services.documentacao_service import gerar_documentacao_github
from utils.processar_documentacao_util import processar_documentacao
import uuid

router = APIRouter(prefix="/documentacao", tags=["Documentação"])

@router.get("/historico")
def buscar_historico(db: Session = Depends(get_db), usuario: Usuario = Depends(get_current_user)):
    projetos = (
        db.query(Projeto.id, Projeto.titulo_projeto)
        .filter(Projeto.usuario_id == usuario.id)
        .order_by(Projeto.criado_em.desc())
        .all()
    )

    if not projetos:
        return {"mensagem": "Nenhum projeto encontrado"}

    return [
        {
            "id": p.id,
            "titulo": p.titulo_projeto
        }
        for p in projetos
    ]

@router.get("/buscar")
def buscar_documentacao(id_projeto: uuid.UUID, db: Session = Depends(get_db), usuario: Usuario = Depends(get_current_user)):
    projeto = (db.query(Projeto).filter(Projeto.id == id_projeto, Projeto.usuario_id == usuario.id)).first()
    if not projeto:
        raise HTTPException(status_code=500, detail="Não foi possível encontrar o projeto.")
    return projeto

@router.post("/criar")
def criar_documentacao(
    dados: ProjetoCriar,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_user)
):

    if not dados.github_url:
        raise HTTPException(400, "Envie github_url")

    projeto = Projeto(
        usuario_id=usuario.id,
        titulo_projeto="Processando...",
        descricao_projeto="Processando...",
        readme_projeto="",
        wiki_projeto="",
        diagramas_projeto="",
        glossario_projeto=""
    )

    db.add(projeto)
    db.commit()
    db.refresh(projeto)

    background_tasks.add_task(
        processar_documentacao,
        projeto.id,
        dados.github_url
    )

    return projeto

@router.patch("/atualizar")
def atualizar_documentacao(id_projeto: uuid.UUID, dados: ProjetoUpdate, db: Session = Depends(get_db), usuario: Usuario = Depends(get_current_user)):
    projeto = (db.query(Projeto).filter(Projeto.id == id_projeto, Projeto.usuario_id == usuario.id).first())
    if not projeto:
        raise HTTPException(status_code=404, detail="Projeto não encontrado")

    for campo, valor in dados.dict(exclude_unset=True).items():
        setattr(projeto, campo, valor)

    db.commit()
    db.refresh(projeto)

    return projeto

@router.delete("/apagar")
def apagar_documentacao(id_projeto: uuid.UUID, db: Session = Depends(get_db), usuario: Usuario = Depends(get_current_user)):
    projeto = (db.query(Projeto).filter(Projeto.id == id_projeto, Projeto.usuario_id == usuario.id).first())
    if not projeto:
        raise HTTPException(status_code=404, detail="Projeto não encontrado")

    db.delete(projeto)
    db.commit()

    return {"mensagem": "Projeto apagado"}
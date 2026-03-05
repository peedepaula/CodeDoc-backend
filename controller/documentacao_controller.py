from fastapi import APIRouter, Depends, HTTPException
from utils.auth import get_current_user, get_db
from sqlalchemy.orm import Session
from model.usuario_model import Usuario
from model.documentacao_model import Projeto
from schemas.documentacao_schemas import ProjetoUpdate
import uuid

router = APIRouter(prefix="/documentacao", tags=["Documentação"])

@router.get("/historico")
def buscar_historico(db: Session = Depends(get_db), usuario: Usuario = Depends(get_current_user)):
    projetos = (db.query(Projeto.id, Projeto.titulo_projeto).filter(Projeto.usuario_id == usuario.id))
    return projetos

@router.get("/buscar")
def buscar_documentacao(id_projeto: uuid.UUID, db: Session = Depends(get_db), usuario: Usuario = Depends(get_current_user)):
    projeto = (db.query(Projeto).filter(projeto.id == id_projeto, Projeto.usuario_id == usuario.id)).first()
    if not projeto:
        raise HTTPException(status_code=500, detail="Não foi possível encontrar o projeto.")
    return projeto

@router.post("/criar")
def criar_documentacao(db: Session = Depends(get_db), usuario: Usuario = Depends(get_current_user)):
    #aui nada ainda
    return

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

@router.delete("apagar")
def apagar_documentacao(id_projeto: uuid.UUID, db: Session = Depends(get_db), usuario: Usuario = Depends(get_current_user)):
    projeto = (db.query(Projeto).filter(Projeto.id == id_projeto, Projeto.usuario_id == usuario.id).first())
    if not projeto:
        raise HTTPException(status_code=404, detail="Projeto não encontrado")

    db.delete(projeto)
    db.commit()

    return {"mensagem": "Projeto apagado"}
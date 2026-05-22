from fastapi import APIRouter, Depends, BackgroundTasks
from utils.auth import get_current_user, get_db
from sqlalchemy.orm import Session
from models.usuario_model import Usuario
from schemas.documentacao_schemas import ProjetoUpdate, ProjetoCriar
from services.documentacao_service import DocumentacaoService
import uuid

router = APIRouter(prefix="/documentacao", tags=["Documentação"])

@router.get("/historico")
def buscar_historico(db: Session = Depends(get_db), usuario: Usuario = Depends(get_current_user)):
    return DocumentacaoService.buscar_historico_service(usuario, db)

@router.get("/buscar")
def buscar_documentacao(id_projeto: uuid.UUID, db: Session = Depends(get_db), usuario: Usuario = Depends(get_current_user)):
    return DocumentacaoService.buscar_documentacao_service(id_projeto, usuario, db)

@router.post("/criar")
def criar_documentacao(
    dados: ProjetoCriar,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_user)
):
    return DocumentacaoService.criar_documentacao_service(dados, background_tasks, usuario, db)

@router.patch("/editar")
def editar_documentacao(id_projeto: uuid.UUID, dados: ProjetoUpdate, db: Session = Depends(get_db), usuario: Usuario = Depends(get_current_user)):
    return DocumentacaoService.editar_documentacao_service(id_projeto, dados, usuario, db)

@router.patch("/atualizar")
def atualizar_documentacao(id_projeto: uuid.UUID, background_tasks: BackgroundTasks, db: Session = Depends(get_db), usuario: Usuario = Depends(get_current_user)):
    return DocumentacaoService.atualizar_documentacao_service(background_tasks, id_projeto, usuario, db)

@router.delete("/apagar")
def apagar_documentacao(id_projeto: uuid.UUID, db: Session = Depends(get_db), usuario: Usuario = Depends(get_current_user)):
    return DocumentacaoService.apagar_documentacao(id_projeto, usuario, db)

@router.get("/download")
def baixar_documentacao(
    id_projeto: uuid.UUID,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_user)
):
    return DocumentacaoService.baixar_documentacao_service(
        id_projeto,
        usuario,
        db
    )
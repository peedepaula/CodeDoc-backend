from fastapi import APIRouter
import uuid

router = APIRouter(prefix="/documentacao", tags=["Documentação"])

@router.get("/historico")
def buscar_historico(usario_id: uuid.UUID):
    return

@router.get("/buscar")
def buscar_documentacao(documantacao_id: uuid.UUID):
    return

@router.post("/criar")
def criar_documentacao(documantacao_id: uuid.UUID):
    return

@router.patch("/atualizar")
def atualizar_documentacao(documantacao_id: uuid.UUID):
    return

@router.delete("apagar")
def apagar_documentacao(documantacao_id: uuid.UUID):
    return
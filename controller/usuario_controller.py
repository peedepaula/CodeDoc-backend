from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from model.usuario_model import Usuario
from database import get_db

router = APIRouter(prefix="/usuario", tags=["Usuários"])

@router.get("/usuarios")
def listar_usuarios(db: Session = Depends(get_db)):
    return db.query(Usuario).all()

@router.get("/me")
def meu_perfil():
    return

@router.post("/entrar")
def entrar():
    return

@router.post("/registrar")
def registrar():
    return

@router.post("/mandar-email-trocar-email")
def mandar_email_trocar_email():
    return

@router.post("/mandar-email-trocar-senha")
def mandar_email_trocar_senha():
    return

@router.patch("/trocar-email")
def trocar_email():
    return

@router.patch("/trocar-senha")
def trocar_senha():
    return

@router.patch("/trocar-foto")
def trocar_foto():
    return

@router.patch("/atualizar-nome-cargo")
def atualizar_nome_cargo():
    return

@router.delete("/apagar")
def apagar_usuario():
    return



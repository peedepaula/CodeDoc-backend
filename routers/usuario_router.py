from fastapi import APIRouter, Depends, UploadFile, File, BackgroundTasks
from sqlalchemy.orm import Session
from models.usuario_model import Usuario
from database import get_db
from schemas.usuario_schemas import usuarioCreate, UsuarioLogin, UsuarioUpdate
from utils.auth import get_current_user
from fastapi import Request
from services.usuario_service import UsuarioService

router = APIRouter(prefix="/usuario", tags=["Usuários"])

@router.get("/me")
def meu_perfil(usuario: Usuario = Depends(get_current_user)):
    return UsuarioService.buscar_meu_perfil_service(usuario)

@router.post("/entrar")
def entrar(dados: UsuarioLogin, db: Session = Depends(get_db)):
    return UsuarioService.entrar_service(dados, db)

@router.post("/registrar")
def registrar(dados: usuarioCreate, db: Session = Depends(get_db)):
    return UsuarioService.registrar_service(dados, db)

@router.patch("/trocar-email")
def trocar_email(token: str, db: Session = Depends(get_db)):
    return UsuarioService.trocar_email_service(token, db)

@router.patch("/trocar-senha-nao-logado")
def trocar_senha(token: str, nova_senha: str, db: Session = Depends(get_db)):
    return UsuarioService.trocar_senha_nao_logado_service(token, nova_senha, db)

@router.patch("/trocar-senha-logado")
def trocar_senha_logado(
    senha_atual: str,
    nova_senha: str,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_user)
):
    return UsuarioService.trocar_senha_logado_service(senha_atual, nova_senha, usuario, db)

@router.patch("/trocar-foto")
def trocar_foto(
    request: Request,
    foto: UploadFile = File(...), 
    db: Session = Depends(get_db), 
    usuario: Usuario = Depends(get_current_user)
):
    return UsuarioService.trocar_foto_service(request, foto, usuario, db)

@router.patch("/atualizar-nome-cargo")
def atualizar_nome_cargo(dados: UsuarioUpdate, db: Session = Depends(get_db), usuario: Usuario = Depends(get_current_user)):
    return UsuarioService.atualizar_nome_cargo_service(dados, usuario, db)

@router.delete("/apagar")
def apagar_usuario(db: Session = Depends(get_db), usuario: Usuario = Depends(get_current_user)):
    return UsuarioService.apagar_usuario_service(usuario, db)

@router.post("/mandar-email-trocar-email")
def mandar_email_trocar_email(
    novo_email: str,
    background_task: BackgroundTasks,
    usuario: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return UsuarioService.mandar_email_trocar_email_service(novo_email, background_task, usuario, db)

@router.post("/mandar-email-trocar-senha-nao-logado")
def mandar_email_trocar_senha(email: str, background_task: BackgroundTasks, db: Session = Depends(get_db)):
    return UsuarioService.mandar_email_trocar_senha_service(email, background_task, db)


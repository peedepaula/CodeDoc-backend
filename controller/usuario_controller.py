from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from model.usuario_model import Usuario
from database import get_db
from schemas.usuario_schemas import usuarioCreate, UsuarioLogin, UsuarioUpdate
from utils.seguranca import gerar_hash_senha, verificar_senha
from utils.token import criar_token
from utils.auth import get_current_user

router = APIRouter(prefix="/usuario", tags=["Usuários"])

@router.get("/me")
def meu_perfil(usuario: Usuario = Depends(get_current_user)):
    return {
        "nome": usuario.nome_usuario,
        "cargo": usuario.cargo_usuario,
        "email_usuario": usuario.nome_usuario
    }

@router.post("/entrar")
def entrar(dados: UsuarioLogin, db: Session = Depends(get_db)):
    usuario = db.query(Usuario).filter(Usuario.email_usuario == dados.email_usuario).first()
    if not usuario:
        raise HTTPException(status_code=401, detail="Email ou senha inválidos")

    if not verificar_senha(dados.senha_usuario, usuario.senha_usuario):
        raise HTTPException(status_code=401, detail="Email ou senha inválidos")

    payload = {
        "sub": str(usuario.id),
        "email": usuario.email_usuario,
        "nome": usuario.nome_usuario,
    }

    token = criar_token(payload)

    return {
        "access_token": token,
        "token_type": "bearer"
    }

@router.post("/registrar")
def registrar(dados: usuarioCreate, db: Session = Depends(get_db)):
    try:
        # 🔎 Verificar se já existe email
        usuario_existente = db.query(Usuario).filter(Usuario.email_usuario == dados.email_usuario).first()

        if usuario_existente:
            raise HTTPException(status_code=400, detail="Email já cadastrado")

        # 🔐 Criptografar senha
        senha_hash = gerar_hash_senha(dados.senha_usuario)

        # 🏗 Criar objeto
        novo_usuario = Usuario(
            nome_usuario=dados.nome_usuario,
            email_usuario=dados.email_usuario,
            senha_usuario=senha_hash
        )

        # 💾 Salvar no banco
        db.add(novo_usuario)
        db.commit()
        db.refresh(novo_usuario)

        return {
            "mensagem": "Usuário criado com sucesso",
            "id": novo_usuario.id
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao tentar registrar: {e}")

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
def atualizar_nome_cargo(dados: UsuarioUpdate, db: Session = Depends(get_db), usuario: Usuario = Depends(get_current_user)):
    usuario.nome_usuario = dados.nome_usuario
    usuario.cargo_usuario = dados.cargo_usuario

    db.commit()
    db.refresh(usuario)

    return {
        "mensagem": "Dados atualizados com sucesso",
        "id": usuario.id,
        "nome": usuario.nome_usuario,
        "cargo": usuario.cargo_usuario
    }

@router.delete("/apagar")
def apagar_usuario(db: Session = Depends(get_db), usuario: Usuario = Depends(get_current_user)):
    db.delete(usuario)
    db.commit()
    return {"mensagem": "Usuário apagado com sucesso"}



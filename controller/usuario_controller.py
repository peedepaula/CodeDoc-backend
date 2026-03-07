from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, BackgroundTasks
from sqlalchemy.orm import Session
from model.usuario_model import Usuario
from model.reset_email_model import ResetEmail
from database import get_db
from schemas.usuario_schemas import usuarioCreate, UsuarioLogin, UsuarioUpdate
from utils.seguranca import gerar_hash_senha, verificar_senha
from utils.token import criar_token
from utils.auth import get_current_user
from model.reset_senha_model import ResetSenha
from utils.email import enviar_email_reset
from utils.token_urlsafe import gerar_token_reset
from datetime import datetime, timedelta
import shutil
import os

router = APIRouter(prefix="/usuario", tags=["Usuários"])

@router.get("/me")
def meu_perfil(usuario: Usuario = Depends(get_current_user)):
    return {
        "nome": usuario.nome_usuario,
        "cargo": usuario.cargo_usuario,
        "foto": usuario.foto_usuario,
        "email_usuario": usuario.email_usuario
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
def mandar_email_trocar_email(
    novo_email: str,
    background_task: BackgroundTasks,
    usuario: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    
    token = gerar_token_reset()

    reset = ResetEmail(
        usuario_id=usuario.id,
        novo_email=novo_email,
        token=token,
        expira_em=datetime.utcnow() + timedelta(hours=1)
    )

    db.add(reset)
    db.commit()

    link = f"http://localhost:5173/email-trocado/{token}"
    background_task.add_task(enviar_email_reset, novo_email, link)

    return {"mensagem": "Email enviado"}

@router.patch("/trocar-email")
def trocar_email(token: str, db: Session = Depends(get_db)):
    reset = db.query(ResetEmail).filter(
        ResetEmail.token == token
    ).first()

    if not reset:
        raise HTTPException(status_code=400, detail="Token inválido")

    usuario = db.query(Usuario).filter(
        Usuario.id == reset.usuario_id
    ).first()

    usuario.email_usuario = reset.novo_email

    db.delete(reset)
    db.commit()

    return {"mensagem": "Email alterado"}

@router.post("/mandar-email-trocar-senha-nao-logado")
def mandar_email_trocar_senha(email: str, background_task: BackgroundTasks, db: Session = Depends(get_db)):
    usuario = db.query(Usuario).filter(
        Usuario.email_usuario == email
    ).first()

    if not usuario:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")

    token = gerar_token_reset()

    reset = ResetSenha(
        usuario_id=usuario.id,
        token=token,
        expira_em=datetime.utcnow() + timedelta(minutes=15)
    )

    db.add(reset)
    db.commit()
    link = f"http://localhost:5173/nova-senha/{token}"
    background_task.add_task(enviar_email_reset, usuario.email_usuario, link)

    return {"mensagem": "Email enviado"}

@router.patch("/trocar-senha-nao-logado")
def trocar_senha(token: str, nova_senha: str, db: Session = Depends(get_db)):
    reset = db.query(ResetSenha).filter(
        ResetSenha.token == token
    ).first()

    if not reset:
        raise HTTPException(status_code=400, detail="Token inválido")

    if reset.expira_em < datetime.utcnow():
        raise HTTPException(status_code=400, detail="Token expirado")

    usuario = db.query(Usuario).filter(
        Usuario.id == reset.usuario_id
    ).first()

    usuario.senha_usuario = gerar_hash_senha(nova_senha)
    db.delete(reset)
    db.commit()

    return {"mensagem": "Senha alterada"}

@router.patch("/trocar-senha-logado")
def trocar_senha_logado(
    senha_atual: str,
    nova_senha: str,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_user)
):

    # 1️⃣ verificar senha atual
    if not verificar_senha(senha_atual, usuario.senha_usuario):
        raise HTTPException(status_code=400, detail="Senha atual incorreta")

    # 2️⃣ gerar hash da nova senha
    usuario.senha_usuario = gerar_hash_senha(nova_senha)

    # 3️⃣ salvar no banco
    db.commit()

    return {"mensagem": "Senha alterada com sucesso"}

@router.patch("/trocar-foto")
def trocar_foto(
    foto: UploadFile = File(...), 
    db: Session = Depends(get_db), 
    usuario: Usuario = Depends(get_current_user)
):
    # 1. Definir o caminho onde a foto será salva
    pasta_fotos = "static/fotos_perfil"
    if not os.path.exists(pasta_fotos):
        os.makedirs(pasta_fotos)

    # 2. Gerar um nome único para o arquivo (evita sobrescrever fotos com mesmo nome)
    extensao = foto.filename.split(".")[-1]
    nome_arquivo = f"{usuario.id}.{extensao}"
    caminho_final = os.path.join(pasta_fotos, nome_arquivo)

    # 3. Salvar o arquivo no disco
    with open(caminho_final, "wb") as buffer:
        shutil.copyfileobj(foto.file, buffer)

    # 4. Salvar o caminho/URL no banco de dados
    usuario.foto_usuario = f"http://localhost:8000/{pasta_fotos}/{nome_arquivo}"
    db.commit()

    return {"mensagem": "Foto atualizada", "url": usuario.foto_usuario}

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



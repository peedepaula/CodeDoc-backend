from fastapi import HTTPException, UploadFile, BackgroundTasks
from sqlalchemy.orm import Session
from models.usuario_model import Usuario
from models.reset_email_model import ResetEmail
from utils.seguranca import gerar_hash_senha, verificar_senha
from utils.token import criar_token
from models.reset_senha_model import ResetSenha
from utils.email import enviar_email_reset
from utils.token_urlsafe import gerar_token_reset
from datetime import datetime, timedelta
from schemas.usuario_schemas import usuarioCreate, UsuarioLogin, UsuarioUpdate
import shutil
from fastapi import Request
import os

class UsuarioService():

    @staticmethod
    def buscar_meu_perfil_service(usuario: Usuario):
        try:
            dados_usuario = {
                "nome": usuario.nome_usuario,
                "cargo": usuario.cargo_usuario,
                "foto": usuario.foto_usuario,
                "email_usuario": usuario.email_usuario
            }

            return dados_usuario
        
        except HTTPException:
            raise
        except Exception:
            raise HTTPException(status_code=500, detail="Erro ao tenta buscar perfil.")
    

    @staticmethod
    def entrar_service(dados: UsuarioLogin, db: Session):
        try:
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

        except HTTPException:
            raise
        except Exception:
            raise HTTPException(status_code=500, detail="Erro ao tentar entrar.")
    
    
    @staticmethod
    def registrar_service(dados: usuarioCreate, db: Session):
        try:
            usuario_existente = db.query(Usuario).filter(Usuario.email_usuario == dados.email_usuario).first()

            if usuario_existente:
                raise HTTPException(status_code=400, detail="Email já cadastrado")

            senha_hash = gerar_hash_senha(dados.senha_usuario)

            novo_usuario = Usuario(
                nome_usuario=dados.nome_usuario,
                email_usuario=dados.email_usuario,
                senha_usuario=senha_hash
            )

            db.add(novo_usuario)
            db.commit()
            db.refresh(novo_usuario)

            return {
                "mensagem": "Usuário criado com sucesso",
                "id": novo_usuario.id
            }

        except HTTPException:
            raise
        except Exception:
            raise HTTPException(status_code=500, detail="Erro ao tentar registrar.")
        

    @staticmethod
    def trocar_email_service(token: str, db: Session):
        try:
            reset = db.query(ResetEmail).filter(ResetEmail.token == token).first()

            if not reset:
                raise HTTPException(status_code=400, detail="Token inválido")

            usuario = db.query(Usuario).filter(Usuario.id == reset.usuario_id).first()

            usuario.email_usuario = reset.novo_email

            db.delete(reset)
            db.commit()

            return {"mensagem": "Email alterado"}

        except HTTPException:
            raise
        except Exception:
            raise HTTPException(status_code=500, detail="Erro ao tentar trocar E-mail.")


    @staticmethod
    def trocar_senha_nao_logado_service(token: str, nova_senha: str, db: Session):
        try:
            reset = db.query(ResetSenha).filter(ResetSenha.token == token).first()

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
        
        except HTTPException:
            raise
        except Exception:
            raise HTTPException(status_code=500, detail="Erro ao tentar trocar senha.")
    

    @staticmethod
    def trocar_senha_logado_service(senha_atual: str, nova_senha: str, usuario: Usuario, db: Session):
        try:
            if not verificar_senha(senha_atual, usuario.senha_usuario):
                raise HTTPException(status_code=400, detail="Senha atual incorreta")

            usuario.senha_usuario = gerar_hash_senha(nova_senha)
            db.commit()

            return {"mensagem": "Senha alterada com sucesso"}

        except HTTPException:
            raise
        except Exception:
            raise HTTPException(status_code=500, detail="Erro ao tentar trocar senha.")
    

    @staticmethod
    def trocar_foto_service(request: Request, foto: UploadFile, usuario: Usuario, db: Session):
        try:
            pasta_fotos = "static/fotos_perfil"
            if not os.path.exists(pasta_fotos):
                os.makedirs(pasta_fotos)

            extensao = foto.filename.split(".")[-1]
            nome_arquivo = f"{usuario.id}.{extensao}"
            caminho_final = os.path.join(pasta_fotos, nome_arquivo)

            with open(caminho_final, "wb") as buffer:
                shutil.copyfileobj(foto.file, buffer)

            url_base = str(request.base_url)
            usuario.foto_usuario = f"{url_base}static/fotos_perfil/{nome_arquivo}"
            db.commit()

            return {"mensagem": "Foto atualizada", "url": usuario.foto_usuario}

        except HTTPException:
            raise
        except Exception:
            raise HTTPException(status_code=500, detail="Erro ao tentar foto.")


    @staticmethod
    def atualizar_nome_cargo_service(dados: UsuarioUpdate, usuario: Usuario, db: Session):
        try:
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

        except HTTPException:
            raise
        except Exception:
            raise HTTPException(status_code=500, detail="Erro ao tentar trocar dados.")
    
    
    @staticmethod
    def apagar_usuario_service(usuario: Usuario, db: Session):
        try:
            db.delete(usuario)
            db.commit()
            return {"mensagem": "Usuário apagado com sucesso"}

        except HTTPException:
            raise
        except Exception:
            raise HTTPException(status_code=500, detail="Erro ao tentar apagar usuário.")
    

    @staticmethod
    def mandar_email_trocar_email_service(novo_email: str, background_task: BackgroundTasks, usuario: Usuario, db: Session):
        try:
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

        except HTTPException:
            raise
        except Exception:
            raise HTTPException(status_code=500, detail="Erro ao tentar mandar E-mail.")
    

    @staticmethod
    def mandar_email_trocar_senha_service(email: str, background_task: BackgroundTasks, db: Session):
        try:
            usuario = db.query(Usuario).filter(Usuario.email_usuario == email).first()

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

        except HTTPException:
            raise
        except Exception:
            raise HTTPException(status_code=500, detail="Erro tentar mandar e-mail.")
    

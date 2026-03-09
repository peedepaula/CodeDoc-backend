from fastapi import HTTPException, BackgroundTasks
from urllib.parse import urlparse
from sqlalchemy.orm import Session
from models.usuario_model import Usuario
from models.documentacao_model import Projeto
from schemas.documentacao_schemas import ProjetoUpdate, ProjetoCriar
from utils.processar_documentacao_util import processar_documentacao
from utils.github import baixar_repo, extrair_codigo
from utils.ia_utils import gerar_documentacao

class DocumentacaoService:

    @staticmethod
    def buscar_historico_service(usuario: Usuario, db: Session):
        try:
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
    
        except Exception:
            raise
        except Exception:
            raise HTTPException(status_code=500, detail="Erro ao tentar buscar histórico.")
    

    @staticmethod
    def buscar_documentacao_service(id_projeto: str, usuario: Usuario, db: Session):
        try:
            projeto = (db.query(Projeto).filter(Projeto.id == id_projeto, Projeto.usuario_id == usuario.id)).first()
            if not projeto:
                raise HTTPException(status_code=500, detail="Não foi possível encontrar o projeto.")
            return projeto
        
        except Exception:
            raise
        except Exception:
            raise HTTPException(status_code=500, detail="Erro ao tentar buscar a documentação.")
    

    @staticmethod
    def criar_documentacao_service(dados: ProjetoCriar, background_tasks: BackgroundTasks, usuario: Usuario, db: Session):
        try:
            if not dados.github_url:
                raise HTTPException(400, "Envie github_url")

            parsed = urlparse(dados.github_url)

            if parsed.netloc not in ["github.com", "www.github.com"]:
                raise HTTPException(
                    status_code=400,
                    detail="O link precisa ser um repositório do GitHub"
                )

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
    
        except Exception:
            raise
        except Exception:
            raise HTTPException(status_code=500, detail="Erro ao tentar criar a documentação.")
    

    @staticmethod
    def atualizar_documentacao_service(id_projeto: str, dados: ProjetoUpdate, usuario: Usuario, db: Session):
        try:
            projeto = (db.query(Projeto).filter(Projeto.id == id_projeto, Projeto.usuario_id == usuario.id).first())
            if not projeto:
                raise HTTPException(status_code=404, detail="Projeto não encontrado")

            for campo, valor in dados.dict(exclude_unset=True).items():
                setattr(projeto, campo, valor)

            db.commit()
            db.refresh(projeto)

            return projeto
        
        except Exception:
            raise
        except Exception:
            raise HTTPException(status_code=500, detail="Erro ao tentar atualizar a documentação.")
    

    @staticmethod
    def apagar_documentacao(id_projeto: str, usuario: Usuario, db: Session):
        try:
            projeto = (db.query(Projeto).filter(Projeto.id == id_projeto, Projeto.usuario_id == usuario.id).first())
            if not projeto:
                raise HTTPException(status_code=404, detail="Projeto não encontrado")

            db.delete(projeto)
            db.commit()

            return {"mensagem": "Projeto apagado"}
    
        except Exception:
            raise
        except Exception:
            raise HTTPException(status_code=500, detail="Erro ao tentar apagar a documentação.")


    @staticmethod
    def gerar_documentacao_github_service(github_url):
        try:
            repo_zip = baixar_repo(github_url)
            codigo = extrair_codigo(repo_zip)
            documentacao = gerar_documentacao(codigo)

            return documentacao
        
        except Exception:
            raise
        except Exception:
            raise HTTPException(status_code=500, detail="Erro ao tentar a gerar documentacao.")
    
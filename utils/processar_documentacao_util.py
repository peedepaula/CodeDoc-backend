from models.documentacao_model import Projeto
from database import SessionLocal
import json

def processar_documentacao(projeto_id, github_url, tipo):
    from services.documentacao_service import DocumentacaoService
    db = SessionLocal()

    try:
        documentacao = DocumentacaoService.gerar_documentacao_github_service(github_url)

        projeto = db.query(Projeto).filter(Projeto.id == projeto_id).first()

        if tipo != 'atualizar':
            projeto.titulo_projeto = documentacao["titulo"]
        projeto.descricao_projeto = documentacao["descricao"]
        projeto.readme_projeto = documentacao["readme"]
        projeto.wiki_projeto = documentacao["wiki"]
        projeto.diagramas_projeto = documentacao["diagrama"]
        projeto.glossario_projeto = json.dumps(documentacao["glossario"])

        db.commit()

    finally:
        db.close()
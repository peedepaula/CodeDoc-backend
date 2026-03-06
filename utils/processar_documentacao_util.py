from model.documentacao_model import Projeto
from services.documentacao_service import gerar_documentacao_github
from database import SessionLocal
import json

def processar_documentacao(projeto_id, github_url):

    db = SessionLocal()

    try:
        documentacao = gerar_documentacao_github(github_url)

        projeto = db.query(Projeto).filter(Projeto.id == projeto_id).first()

        projeto.titulo_projeto = documentacao["titulo"]
        projeto.descricao_projeto = documentacao["descricao"]
        projeto.readme_projeto = documentacao["readme"]
        projeto.wiki_projeto = documentacao["wiki"]
        projeto.diagramas_projeto = documentacao["diagrama"]
        projeto.glossario_projeto = json.dumps(documentacao["glossario"])

        db.commit()

    finally:
        db.close()
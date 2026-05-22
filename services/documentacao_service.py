from fastapi import HTTPException, BackgroundTasks
from fastapi.responses import FileResponse
from urllib.parse import urlparse
from sqlalchemy.orm import Session
from models.usuario_model import Usuario
from models.documentacao_model import Projeto
from schemas.documentacao_schemas import ProjetoUpdate, ProjetoCriar
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.utils import ImageReader
from reportlab.lib.styles import getSampleStyleSheet
import tempfile
from utils.processar_documentacao_util import processar_documentacao
from utils.github import baixar_repo, extrair_codigo
from utils.ia_utils import gerar_documentacao
from reportlab.platypus import Image
import base64
import httpx
import markdown
import json
import os

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
                glossario_projeto="",
                github_url=dados.github_url
            )

            db.add(projeto)
            db.commit()
            db.refresh(projeto)

            background_tasks.add_task(
                processar_documentacao,
                projeto.id,
                dados.github_url,
                'geracao'
            )

            return projeto
    
        except Exception:
            raise
        except Exception:
            raise HTTPException(status_code=500, detail="Erro ao tentar criar a documentação.")
    

    @staticmethod
    def editar_documentacao_service(id_projeto: str, dados: ProjetoUpdate, usuario: Usuario, db: Session):
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
            raise HTTPException(status_code=500, detail="Erro ao tentar editar a documentação.")
        

    def atualizar_documentacao_service(background_tasks: BackgroundTasks, id_projeto: str, usuario: Usuario, db: Session):
        try:
            projeto = (db.query(Projeto).filter(Projeto.id == id_projeto, Projeto.usuario_id == usuario.id).first())
            if not projeto:
                raise HTTPException(status_code=404, detail="Projeto não encontrado")

            projeto.usuario_id=usuario.id,
            projeto.descricao_projeto="Atualizando...",
            projeto.readme_projeto="Atualizando...",
            projeto.wiki_projeto="Atualizando...",
            projeto.diagramas_projeto="",
            projeto.glossario_projeto="Atualizando...",

            db.commit()
            db.refresh(projeto)
            
            background_tasks.add_task(
                processar_documentacao,
                projeto.id,
                projeto.github_url,
                'atualizar'
            )

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
        

    @staticmethod
    def baixar_documentacao_service(
        id_projeto: str,
        usuario: Usuario,
        db: Session
    ):
        projeto = (
            db.query(Projeto)
            .filter(
                Projeto.id == id_projeto,
                Projeto.usuario_id == usuario.id
            )
            .first()
        )

        if not projeto:
            raise HTTPException(
                status_code=404,
                detail="Projeto não encontrado"
            )

        temp_pdf = tempfile.NamedTemporaryFile(
            delete=False,
            suffix=".pdf"
        )

        doc = SimpleDocTemplate(temp_pdf.name)

        styles = getSampleStyleSheet()

        elementos = []

        elementos.append(
            Paragraph("README", styles['Heading1'])
        )

        elementos.extend(
            DocumentacaoService.markdown_para_elementos(
                projeto.readme_projeto,
                styles
            )
        )

        elementos.append(Spacer(1, 20))

        elementos.append(
            Paragraph("WIKI", styles['Heading1'])
        )

        elementos.extend(
            DocumentacaoService.markdown_para_elementos(
                projeto.readme_projeto,
                styles
            )
        )

        elementos.append(Spacer(1, 20))

        elementos.append(
            Paragraph("GLOSSÁRIO", styles['Heading1'])
        )

        elementos.extend(
            DocumentacaoService.glossario_para_elementos(
                projeto.glossario_projeto,
                styles
            )
        )

        elementos.append(Spacer(1, 20))

        elementos.append(
            Paragraph("DIAGRAMAS", styles['Heading1'])
        )

        imagem_diagrama = "diagrama.png"

        try:
            codigo_mermaid = (
                projeto.diagramas_projeto
                .replace("```mermaid", "")
                .replace("```", "")
                .strip()
            )

            DocumentacaoService.gerar_imagem_mermaid(
                codigo_mermaid,
                imagem_diagrama
            )

            img = ImageReader(imagem_diagrama)
            largura_original, altura_original = img.getSize()
            largura_max = 450
            altura_max = 500

            proporcao = min(
                largura_max / largura_original,
                altura_max / altura_original
            )

            nova_largura = largura_original * proporcao
            nova_altura = altura_original * proporcao

            elementos.append(
                Image(
                    imagem_diagrama,
                    width=nova_largura,
                    height=nova_altura
                )
            )

        except Exception as e:

            elementos.append(
                Paragraph(
                    f"Erro: {str(e)}",
                    styles['BodyText']
                )
            )

        doc.build(elementos)
        if os.path.exists(imagem_diagrama):
            os.remove(imagem_diagrama)

        return FileResponse(
            temp_pdf.name,
            media_type='application/pdf',
            filename='documentacao.pdf'
        )


    @staticmethod
    def gerar_imagem_mermaid(codigo_mermaid: str, output_path: str):
        encoded = base64.urlsafe_b64encode(codigo_mermaid.encode("utf-8")).decode("utf-8")
        url = f"https://mermaid.ink/img/{encoded}"
        
        response = httpx.get(url, timeout=30)
        response.raise_for_status()
        
        with open(output_path, "wb") as f:
            f.write(response.content)


    @staticmethod
    def markdown_para_elementos(markdown_texto, styles):

        html = markdown.markdown(markdown_texto)

        elementos = []

        for linha in html.split("\n"):

            if linha.strip():
                elementos.append(
                    Paragraph(
                        linha,
                        styles['BodyText']
                    )
                )

                elementos.append(
                    Spacer(1, 8)
                )

        return elementos
    
    @staticmethod
    def glossario_para_elementos(glossario_texto, styles):

        elementos = []

        try:
            glossario = json.loads(glossario_texto)
            for item in glossario:

                termo = item.get("termo", "")
                definicao = item.get("definicao", "")

                elementos.append(
                    Paragraph(
                        f"<b>{termo}</b>: {definicao}",
                        styles['BodyText']
                    )
                )

                elementos.append(
                    Spacer(1, 10)
                )

        except Exception:
            elementos.append(
                Paragraph(
                    "Glossário inválido.",
                    styles['BodyText']
                )
            )

        return elementos
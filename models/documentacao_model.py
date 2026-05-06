from sqlalchemy import Column, String, DateTime
from datetime import datetime
from database import Base
import uuid


class Projeto(Base):
    __tablename__ = "projetos"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    titulo_projeto = Column(String(200), nullable=False)
    descricao_projeto = Column(String(100), nullable=True)
    readme_projeto = Column(String(200), nullable=False, unique=True)
    wiki_projeto = Column(String(200), nullable=False)
    diagramas_projeto = Column(String(100), nullable=True)
    glossario_projeto = Column(String(200), nullable=False, unique=True)
    usuario_id = Column(String(200), nullable=False)
    criado_em = Column(DateTime, default=datetime.utcnow)
    atualizado_em = Column(DateTime, default=datetime.utcnow)
    github_url = Column(String(300), nullable=False)
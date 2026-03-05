from sqlalchemy import Column, String, DateTime
from datetime import datetime
from database import Base
import uuid

class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    nome_usuario = Column(String(200), nullable=False)
    cargo_usuario = Column(String(100), nullable=True)
    email_usuario = Column(String(200), nullable=False, unique=True)
    senha_usuario = Column(String(255), nullable=False)
    foto_usuario = Column(String(255), nullable=True)
    criado_em = Column(DateTime, default=datetime.utcnow)
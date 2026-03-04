from sqlalchemy import Column, String
from database import Base

class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(String(36), primary_key=True)
    nome_usuario = Column(String(200), nullable=False)
    email_usuario = Column(String(200), nullable=False)
    senha_usuario = Column(String(255), nullable=False)
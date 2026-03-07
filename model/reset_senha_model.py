from sqlalchemy import Column, String, DateTime, ForeignKey
from database import Base
import uuid
from datetime import datetime

class ResetSenha(Base):
    __tablename__ = "reset_senha"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    usuario_id = Column(String, ForeignKey("usuarios.id"))
    token = Column(String, unique=True)
    expira_em = Column(DateTime)
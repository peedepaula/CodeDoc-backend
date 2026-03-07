from sqlalchemy import Column, String, DateTime, ForeignKey
from database import Base
import uuid
from sqlalchemy.dialects.postgresql import UUID

class ResetEmail(Base):
    __tablename__ = "reset_email"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    usuario_id = Column(UUID(as_uuid=True), ForeignKey("usuarios.id", ondelete="CASCADE"), nullable=False)

    novo_email = Column(String, nullable=False)
    token = Column(String, unique=True, nullable=False)

    expira_em = Column(DateTime, nullable=False)
    criado_em = Column(DateTime)
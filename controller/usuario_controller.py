from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from model.usuario_model import Usuario
from database import get_db

router = APIRouter(prefix="/usuario", tags=["Usuários"])

@router.get("/usuarios")
def listar_usuarios(db: Session = Depends(get_db)):
    return db.query(Usuario).all()
from fastapi import Depends, HTTPException, status
from jose import JWTError, jwt
from sqlalchemy.orm import Session
from database import get_db
from model.usuario_model import Usuario
from utils.token import SECRET_KEY, ALGORITHM
from fastapi.security import HTTPBearer
from fastapi import Security

security = HTTPBearer()

def get_current_user(
    credentials = Security(security),
    db: Session = Depends(get_db)
):
    token = credentials.credentials

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")

        if user_id is None:
            raise HTTPException(status_code=401, detail="Token inválido")

    except JWTError:
        raise HTTPException(status_code=401, detail="Token inválido ou expirado")

    usuario = db.query(Usuario).filter(Usuario.id == user_id).first()

    if not usuario:
        raise HTTPException(status_code=401, detail="Usuário não encontrado")
    print(usuario)

    return usuario
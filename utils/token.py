from jose import JWTError, jwt
from datetime import datetime, timedelta, timezone
from uuid import UUID

SECRET_KEY = "SUA_CHAVE_SUPER_SECRETA"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_DAYS = 30

def criar_token(data: dict) -> str:
    to_encode = data.copy()

    # Converte automaticamente qualquer UUID para string
    for key, value in list(to_encode.items()):
        if isinstance(value, UUID):
            to_encode[key] = str(value)
        # caso esteja aninhado (menos comum, mas acontece)
        elif isinstance(value, dict):
            to_encode[key] = criar_token(value)  # recursivo, se quiser ser paranoico

    expire = datetime.now(timezone.utc) + timedelta(days=ACCESS_TOKEN_EXPIRE_DAYS)

    to_encode.update({
        "exp": expire,                # pode deixar datetime, jose aceita
        # "iat": datetime.now(timezone.utc),   # opcional
        # "jti": str(uuid.uuid4()),           # se for usar, sempre str!
    })

    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
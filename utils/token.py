from jose import JWTError, jwt
from datetime import datetime, timedelta, timezone
from uuid import UUID

SECRET_KEY = "SI3jSUhhjsdauaj37ISJDKjhausd8a9JSKjdiad89adhaknrk3j928r9ioajfskadhfjesury48wjkajopai3urhjahfjdsyf74yfjahiaoiojkojkyfigknmgfu8wy3g3788ruweofjdghurughrgs7ut6esggsyfusih7ftwefgyusuifhs78e7fsfuisheufid7fyesR"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_DAYS = 30

def criar_token(data: dict) -> str:
    to_encode = data.copy()

    for key, value in list(to_encode.items()):
        if isinstance(value, UUID):
            to_encode[key] = str(value)

        elif isinstance(value, dict):
            to_encode[key] = criar_token(value)

    expire = datetime.now(timezone.utc) + timedelta(days=ACCESS_TOKEN_EXPIRE_DAYS)

    to_encode.update({
        "exp": expire,
    })

    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
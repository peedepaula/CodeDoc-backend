from pydantic import BaseModel, EmailStr, Field

class usuarioCreate(BaseModel):
    nome_usuario: str
    email_usuario: EmailStr
    senha_usuario: str = Field(min_length=6, max_length=72)

class UsuarioLogin(BaseModel):
    email_usuario: EmailStr
    senha_usuario: str

class UsuarioUpdate(BaseModel):
    nome_usuario: str
    cargo_usuario: str
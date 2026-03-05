from pydantic import BaseModel
from typing import Optional

class ProjetoUpdate(BaseModel):
    titulo_projeto: str | None = None
    descricao_projeto: str | None = None
    readme_projeto: str | None = None
    wiki_projeto: str | None = None
    diagramas_projeto: str | None = None
    glossario_projeto: str | None = None

class ProjetoCriar(BaseModel):
    github_url: Optional[str] = None
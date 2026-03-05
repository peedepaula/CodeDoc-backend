from utils.github import baixar_repo, extrair_codigo
from utils.ia_utils import gerar_documentacao


def gerar_documentacao_github(github_url):
    repo_zip = baixar_repo(github_url)

    codigo = extrair_codigo(repo_zip)

    documentacao = gerar_documentacao(codigo)

    return documentacao
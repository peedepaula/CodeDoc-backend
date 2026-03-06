import secrets

def gerar_token_reset():
    return secrets.token_urlsafe(32)
import smtplib
from email.mime.text import MIMEText

EMAIL = "codedoc@gmail.com"
SENHA = "senha_app_gmail"

def enviar_email_reset(destinatario, link):

    corpo = f"""
    Clique no link para redefinir sua senha:

    {link}

    Esse link expira em 15 minutos.
    """

    msg = MIMEText(corpo)
    msg["Subject"] = "Recuperação de senha"
    msg["From"] = EMAIL
    msg["To"] = destinatario

    servidor = smtplib.SMTP("smtp.gmail.com", 587)
    servidor.starttls()
    servidor.login(EMAIL, SENHA)
    servidor.send_message(msg)
    servidor.quit()
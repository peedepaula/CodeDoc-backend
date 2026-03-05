import requests
import zipfile
import tempfile


def baixar_repo(url):

    url = url.replace(".git", "")
    url = url.rstrip("/")

    zip_url = f"{url}/archive/refs/heads/main.zip"

    r = requests.get(zip_url)

    if r.status_code != 200:
        zip_url = f"{url}/archive/refs/heads/master.zip"
        r = requests.get(zip_url)

    if r.status_code != 200:
        raise Exception("Erro ao baixar repositório")

    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        tmp.write(r.content)
        tmp.close()

        return tmp.name


def extrair_codigo(zip_path):

    codigo = ""

    with zipfile.ZipFile(zip_path, "r") as zip_ref:

        for nome in zip_ref.namelist():

            if nome.endswith((".py", ".js", ".ts", ".jsx", ".tsx", ".java", ".html", ".css")):

                try:
                    codigo += zip_ref.read(nome).decode(errors="ignore")
                except:
                    pass

    return codigo
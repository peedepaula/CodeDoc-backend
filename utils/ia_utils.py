from openai import OpenAI
import json

client = OpenAI()


def gerar_documentacao(codigo):

    prompt = f"""
Analise este código e gere documentação completa.

Responda APENAS em JSON no formato:

{{
 "titulo": "",
 "descricao": "",
 "readme": "",
 "wiki": "",
 "glossario": "",
 "diagrama": ""
}}

Código:
{codigo[:20000]}
"""

    response = client.responses.create(
        model="gpt-5-mini",
        input=prompt,
        max_output_tokens=10000
    )

    texto = response.output_text

    return json.loads(texto)
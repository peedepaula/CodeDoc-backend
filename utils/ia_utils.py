from openai import OpenAI
import json

client = OpenAI()

def gerar_documentacao(codigo):

    prompt = f"""
Analise o código fornecido e gere documentação técnica.

Responda APENAS com JSON válido.

Estrutura obrigatória:

{{
 "titulo": "titulo curto do projeto",
 "descricao": "explicação geral",
 "readme": "readme completo em markdown",
 "wiki": "explicação detalhada da arquitetura",
 "glossario": [
   {{
     "termo": "nome do termo",
     "definicao": "explicação"
   }}
 ],
 "diagrama": "codigo_mermaid"
}}

REGRAS IMPORTANTES:

- O JSON deve ser válido.
- Não coloque JSON dentro de strings.
- glossario DEVE ser um ARRAY de objetos.
- Cada objeto deve ter "termo" e "definicao".

REGRAS PARA O CAMPO "diagrama":

- Deve ser um diagrama Mermaid válido
- Deve começar obrigatoriamente com: flowchart TD
- Use setas --> para conectar etapas
- Cada etapa deve estar dentro de colchetes []
- Use <br/> para quebra de linha
- Use no máximo 15 nós
- NÃO use aspas dentro de []
- NÃO escreva explicações
- NÃO escreva markdown
- NÃO use ```mermaid
- NÃO use blocos de código

EXEMPLO CORRETO:

flowchart TD
A[Inicio] --> B[Receber requisicao]
B --> C{{Validacao}}
C -->|valido| D[Processar dados]
C -->|erro| E[Retornar erro]
D --> F[Salvar no banco]
F --> G[Fim]

Código para análise:

{codigo[:30000]}
"""

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "Você é um assistente especializado em documentação técnica."},
            {"role": "user", "content": prompt}
        ],
        response_format={"type": "json_object"},
        max_tokens=8000
    )

    texto = response.choices[0].message.content

    return json.loads(texto)
from openai import OpenAI
import json

client = OpenAI()


def gerar_documentacao(codigo):

    prompt = f"""
Analise este código e gere documentação completa.

Responda APENAS em JSON válido.

Formato obrigatório:

{{
 "titulo": "titulo curto do projeto",
 "descricao": "explicação geral",
 "readme": "readme completo em markdown",
 "wiki": "explicação detalhada da arquitetura",
 "glossario": "lista de termos importantes",
 "diagrama": "código do diagrama em sintaxe MERMAID flowchart"
}}

REGRAS IMPORTANTES PARA O CAMPO "diagrama":

- O diagrama DEVE usar sintaxe Mermaid.
- Use o formato flowchart TD.
- Use setas --> para conectar etapas.
- Cada etapa deve estar dentro de colchetes [].
- Use <br/> para quebrar linha dentro de caixas.
- NÃO escreva texto fora do diagrama.
- NÃO explique o diagrama.
- NÃO escreva markdown.
- Retorne apenas o código Mermaid.

Exemplo de formato correto para o campo "diagrama":

flowchart TD
A[Inicio] --> B[Processar dados]
B --> C{{Validação}}
C -->|válido| D[Salvar no banco]
C -->|inválido| E[Erro]
D --> F[Fim]

Código para análise:
{codigo[:20000]}
"""

    response = client.responses.create(
        model="gpt-5-mini",
        input=prompt,
        max_output_tokens=10000
    )

    texto = response.output_text

    return json.loads(texto)
"""
cap_08 — Exercício 3: Pipeline de Refatoração com GroupChat
Dificuldade: Difícil | Tempo estimado: ~2-3h

TAREFA:
Construa um pipeline de revisão e refatoração de código usando GroupChat
com 4 agentes especializados que colaboram iterativamente.

Agentes:
- Analyzer: identifica code smells e problemas de qualidade
- Refactorer: aplica as sugestões e produz código melhorado
- Tester: escreve testes unitários para o código refatorado
- Reviewer: aprovação final (TERMINATE se aprovado)

Requisitos:
1. Configure SelectorGroupChat com seleção round-robin customizada.
2. O Reviewer termina a conversa com "APPROVED" quando satisfeito.
3. Limite a 6 rodadas máximas de refinamento.
4. Salve o código refatorado final em cap_08/outputs/refactored.py.
5. Teste com um código Python intencionalmentente mal escrito (fornecido abaixo).

Código de teste:
def calc(x,y,z):
    r=0
    for i in range(x):
        r=r+y
    r=r*z
    return r
"""
import os
import asyncio
from dotenv import load_dotenv

load_dotenv()

CODE_TO_REFACTOR = """
def calc(x,y,z):
    r=0
    for i in range(x):
        r=r+y
    r=r*z
    return r
"""

OUTPUT_PATH = "cap_08/outputs/refactored.py"
os.makedirs("cap_08/outputs", exist_ok=True)

# TODO: configure os 4 agentes e o SelectorGroupChat


async def main():
    # TODO: execute o pipeline e salve o resultado
    pass


if __name__ == "__main__":
    asyncio.run(main())

"""
cap_04 — Exercício 2: Dupla Aprovação com HITL
Dificuldade: Médio | Tempo estimado: ~45 min

TAREFA:
Implemente um fluxo de dupla aprovação: a primeira para executar a ferramenta
e a segunda para confirmar o resultado antes de apresentar ao usuário.

Requisitos:
1. Configure interrupt_before=["tools"] E interrupt_after=["tools"].
2. Após a execução da ferramenta, pause e mostre o resultado bruto ao usuário.
3. Pergunte se o usuário deseja que o agente continue a análise.
4. Se não, retorne apenas o resultado bruto da ferramenta.
"""
import os
from dotenv import load_dotenv

load_dotenv()

# TODO: reconfigure o grafo do finance_bot com interrupt_after=["tools"]
# e implemente o loop de dupla aprovação


if __name__ == "__main__":
    print("Finance Bot — Dupla Aprovação HITL")
    # TODO: implemente o loop interativo com dupla confirmação

"""
cap_07 — Exercício 1: Adicionando um Novo Agente
Dificuldade: Fácil | Tempo estimado: ~20 min

TAREFA:
Adicione um terceiro agente ao chatbot de suporte LangGraph: um "Agente de FAQ"
que responde perguntas frequentes a partir de uma lista hardcoded, sem usar LLM.

Requisitos:
1. Crie um dict FAQ_DB com pelo menos 5 perguntas e respostas.
2. Implemente o nó faq_agent que busca por palavras-chave na query.
3. Adicione o roteamento: se a query tem correspondência no FAQ, vai para faq_agent.
4. Se não há correspondência, segue o fluxo normal (LLM).
"""
import os
from dotenv import load_dotenv

load_dotenv()

FAQ_DB = {
    "horário": "Nosso atendimento funciona de segunda a sexta, das 8h às 18h.",
    "prazo": "O prazo de entrega padrão é de 5 a 7 dias úteis.",
    "cancelamento": "Para cancelar um pedido, acesse Minha Conta > Pedidos > Cancelar.",
    # TODO: adicione mais entradas
}


def faq_agent_node(state: dict) -> dict:
    """Responde com base no FAQ sem chamar o LLM."""
    # TODO: implemente a busca por palavras-chave e retorne a resposta
    raise NotImplementedError


# TODO: integre ao grafo de cap_07/projeto/chatbot_suporte_langgraph.py


if __name__ == "__main__":
    query = "Qual é o horário de atendimento?"
    print(f"Query: {query}")
    # TODO: teste o agente FAQ

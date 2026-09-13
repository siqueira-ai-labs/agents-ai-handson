"""
cap_05 — Exercício 1: Adicionando uma Nova Fonte de Dados
Dificuldade: Fácil | Tempo estimado: ~20 min

TAREFA:
Adicione uma terceira fonte de dados ao analisador de vendas: um arquivo JSON
contendo dados de devoluções de produtos. O agente deve ser capaz de responder
perguntas que cruzem dados de vendas e devoluções.

Requisitos:
1. Crie cap_05/projeto/project_data/devolucoes.json com pelo menos 10 registros.
2. Crie uma nova QueryEngineTool para o arquivo JSON no LlamaIndex.
3. Adicione a tool ao agente junto com as existentes de CSV.
4. Teste com: "Qual produto teve maior taxa de devolução em relação às vendas?"
"""
import os
from dotenv import load_dotenv

load_dotenv()

# TODO: crie o arquivo devolucoes.json e configure a nova ferramenta no LlamaIndex


if __name__ == "__main__":
    query = "Qual produto teve maior taxa de devolução em relação às vendas?"
    print(f"Query: {query}")
    # TODO: invoque o agente

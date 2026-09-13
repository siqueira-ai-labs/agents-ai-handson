"""
cap_10 — Exercício 1: Adicionando Múltiplas Entradas
Dificuldade: Fácil | Tempo estimado: ~20 min

TAREFA:
Modifique a chamada ao fluxo Langflow para enviar múltiplas variáveis de entrada
via o parâmetro `tweaks`, permitindo personalização da resposta por usuário.

Requisitos:
1. Adicione tweaks para: nome_usuario, idioma e tom_resposta.
2. Verifique a aba "API" do Langflow para o formato correto do dicionário tweaks.
3. Teste com 3 combinações diferentes de usuário/idioma/tom.
"""
import os
from dotenv import load_dotenv
from cap_10.projeto.nocode_integration import run_flow

load_dotenv()


def run_personalized(message: str, nome: str, idioma: str, tom: str) -> dict:
    tweaks = {
        # TODO: mapeie os IDs dos componentes do seu fluxo Langflow
        # Exemplo: "ChatInput-xyz": {"user_name": nome}
    }
    return run_flow(message, tweaks=tweaks)


if __name__ == "__main__":
    scenarios = [
        ("Quero trocar um produto", "Ana", "português", "formal"),
        ("I need to return an item", "John", "english", "friendly"),
        ("Qual o prazo de entrega?", "Carlos", "português", "informal"),
    ]
    for msg, nome, idioma, tom in scenarios:
        print(f"\n--- {nome} ({idioma}, {tom}) ---")
        # result = run_personalized(msg, nome, idioma, tom)
        # print(result)

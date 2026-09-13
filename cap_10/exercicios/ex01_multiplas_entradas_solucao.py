"""
cap_10 — Solução Exercício 1: Adicionando Múltiplas Entradas
Dificuldade: Fácil | Tempo estimado: ~20 min
"""
import pathlib
import sys

from dotenv import load_dotenv

load_dotenv()

sys.path.insert(0, str(pathlib.Path(__file__).parent.parent / "projeto"))
from nocode_integration import run_flow  # noqa: E402


def build_tweaks(nome: str, idioma: str, tom: str) -> dict:
    """Monta o dicionário de tweaks para personalizar o fluxo Langflow.

    Os IDs de componente ("ChatInput-xxxx" etc.) são específicos de cada
    fluxo — copie-os da aba "API" do seu fluxo no Langflow e ajuste aqui.
    """
    return {
        "ChatInput-xxxx": {"sender_name": nome},
        "Prompt-xxxx": {"idioma": idioma, "tom_resposta": tom},
    }


def run_personalized(message: str, nome: str, idioma: str, tom: str) -> dict:
    tweaks = build_tweaks(nome, idioma, tom)
    return run_flow(message, tweaks=tweaks)


if __name__ == "__main__":
    scenarios = [
        ("Quero trocar um produto", "Ana", "português", "formal"),
        ("I need to return an item", "John", "english", "friendly"),
        ("Qual o prazo de entrega?", "Carlos", "português", "informal"),
    ]
    for msg, nome, idioma, tom in scenarios:
        print(f"\n--- {nome} ({idioma}, {tom}) ---")
        try:
            print(run_personalized(msg, nome, idioma, tom))
        except Exception as e:
            print(f"Langflow indisponível ({e}). Confira LANGFLOW_BASE_URL/LANGFLOW_FLOW_ID no .env.")

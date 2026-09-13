"""
cap_12 — Exercício 3: Moderação de Saída com Llama Guard 3
Dificuldade: Difícil | Tempo estimado: ~2-3h

TAREFA:
Integre o Llama Guard 3 (via Ollama local) como camada de moderação da SAÍDA
do agente, verificando se a resposta gerada é segura antes de retorná-la ao usuário.

Requisitos:
1. Configure `ollama pull meta-llama/llama-guard-3` (ou versão equivalente disponível).
2. Implemente output_moderator() que envia a resposta do agente ao Llama Guard.
3. Se a resposta for classificada como "unsafe", substitua por mensagem padrão.
4. Registre cada moderação com: input_hash, classification, categoria de risco.
5. Integre ao app.py do projeto como middleware Flask.

NOTA: Llama Guard classifica saídas em categorias S1-S14 (OWASP LLM Top 10).
"""
import os
import hashlib
import logging
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(filename="cap_12/moderation.log", level=logging.INFO)
logger = logging.getLogger("moderation")

SAFE_FALLBACK = "Não posso fornecer essa informação. Por favor, consulte um profissional."


def hash_content(text: str) -> str:
    """Gera hash SHA-256 do conteúdo para log sem armazenar o dado original."""
    return hashlib.sha256(text.encode()).hexdigest()[:16]


def moderate_output(agent_response: str) -> tuple[str, bool]:
    """
    Modera a saída do agente com Llama Guard via Ollama.
    Retorna (resposta_final, foi_bloqueada).
    """
    # TODO: implemente chamada ao Ollama com o modelo llama-guard-3
    # Prompt padrão do Llama Guard: "Task: Check if there is unsafe content..."
    # Retorno esperado: "safe" ou "unsafe\n<categoria>"
    raise NotImplementedError


def create_moderation_middleware(app, agent_fn):
    """Envolve a função do agente com moderação de saída."""
    # TODO: implemente como decorator Flask ou wrapper de função
    raise NotImplementedError


if __name__ == "__main__":
    test_responses = [
        "A taxa Selic está em 10,5% ao ano, com expectativa de queda no próximo trimestre.",
        "Para maximizar retornos, você deveria investir toda sua poupança em criptomoedas.",
    ]
    for response in test_responses:
        try:
            final, blocked = moderate_output(response)
            status = "BLOQUEADO" if blocked else "APROVADO"
            print(f"[{status}] {response[:60]}")
        except NotImplementedError:
            print(f"TODO: implemente moderate_output() | Entrada: {response[:60]}")

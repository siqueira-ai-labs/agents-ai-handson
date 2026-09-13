"""
cap_12 — Exercício 1: Expandindo o Bloqueio de PII
Dificuldade: Fácil | Tempo estimado: ~20 min

TAREFA:
Adicione detecção de PII (Personally Identifiable Information) ao pipeline
do guardrail. O agente não deve processar nem retornar dados sensíveis.

Tipos de PII a bloquear:
- CPF (formato: 000.000.000-00)
- Número de cartão de crédito (16 dígitos)
- Endereço de e-mail

Requisitos:
1. Use regex para detectar os padrões de PII na entrada do usuário.
2. Se PII detectado, retorne uma mensagem padrão sem processar a query.
3. Registre (sem logar o PII em si) quantas vezes cada tipo foi detectado.
4. Adicione testes unitários para os 3 padrões.
"""
import re
import pytest


PII_PATTERNS = {
    "cpf": re.compile(r"\b\d{3}\.\d{3}\.\d{3}-\d{2}\b"),
    "credit_card": re.compile(r"\b(?:\d{4}[\s-]?){3}\d{4}\b"),
    "email": re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"),
}

pii_detection_count: dict[str, int] = {k: 0 for k in PII_PATTERNS}


def detect_pii(text: str) -> list[str]:
    """Retorna lista de tipos de PII encontrados (sem o dado em si)."""
    found = []
    for pii_type, pattern in PII_PATTERNS.items():
        if pattern.search(text):
            found.append(pii_type)
            pii_detection_count[pii_type] += 1
    return found


def sanitize_input(text: str) -> tuple[str, list[str]]:
    """Retorna (texto_seguro, tipos_de_pii_removidos)."""
    pii_types = detect_pii(text)
    if not pii_types:
        return text, []
    return "Sua mensagem contém dados sensíveis e não pode ser processada.", pii_types


# --- Testes ---
def test_cpf_detection():
    assert "cpf" in detect_pii("Meu CPF é 123.456.789-00")


def test_credit_card_detection():
    assert "credit_card" in detect_pii("Cartão 4111 1111 1111 1111")


def test_email_detection():
    assert "email" in detect_pii("Entre em contato: usuario@exemplo.com")


def test_no_pii():
    assert detect_pii("Qual é a cotação do Bitcoin?") == []


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

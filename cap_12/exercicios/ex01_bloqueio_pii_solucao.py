"""
cap_12 — Solução Exercício 1: Expandindo o Bloqueio de PII
Dificuldade: Fácil | Tempo estimado: ~20 min
"""
import re

PII_PATTERNS = {
    "cpf": re.compile(r"\b\d{3}\.\d{3}\.\d{3}-\d{2}\b"),
    "credit_card": re.compile(r"\b(?:\d{4}[\s-]?){3}\d{4}\b"),
    "email": re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"),
}

pii_detection_count: dict[str, int] = {k: 0 for k in PII_PATTERNS}

BLOCKED_MESSAGE = "Sua mensagem contém dados sensíveis e não pode ser processada."


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
    return BLOCKED_MESSAGE, pii_types


if __name__ == "__main__":
    exemplos = [
        "Meu CPF é 123.456.789-00",
        "Cartão 4111 1111 1111 1111",
        "Entre em contato: usuario@exemplo.com",
        "Qual é a cotação do Bitcoin?",
    ]
    for texto in exemplos:
        seguro, tipos = sanitize_input(texto)
        print(f"[{'BLOQUEADO' if tipos else 'OK'}] {texto[:40]!r} -> tipos={tipos}")

    print("\nContagem de detecções:", pii_detection_count)

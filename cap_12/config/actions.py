# Ações personalizadas do NeMo Guardrails
# Adicione aqui funções Python que podem ser chamadas pelos fluxos do guardrail
import logging
import pathlib
import re

from nemoguardrails.actions import action

LOG_PATH = pathlib.Path(__file__).parent.parent / "security.log"
logger = logging.getLogger("security")
logger.setLevel(logging.WARNING)
if not logger.handlers:
    _handler = logging.FileHandler(str(LOG_PATH))
    _handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
    logger.addHandler(_handler)

INJECTION_PATTERNS = [
    # Inglês
    re.compile(r"ignore\s+(all\s+)?previous\s+instructions", re.IGNORECASE),
    re.compile(r"you\s+are\s+now\s+a", re.IGNORECASE),
    re.compile(r"act\s+as\s+(if\s+you\s+are|a)", re.IGNORECASE),
    re.compile(r"forget\s+(your\s+)?(previous\s+)?instructions", re.IGNORECASE),
    re.compile(r"your\s+new\s+(system\s+)?prompt\s+is", re.IGNORECASE),
    # Português — o bot atende usuários em pt-BR, então os ataques também vêm em pt-BR.
    re.compile(r"ignore\s+(todas\s+)?as\s+instru[cç][oõ]es\s+anteriores", re.IGNORECASE),
    re.compile(r"voc[eê]\s+(agora\s+)?[eé]\s+(agora\s+)?um[a]?", re.IGNORECASE),
    re.compile(r"aja\s+como\s+(se\s+voc[eê]\s+fosse|um[a]?)", re.IGNORECASE),
    re.compile(r"esque[cç]a\s+(suas\s+)?(as\s+)?instru[cç][oõ]es", re.IGNORECASE),
    re.compile(r"seu\s+novo\s+prompt\s+(de\s+sistema\s+)?[eé]", re.IGNORECASE),
]


def check_prompt_injection(user_input: str) -> dict:
    """Detecta tentativas de prompt injection. Retorna {"safe": bool, "pattern": str|None}."""
    for pattern in INJECTION_PATTERNS:
        if pattern.search(user_input):
            logger.warning(f"Prompt injection detectado: padrão '{pattern.pattern[:30]}'")
            return {"safe": False, "pattern": pattern.pattern[:30]}
    return {"safe": True, "pattern": None}


@action(name="check_prompt_injection")
async def check_prompt_injection_action(context: dict) -> dict:
    """Action NeMo que expõe check_prompt_injection ao fluxo 'detect prompt injection'."""
    user_input = context.get("user_message", "")
    return check_prompt_injection(user_input)

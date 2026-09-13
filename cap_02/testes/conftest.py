"""Configurações e fixtures globais para os testes do cap_02."""
import pathlib
import sys

# Garante que 'exercicios' está sempre no path, independente de onde pytest é chamado
_EXERCICIOS = str(pathlib.Path(__file__).parent.parent / "exercicios")
if _EXERCICIOS not in sys.path:
    sys.path.insert(0, _EXERCICIOS)

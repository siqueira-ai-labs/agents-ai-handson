"""Garante que o diretório de exercícios está no sys.path para todos os testes."""
import pathlib
import sys

_EXERCICIOS = str(pathlib.Path(__file__).parent)
if _EXERCICIOS not in sys.path:
    sys.path.insert(0, _EXERCICIOS)

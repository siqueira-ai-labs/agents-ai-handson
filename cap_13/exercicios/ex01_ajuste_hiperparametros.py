"""
cap_13 — Exercício 1: Ajuste de Hiperparâmetros no LoRA
Dificuldade: Fácil | Tempo estimado: ~20 min

TAREFA:
Modifique a configuração LoRA do projeto e compare os resultados de treino
com diferentes combinações de rank (r) e alpha.

Combinações a testar:
- r=8, alpha=16 (padrão)
- r=16, alpha=32 (maior capacidade)
- r=4, alpha=8 (mais leve)

Requisitos:
1. Configure LoraConfig com cada combinação.
2. Monitore: loss de treino, número de parâmetros treináveis, tempo de treino.
3. Salve um CSV com os resultados em cap_13/lora_experiments.csv.
4. Identifique qual configuração deu melhor trade-off qualidade/velocidade.

NOTA: Requer GPU NVIDIA. Para CPU/Colab, use r=4 para menor tempo de treino.
"""
import os
from dotenv import load_dotenv

load_dotenv()

CONFIGS = [
    {"r": 8, "lora_alpha": 16, "label": "default"},
    {"r": 16, "lora_alpha": 32, "label": "larger"},
    {"r": 4, "lora_alpha": 8, "label": "lighter"},
]

# TODO: implemente o loop de experimentos com peft.LoraConfig
# TODO: salve os resultados em lora_experiments.csv


if __name__ == "__main__":
    print("Experimentos LoRA — requer GPU NVIDIA ou Google Colab")
    for config in CONFIGS:
        print(f"  r={config['r']}, alpha={config['lora_alpha']} ({config['label']})")

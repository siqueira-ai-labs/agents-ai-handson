"""
cap_13 — Exercício 3: Quantização Extrema e Deploy Local
Dificuldade: Difícil | Tempo estimado: ~2-3h

TAREFA:
Aplique QLoRA (4-bit) para fine-tuning de um modelo 7B e faça o deploy local
via Ollama, comparando inferência quantizada vs FP16.

Requisitos:
1. Configure BitsAndBytesConfig para quantização NF4 (4-bit).
2. Aplique LoRA sobre o modelo quantizado com r=8.
3. Treine por 1 época no dataset de function calling do cap_13.
4. Mescle os adaptadores LoRA e exporte o modelo no formato GGUF para Ollama.
5. Benchmark: compare latência e qualidade (FP16 vs NF4) com 10 queries.

NOTA: Requer GPU NVIDIA com ≥ 8 GB VRAM para modelo 7B com QLoRA.
Para ambiente sem GPU: use Google Colab Pro ou SageMaker.
"""
import os
from dotenv import load_dotenv

load_dotenv()

# TODO: implemente com transformers + peft + bitsandbytes
# Referência: https://github.com/artidoro/qlora


QLORA_CONFIG = {
    "load_in_4bit": True,
    "bnb_4bit_compute_dtype": "float16",
    "bnb_4bit_quant_type": "nf4",
    "bnb_4bit_use_double_quant": True,
}

LORA_CONFIG = {
    "r": 8,
    "lora_alpha": 16,
    "target_modules": ["q_proj", "v_proj"],
    "lora_dropout": 0.05,
    "bias": "none",
    "task_type": "CAUSAL_LM",
}

BENCHMARK_QUERIES = [
    "Qual a diferença entre ações ON e PN?",
    "O que é diversificação de carteira?",
    "Explique o Índice de Sharpe.",
]

if __name__ == "__main__":
    print("QLoRA fine-tuning — requer GPU NVIDIA ≥ 8 GB VRAM")
    print("Alternativa gratuita: github.com/powerrandman/agents-ai-handson → notebooks/qlora_colab.ipynb")

"""
cap_13 — Solução Exercício 1: Ajuste de Hiperparâmetros no LoRA
Dificuldade: Fácil | Tempo estimado: ~20 min

Usa um modelo GPT-2 minúsculo (sshleifer/tiny-gpt2) para que o experimento
rode em CPU em segundos — os mesmos princípios (r, alpha, contagem de
parâmetros treináveis) se aplicam a modelos maiores como Llama, só troque
`MODEL_NAME` e `target_modules` (para Llama: ["q_proj", "v_proj"]).
"""
import csv
import pathlib
import time

from dotenv import load_dotenv
from peft import LoraConfig, get_peft_model
from transformers import AutoModelForCausalLM, AutoTokenizer

load_dotenv()

MODEL_NAME = "sshleifer/tiny-gpt2"
RESULTS_PATH = pathlib.Path(__file__).parent.parent / "lora_experiments.csv"

CONFIGS = [
    {"r": 8, "lora_alpha": 16, "label": "default"},
    {"r": 16, "lora_alpha": 32, "label": "larger"},
    {"r": 4, "lora_alpha": 8, "label": "lighter"},
]

TRAIN_TEXTS = [
    "O RAG combina recuperação de documentos com geração de texto.",
    "LoRA treina apenas uma pequena fração dos parâmetros do modelo.",
    "QLoRA aplica LoRA sobre um modelo quantizado em 4 bits.",
]


def count_trainable_params(model) -> tuple[int, int]:
    """Retorna (parâmetros treináveis, parâmetros totais)."""
    trainable = sum(p.numel() for p in model.parameters() if p.requires_grad)
    total = sum(p.numel() for p in model.parameters())
    return trainable, total


def run_experiment(config: dict, tokenizer, base_model_name: str = MODEL_NAME) -> dict:
    """Aplica uma config LoRA, roda um passo de treino de exemplo e mede o resultado."""
    model = AutoModelForCausalLM.from_pretrained(base_model_name)

    lora_config = LoraConfig(
        r=config["r"],
        lora_alpha=config["lora_alpha"],
        target_modules=["c_attn"],  # GPT-2; para Llama use ["q_proj", "v_proj"]
        fan_in_fan_out=True,  # GPT-2 usa Conv1D (pesos transpostos) em vez de Linear
        lora_dropout=0.05,
        bias="none",
        task_type="CAUSAL_LM",
    )
    peft_model = get_peft_model(model, lora_config)
    trainable, total = count_trainable_params(peft_model)

    batch = tokenizer(TRAIN_TEXTS, return_tensors="pt", padding=True, truncation=True)
    batch["labels"] = batch["input_ids"].clone()

    start = time.time()
    outputs = peft_model(**batch)
    loss = outputs.loss
    loss.backward()
    elapsed = time.time() - start

    return {
        "label": config["label"],
        "r": config["r"],
        "lora_alpha": config["lora_alpha"],
        "trainable_params": trainable,
        "total_params": total,
        "trainable_pct": round(100 * trainable / total, 4),
        "loss": round(loss.item(), 4),
        "time_sec": round(elapsed, 4),
    }


def run_all_experiments(configs: list[dict] = CONFIGS) -> list[dict]:
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    return [run_experiment(cfg, tokenizer) for cfg in configs]


def save_results(results: list[dict], path: pathlib.Path = RESULTS_PATH) -> None:
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(results[0].keys()))
        writer.writeheader()
        writer.writerows(results)


def best_tradeoff(results: list[dict]) -> dict:
    """Melhor trade-off qualidade/velocidade: menor loss por segundo de treino."""
    return min(results, key=lambda r: r["loss"] * r["time_sec"])


if __name__ == "__main__":
    resultados = run_all_experiments()
    save_results(resultados)
    print(f"Resultados salvos em {RESULTS_PATH}\n")
    for r in resultados:
        print(f"{r['label']:8s} r={r['r']:2d} alpha={r['lora_alpha']:2d} | "
              f"treináveis={r['trainable_params']} ({r['trainable_pct']}%) | "
              f"loss={r['loss']} | tempo={r['time_sec']}s")

    melhor = best_tradeoff(resultados)
    print(f"\nMelhor trade-off qualidade/velocidade: {melhor['label']}")

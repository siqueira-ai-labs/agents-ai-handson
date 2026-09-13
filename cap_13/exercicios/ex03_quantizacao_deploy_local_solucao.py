"""
cap_13 — Solução Exercício 3: Quantização Extrema e Deploy Local
Dificuldade: Difícil | Tempo estimado: ~2-3h

NOTA: Requer GPU NVIDIA com >= 8 GB VRAM para o modelo 7B alvo. A conversão
para GGUF depende do conversor do llama.cpp (ferramenta externa, não uma
biblioteca Python) — este script chama o script `convert_hf_to_gguf.py` do
repositório llama.cpp via subprocess; ajuste LLAMA_CPP_DIR para onde você
clonou https://github.com/ggerganov/llama.cpp.
"""
import os
import pathlib
import subprocess
import time

from dotenv import load_dotenv
from peft import LoraConfig
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig

load_dotenv()

BASE_MODEL = os.getenv("BASE_MODEL_7B", "meta-llama/Llama-2-7b-hf")
OUTPUT_DIR = pathlib.Path(__file__).parent.parent / "outputs" / "qlora-merged"
GGUF_OUTPUT = pathlib.Path(__file__).parent.parent / "outputs" / "model-q4_k_m.gguf"
LLAMA_CPP_DIR = pathlib.Path(os.getenv("LLAMA_CPP_DIR", "~/llama.cpp")).expanduser()

QLORA_CONFIG = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_compute_dtype="float16",
    bnb_4bit_quant_type="nf4",
    bnb_4bit_use_double_quant=True,
)

LORA_CONFIG = LoraConfig(
    r=8,
    lora_alpha=16,
    target_modules=["q_proj", "v_proj"],
    lora_dropout=0.05,
    bias="none",
    task_type="CAUSAL_LM",
)

BENCHMARK_QUERIES = [
    "Qual a diferença entre ações ON e PN?",
    "O que é diversificação de carteira?",
    "Explique o Índice de Sharpe.",
]


def load_quantized_model(model_name: str = BASE_MODEL):
    """Carrega o modelo base em 4-bit (NF4) para treino com QLoRA."""
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    model = AutoModelForCausalLM.from_pretrained(
        model_name,
        quantization_config=QLORA_CONFIG,
        device_map="auto",
    )
    return model, tokenizer


def train_qlora(model, tokenizer, train_texts: list[str], output_dir: pathlib.Path = OUTPUT_DIR):
    """Treina 1 época com SFTTrainer (trl) sobre o dataset de function calling do capítulo."""
    from datasets import Dataset
    from peft import get_peft_model
    from trl import SFTConfig, SFTTrainer

    peft_model = get_peft_model(model, LORA_CONFIG)
    dataset = Dataset.from_dict({"text": train_texts})

    sft_config = SFTConfig(
        output_dir=str(output_dir),
        num_train_epochs=1,
        per_device_train_batch_size=1,
        gradient_accumulation_steps=4,
        logging_steps=1,
        save_strategy="epoch",
    )
    trainer = SFTTrainer(
        model=peft_model,
        args=sft_config,
        train_dataset=dataset,
        tokenizer=tokenizer,  # trl 0.11.x usa `tokenizer`; versões mais novas usam `processing_class`
    )
    trainer.train()
    return peft_model


def merge_and_export(peft_model, tokenizer, output_dir: pathlib.Path = OUTPUT_DIR) -> pathlib.Path:
    """Mescla os adaptadores LoRA no modelo base e salva em disco."""
    merged = peft_model.merge_and_unload()
    output_dir.mkdir(parents=True, exist_ok=True)
    merged.save_pretrained(str(output_dir))
    tokenizer.save_pretrained(str(output_dir))
    return output_dir


def convert_to_gguf(merged_dir: pathlib.Path = OUTPUT_DIR, gguf_path: pathlib.Path = GGUF_OUTPUT) -> pathlib.Path:
    """Converte o modelo mesclado para GGUF (quantização Q4_K_M) via llama.cpp."""
    convert_script = LLAMA_CPP_DIR / "convert_hf_to_gguf.py"
    if not convert_script.exists():
        raise FileNotFoundError(
            f"Script de conversão não encontrado em {convert_script}. "
            f"Clone https://github.com/ggerganov/llama.cpp e ajuste LLAMA_CPP_DIR."
        )
    gguf_path.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        ["python3", str(convert_script), str(merged_dir), "--outfile", str(gguf_path), "--outtype", "q4_k_m"],
        check=True,
    )
    return gguf_path


def benchmark_inference(model, tokenizer, queries: list[str] = BENCHMARK_QUERIES) -> list[dict]:
    """Mede a latência de inferência do modelo (quantizado ou não) para cada query."""
    results = []
    for query in queries:
        inputs = tokenizer(query, return_tensors="pt").to(model.device)
        start = time.time()
        output_ids = model.generate(**inputs, max_new_tokens=50)
        elapsed = time.time() - start
        texto = tokenizer.decode(output_ids[0], skip_special_tokens=True)
        results.append({"query": query, "latency_sec": round(elapsed, 3), "output": texto})
    return results


if __name__ == "__main__":
    print("QLoRA fine-tuning — requer GPU NVIDIA >= 8 GB VRAM")
    print("Alternativa gratuita: github.com/powerrandman/agents-ai-handson → notebooks/qlora_colab.ipynb")

    model, tokenizer = load_quantized_model()
    peft_model = train_qlora(model, tokenizer, train_texts=[
        "Pergunta: Qual a cotação da PETR4? Resposta: chamando get_stock_price(ticker='PETR4.SA')",
    ])
    merged_dir = merge_and_export(peft_model, tokenizer)
    print(f"Modelo mesclado salvo em {merged_dir}")

    resultados_nf4 = benchmark_inference(peft_model, tokenizer)
    for r in resultados_nf4:
        print(f"[NF4] {r['latency_sec']}s — {r['query']}")

    try:
        gguf_path = convert_to_gguf(merged_dir)
        print(f"GGUF exportado em {gguf_path} — importe no Ollama com um Modelfile apontando para esse arquivo.")
    except FileNotFoundError as e:
        print(f"Conversão para GGUF pulada: {e}")

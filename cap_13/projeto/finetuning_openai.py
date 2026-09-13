"""
cap_13 — Fine-Tuning de Function Calling via API OpenAI
Módulo 14: Fine-Tuning vs. RAG

NOTA: Este script requer uma conta OpenAI (não OpenRouter).
Configure OPENAI_API_KEY no .env — custo estimado: ~$1-5 para dataset pequeno.

Por segurança (evitar custo acidental), upload + início do job de
fine-tuning só rodam se a variável de ambiente RUN_FINETUNE=1 estiver
definida. Sem ela, o script só gera e valida os arquivos JSONL localmente.
"""
import json
import os
import pathlib

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

DATA_DIR = pathlib.Path(__file__).parent.parent
TRAINING_FILE = DATA_DIR / "training_data.jsonl"
VALIDATION_FILE = DATA_DIR / "validation_data.jsonl"

# Ferramenta de exemplo usada nos dados de treino — o modelo aprende a
# chamá-la corretamente a partir dos exemplos rotulados.
GET_STOCK_PRICE_TOOL = {
    "type": "function",
    "function": {
        "name": "get_stock_price",
        "description": "Retorna a cotação atual de uma ação pelo ticker.",
        "parameters": {
            "type": "object",
            "properties": {"ticker": {"type": "string"}},
            "required": ["ticker"],
        },
    },
}

TRAINING_EXAMPLES = [
    ("Qual o preço da ação da Petrobras (PETR4)?", "get_stock_price", {"ticker": "PETR4.SA"}),
    ("Quanto está a Vale hoje?", "get_stock_price", {"ticker": "VALE3.SA"}),
    ("Cotação da Apple agora?", "get_stock_price", {"ticker": "AAPL"}),
    ("Preço atual das ações da Tesla", "get_stock_price", {"ticker": "TSLA"}),
]

VALIDATION_EXAMPLES = [
    ("Qual o valor da ação do Itaú (ITUB4)?", "get_stock_price", {"ticker": "ITUB4.SA"}),
]


def create_training_example(user_msg: str, function_name: str, arguments: dict) -> dict:
    """Cria um exemplo no formato de tool calling para fine-tuning (schema atual da
    API OpenAI — o formato function_call/functions foi descontinuado em favor de
    tool_calls/tools)."""
    return {
        "messages": [
            {"role": "system", "content": "Você é um assistente financeiro especializado."},
            {"role": "user", "content": user_msg},
            {
                "role": "assistant",
                "content": None,
                "tool_calls": [
                    {
                        "id": "call_1",
                        "type": "function",
                        "function": {
                            "name": function_name,
                            "arguments": json.dumps(arguments, ensure_ascii=False),
                        },
                    }
                ],
            },
        ],
        "tools": [GET_STOCK_PRICE_TOOL],
    }


def build_dataset_file(examples: list[tuple[str, str, dict]], path: pathlib.Path) -> pathlib.Path:
    """Gera um arquivo JSONL de treino/validação a partir de (user_msg, function_name, arguments)."""
    with path.open("w", encoding="utf-8") as f:
        for user_msg, function_name, arguments in examples:
            example = create_training_example(user_msg, function_name, arguments)
            f.write(json.dumps(example, ensure_ascii=False) + "\n")
    return path


def upload_training_file(file_path: str) -> str:
    """Faz upload do arquivo de treino e retorna o file_id."""
    with open(file_path, "rb") as f:
        response = client.files.create(file=f, purpose="fine-tune")
    print(f"Arquivo enviado: {response.id}")
    return response.id


def start_finetuning(training_file_id: str, validation_file_id: str | None = None) -> str:
    """Inicia o job de fine-tuning e retorna o job_id."""
    params = {
        "training_file": training_file_id,
        "model": "gpt-4o-mini-2024-07-18",
        "hyperparameters": {"n_epochs": 3},
    }
    if validation_file_id:
        params["validation_file"] = validation_file_id

    job = client.fine_tuning.jobs.create(**params)
    print(f"Job iniciado: {job.id}")
    return job.id


def check_status(job_id: str) -> dict:
    """Verifica o status de um job de fine-tuning."""
    job = client.fine_tuning.jobs.retrieve(job_id)
    return {"status": job.status, "model": job.fine_tuned_model}


if __name__ == "__main__":
    build_dataset_file(TRAINING_EXAMPLES, TRAINING_FILE)
    build_dataset_file(VALIDATION_EXAMPLES, VALIDATION_FILE)
    print(f"Dataset de treino gerado: {TRAINING_FILE} ({len(TRAINING_EXAMPLES)} exemplos)")
    print(f"Dataset de validação gerado: {VALIDATION_FILE} ({len(VALIDATION_EXAMPLES)} exemplos)")

    if os.getenv("RUN_FINETUNE") != "1":
        print("\nRUN_FINETUNE não está definida como '1' — pulando upload e início do "
              "job (evita custo acidental). Defina RUN_FINETUNE=1 para prosseguir de verdade.")
    else:
        training_file_id = upload_training_file(str(TRAINING_FILE))
        validation_file_id = upload_training_file(str(VALIDATION_FILE))
        job_id = start_finetuning(training_file_id, validation_file_id)
        print(f"Acompanhe o status com check_status('{job_id}')")

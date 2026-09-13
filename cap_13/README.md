# cap_13 — Módulo 14: Fine-Tuning vs. RAG

## Objetivo
Entender quando usar RAG vs fine-tuning, implementar LoRA/QLoRA eficiente
e criar um pipeline híbrido para casos de uso reais.

## Duas abordagens de fine-tuning

### Via API OpenAI (recomendada — sem GPU)
```bash
source cap_13/.myenv/bin/activate
pip install openai python-dotenv
# Requer OPENAI_API_KEY (conta OpenAI, não OpenRouter)
```

### Local com QLoRA (requer GPU NVIDIA)
```bash
pip install -r cap_13/requirements-cap13.txt
# Alternativa gratuita: Google Colab + Unsloth
# Ver: github.com/powerrandman/agents-ai-handson → notebooks/
```

## Projeto Principal
| Arquivo | Descrição |
|---|---|
| `projeto/finetuning_openai.py` | Fine-tuning via API OpenAI (function calling) |
| `projeto/rag_pipeline.py` | Pipeline RAG de referência para comparação |

## Exercícios
| # | Arquivo | Dificuldade | Tempo |
|---|---|---|---|
| 1 | `exercicios/ex01_ajuste_hiperparametros.py` | Fácil | ~20 min |
| 2 | `exercicios/ex02_hibridizacao_rag_fallback.py` | Médio | ~45 min |
| 3 | `exercicios/ex03_quantizacao_deploy_local.py` | Difícil | ~2-3h |

## Alternativa Local
```bash
pip install langchain-ollama
ollama pull qwen3.5:7b
```
Ver `local/rag_pipeline_ollama.py` (lado RAG do capítulo, 100% local). O
fine-tuning com QLoRA já é local por natureza — veja
`exercicios/ex03_quantizacao_deploy_local_solucao.py` (requer GPU).

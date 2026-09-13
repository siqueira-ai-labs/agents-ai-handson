# cap_15 — Bônus: Agentes na Nuvem (AWS, Azure, GCP)

## Objetivo
Deploy multi-cloud de um agente serverless "Cloud Cost Analyst" que consulta
custos de infraestrutura em múltiplos provedores.

## Arquitetura
```
handler.py   ← ponto de entrada serverless (Lambda / Azure Functions / GCP Functions)
agent.py     ← grafo LangGraph do agente
tools.py     ← ferramentas de consulta de custos por provider
requirements.txt
```

## Setup por provider
### AWS Lambda
```bash
pip install -r cap_15/requirements-cap15.txt
# Configure credenciais: aws configure
```

### Azure Functions
```bash
az login
```

### GCP Cloud Functions
```bash
gcloud auth login
```

## Exercícios
| # | Arquivo | Dificuldade | Tempo |
|---|---|---|---|
| 1 | `exercicios/ex01_novo_provider_fallback.py` | Fácil | ~20 min |
| 2 | `exercicios/ex02_analise_custos_multicloud.py` | Médio | ~45 min |
| 3 | `exercicios/ex03_roteamento_dinamico.py` | Difícil | ~2-3h |

## Alternativa Local
```bash
pip install langchain-ollama
ollama pull qwen3.5:7b
```
Ver `local/agent_ollama.py`. As tools de custo continuam chamando as APIs
reais de AWS/Azure/GCP (não têm equivalente local) — só o raciocínio do
agente roda localmente.

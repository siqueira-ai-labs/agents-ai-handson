# Agentes de IA Hands-On: Do Protótipo à Produção

Repositório oficial do livro — todos os projetos, exercícios e gabaritos organizados por capítulo.

## Estrutura

```
.myenv/                     ← ambiente virtual compartilhado (Python 3.12)
modulo-00-avisos/           ← Avisos críticos e configuração inicial
modulo-01-llm-fundamentos/  ← Como os LLMs funcionam (teoria)
cap_01/                     ← Módulo 2: Fundamentos da IA Agentiva
cap_02/                     ← Módulo 3: Arquiteturas e Padrões de Design
cap_03/                     ← Módulo 4: LangChain e LCEL na Prática
cap_04/                     ← Módulo 5: Construindo Agentes com LangGraph
cap_05/                     ← Módulo 6: RAG Agentivo (Agentic RAG)
cap_06/                     ← Módulo 7: Desenvolvendo Agentes com Phidata
cap_07/                     ← Módulo 8: Sistemas Multiagente (LangGraph + CrewAI)
cap_08/                     ← Módulo 9: Desenvolvimento Avançado com Autogen
cap_09/                     ← Módulo 10: Observabilidade (Langfuse, Langsmith, AgentOps)
cap_10/                     ← Módulo 11: Agentes No-Code/Low-Code
cap_11/                     ← Módulo 12: Avaliação de Agentes (Agent Evaluation)
cap_12/                     ← Módulo 13: Segurança e Guardrails Avançados
cap_13/                     ← Módulo 14: Fine-Tuning vs. RAG
cap_14/                     ← Módulo 15: Gerenciamento de Estado Distribuído
cap_15/                     ← Bônus: Agentes na Nuvem (AWS, Azure, GCP)
apendice-e-llms-opensource/ ← Apêndice E: LLMs Open-Source na Prática
```

Cada `cap_NN/` contém:
- `requirements-cap_NN.txt` — dependências pinadas
- `projeto/` — código do projeto principal do capítulo
- `exercicios/` — esqueletos dos exercícios (ex01, ex02, ex03) e suas respectivas soluções
- `local/` — alternativa 100% local via Ollama (onde disponível)

## Início Rápido

```bash
# 1. Ativar o ambiente virtual
source .myenv/bin/activate

# 2. Copiar e configurar variáveis de ambiente
cp .env.example .env
# edite .env com suas chaves de API

# 3. Instalar dependências do capítulo desejado (ex: cap_01)
pip install -r cap_01/requirements-cap01.txt
```

## Gabaritos

Os gabaritos dos exercícios ficam na própria pasta com sufixo `_solucao.pu`:

## Provider LLM

Este livro usa **OpenRouter** (openrouter.ai) como provider padrão.
Crie sua chave gratuita em openrouter.ai/keys e adicione ao `.env`.

Para execução 100% local sem API, veja `apendice-e-llms-opensource/`.

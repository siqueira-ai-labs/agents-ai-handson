# cap_08 — Módulo 9: Desenvolvimento Avançado com Autogen

## Objetivo
Dominar a arquitetura dual Core/AgentChat do AutoGen para construir um
agente de pesquisa científica com execução de código e GroupChat.

## Setup
```bash
source cap_08/.myenv/bin/activate
pip install -r cap_08/requirements-cap08.txt
```

## Projeto Principal
| Arquivo | Descrição |
|---|---|
| `projeto/pesquisa_cientifica.py` | Agente de pesquisa com Pesquisador + Revisor |

## Exercícios
| # | Arquivo | Dificuldade | Tempo |
|---|---|---|---|
| 1 | `exercicios/ex01_critico_fibonacci.py` | Fácil | ~20 min |
| 2 | `exercicios/ex02_tratamento_falhas.py` | Médio | ~45 min |
| 3 | `exercicios/ex03_refatoracao_groupchat.py` | Difícil | ~2-3h |

## Nota sobre execução de código
No AutoGen v0.4, quem executa código é o `CodeExecutorAgent` (não mais o
`UserProxyAgent`, que agora serve apenas para input humano). O executor roda
no diretório `cap_08/coding/` via `LocalCommandLineCodeExecutor`. Em produção,
troque por `DockerCommandLineCodeExecutor` para isolar a execução.

## Alternativa Local
```bash
pip install "autogen-ext[ollama]"
ollama pull qwen3.5:7b
```
Ver `local/pesquisa_cientifica_ollama.py` (troca `OpenAIChatCompletionClient`
por `OllamaChatCompletionClient`).

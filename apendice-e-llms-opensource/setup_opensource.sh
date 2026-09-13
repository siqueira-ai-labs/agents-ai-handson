#!/usr/bin/env bash
# Apêndice E — Setup completo para uso de LLMs open-source via Ollama
set -e

echo "=== 1. Instalando Ollama ==="
curl -fsSL https://ollama.com/install.sh | sh

echo "=== 2. Iniciando servidor Ollama ==="
ollama serve &
sleep 3

echo "=== 3. Baixando modelos ==="
ollama pull llama4.1:8b          # trilha fácil — 5.7 GB
ollama pull qwen3.5:7b           # trilha média — 5.4 GB (function calling)
ollama pull mistral:7b           # alternativa leve — 5.1 GB
ollama pull nomic-embed-text     # embeddings locais — 274 MB

echo "=== 4. Instalando dependências Python ==="
source .myenv/bin/activate
pip install langchain-ollama langchain-community

echo "=== Setup concluído! ==="
echo "Teste: ollama run llama4.1:8b 'Olá, tudo bem?'"

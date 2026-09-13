# Módulo 0 — Avisos Críticos Antes de Começar

## Pontos essenciais antes de rodar qualquer projeto

### 1. Custos de API
- Configure limites de gasto no seu provider antes de executar qualquer agente.
- **OpenRouter**: openrouter.ai/settings → configure um Hard Limit (ex: US$ 10/mês).
- Agentes consomem tokens de forma recursiva — uma task simples pode gerar dezenas de chamadas.

### 2. A Ilusão do Determinismo
- Mesmo com `temperature=0`, agentes podem tomar caminhos diferentes.
- Use métricas estatísticas de avaliação (Módulo 12) em vez de testes binários.

### 3. O Inferno de Dependências
- **Sempre** use ambientes virtuais com versões pinadas.
- Este repositório usa `.myenv` na raiz + `requirements-cap_NN.txt` por capítulo.

## Configuração inicial

```bash
# Criar e ativar o ambiente virtual (já criado na raiz como .myenv)
source .myenv/bin/activate

# Copiar variáveis de ambiente
cp .env.example .env
# edite .env com suas chaves
```

## Ferramentas essenciais
- Python 3.12+
- Git
- Docker (necessário para cap_09, cap_14)
- Ollama (opcional — para execução local sem API)

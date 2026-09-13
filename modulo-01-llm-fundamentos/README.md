# Módulo 1 — Como os LLMs Funcionam: Fundamentos Essenciais

> Módulo teórico — sem projeto prático nem exercícios. Se você já conhece
> tokenização, atenção multi-head e janela de contexto, pode pular para cap_01.

## Conceitos cobertos

1. **O Ciclo Fundamental**: Texto → Tokens → Embeddings → Logits → Resposta
2. **Temperatura, Top-p e Top-k**: Controlando a aleatoriedade
   - `temperature=0` → determinístico (ideal para function calling)
   - `top-p=0.9` → nucleus sampling
3. **Janela de Contexto**: GPT-4.1 = 1M tokens; LLaMA 4.1:8b = 128K tokens
4. **Arquiteturas**: Decoder-Only (GPT, LLaMA, Claude) vs Encoder-Decoder (T5)
5. **Mecanismo de Atenção**: Query (Q), Key (K), Value (V) e atenção multi-head

## Referências
- Vaswani et al., "Attention is All You Need" (NeurIPS 2017)
- Karpathy, "Let's build GPT from scratch" (YouTube, 2023)
- Documentação tiktoken — tokenização OpenAI

## Próximo passo

→ **cap_01** (Módulo 2): Fundamentos da IA Agentiva — primeiro projeto prático.

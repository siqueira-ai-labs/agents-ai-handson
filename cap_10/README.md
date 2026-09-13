# cap_10 — Módulo 11: Agentes No-Code/Low-Code

## Objetivo
Construir agentes em plataformas visuais: Wordware (redator), Relevance AI
(SEO Agent) e Langflow (RAG de atendimento).

## Plataformas
| Plataforma | Projeto | Tipo |
|---|---|---|
| Wordware | Agente Redator | No-Code |
| Relevance AI | SEO Agent | No-Code |
| Langflow | Atendimento RAG | Low-Code |

## Artefatos deste capítulo
- `cap_10/langflow_rag_flow.json` — fluxo exportado, pronto para importar no
  Langflow (botão Import). Testado de ponta a ponta via `POST /api/v1/run`
  com pergunta real, respondendo com base no `faq_atendimento.md`. Ver o
  diagrama de referência abaixo para como ele é montado.
- [`langflow_rag_flow_diagrama.html`](langflow_rag_flow_diagrama.html) —
  diagrama de referência do fluxo (mecanismo, tabela de componentes, tweaks
  da API, passo a passo de montagem, e os dois bugs reais encontrados ao
  montar). Abra direto num navegador.
- `cap_10/data/faq_atendimento.md` — base de conhecimento (FAQ) usada pelo
  `Read File` do fluxo.
- `projeto/nocode_integration.py` — invocação do fluxo Langflow via API

## Langflow local
```bash
docker run -d --name langflow_rag -p 7860:7860 \
  -e LANGFLOW_SUPERUSER=admin \
  -e LANGFLOW_SUPERUSER_PASSWORD=admin123456 \
  -e LANGFLOW_AUTO_LOGIN=false \
  langflowai/langflow:latest
# Importe cap_10/langflow_rag_flow.json pelo botão Import do Langflow (≥ 1.0.x)
```
> Sem `LANGFLOW_SUPERUSER`/`LANGFLOW_SUPERUSER_PASSWORD` o container entra em
> loop de crash no boot (`ValueError: Username and password must be set`) —
> versões recentes do Langflow removeram o superusuário default por
> segurança e exigem essas variáveis explicitamente.

## Usando o Langflow (guia rápido para quem nunca abriu)

Langflow é um editor visual: você arrasta **componentes** (caixas prontas —
carregar arquivo, dividir texto, gerar embeddings, chamar um LLM, etc.) para
uma tela (*canvas*) e liga a saída de um na entrada do outro puxando uma
linha entre eles. Cada fluxo montado vira automaticamente um endpoint HTTP
que qualquer código (como `projeto/nocode_integration.py`) pode chamar.

### 1. Login
Depois do `docker run` acima, abra `http://localhost:7860` e entre com o
usuário/senha definidos nas env vars (`admin` / `admin123456` no comando
sugerido). Isso cria uma conta local dentro do próprio container — não é uma
conta na nuvem, os dados ficam só ali.

### 2. Montar o fluxo do zero
Clique em **"New Flow" → "Blank Flow"**. Na barra lateral esquerda há uma
busca de componentes; arraste cada um para o canvas e conecte os pontos
(*handles*) nas bordas das caixas — a cor do handle indica o tipo de dado
aceito, o Langflow bloqueia conexões incompatíveis.

> **Sobre os nomes dos componentes abaixo**: o Langflow não tem uma categoria
> fixa chamada "Vector Store" na barra lateral — cada banco vetorial (Chroma,
> Pinecone, Qdrant, Redis, Weaviate...) é seu próprio componente, e o
> agrupamento visual desses componentes na barra lateral **varia entre
> versões** (pode aparecer sob "Data Source", sob o nome do provedor, ou em
> outro agrupamento). Não confie em navegar por categoria — **use a busca**
> da barra lateral digitando o nome do componente (ex.: "chroma", "prompt
> template"). Os nomes abaixo foram conferidos direto na instância local via
> `GET /api/v1/all` (Langflow 1.11.2); podem variar em outras versões.

A sequência para o RAG de atendimento deste capítulo (ver diagrama de
referência do fluxo):

1. **Read File → Split Text → Embedding Model → Chroma DB**: monta a base de
   conhecimento. **Read File** carrega o(s) documento(s) de FAQ; **Split
   Text** divide em chunks (`chunk_size`/`chunk_overlap`); **Embedding
   Model** gera os vetores; **Chroma DB** (busque por "chroma" — tem duas
   opções, use a que se chama exatamente **"Chroma DB"**, não "Local DB")
   grava tudo em `persist_directory`. Depois de conectar os quatro, clique no
   ícone de *play* (▶) no nó **Chroma DB** para indexar de fato — sem isso
   ele fica vazio, já que ligar os componentes só desenha o cano, não roda a
   indexação sozinho.
   > **Embedding Model**: esse componente só aceita **OpenAI**, **Google
   > Generative AI** ou **Ollama** — Hugging Face não é uma opção, ao
   > contrário do padrão de embeddings locais do resto do livro. Grátis: use
   > Google (chave em [aistudio.google.com/apikey](https://aistudio.google.com/apikey),
   > configurada como variável global `GOOGLE_API_KEY` em Settings → Global
   > Variables). Com Google, mandar 3+ chunks no mesmo request de indexação
   > faz a API devolver menos embeddings do que textos enviados — um
   > `IndexError` dentro do `langchain-chroma`, sem controle de batch size
   > exposto pelo Langflow. Se sua base for pequena, aumente o `Chunk Size`
   > do **Split Text** o bastante pra virar 1-2 chunks só (evita o lote); se
   > for grande, use OpenAI em vez de Google.
2. **Chat Input**: ponto de entrada da conversa. Ligue sua saída tanto ao
   campo `search_query` do **Chroma DB** (ele usa a mensagem como busca,
   parâmetro `number_of_results` controla quantos chunks voltam) quanto
   direto ao **Prompt Template** (como pergunta original).
3. **Parser**: ligue a saída do **Chroma DB** a um **Parser** — não direto ao
   Prompt Template, o Chroma devolve objetos `Data`, não texto puro. No
   template do Parser, use `Text: {text}` — a chave é **`text`**, não
   `content` (esse é o default de fábrica do componente, mas fácil de digitar
   errado; um template com a chave errada não dá nenhum erro, só produz
   contexto vazio silenciosamente — ver "Erros comuns" abaixo).
4. **Prompt Template**: componente de template de texto (não aparece só como
   "Prompt" — o nome completo no menu é **"Prompt Template"**). Declare
   variáveis entre chaves no template (`{context}`, `{question}`, `{idioma}`,
   `{tom_resposta}`) — o Langflow cria automaticamente uma entrada para cada
   uma; ligue `{context}` na saída do **Parser** e `{question}` na saída do
   **Chat Input**. `{idioma}`/`{tom_resposta}` ficam com um valor default
   digitado direto no componente (são o que os `tweaks` da API sobrescrevem
   depois).
5. **Language Model** (categoria "Models & Agents") ou o componente dedicado
   **OpenRouter** (busque por "openrouter" — já vem pronto com `api_key`,
   `model_name`, `temperature`, sem precisar configurar `base_url` na mão):
   qualquer um dos dois funciona, mas o **OpenRouter** é o mais direto,
   consistente com o resto do livro. Se usar o **Language Model** genérico,
   selecione o provedor **OpenAI** e preencha `base_url`/`api_key` do
   OpenRouter manualmente.
6. **Chat Output**: ponto de saída — é o que a API devolve como resposta.

Use o botão **"Playground"** (canto superior direito) para conversar com o
fluxo direto na UI antes de integrar por código — é o jeito mais rápido de
confirmar que o RAG está recuperando contexto de verdade.

### 3. Pegar o `FLOW_ID`, a API key e os IDs de tweak
Com o fluxo salvo, abra a aba **"API"** (ou o botão `</>` no topo). Lá tem:
- A **URL do endpoint**, com o `FLOW_ID` (um UUID) — copie para
  `LANGFLOW_FLOW_ID` no `.env`.
- Um botão para gerar uma **API key** (opcional em uso local, obrigatório se
  desligar `LANGFLOW_AUTO_LOGIN`) — copie para `LANGFLOW_API_KEY`.
- O **payload de exemplo em JSON**, já com os `tweaks` de cada componente
  (`"ChatInput-xxxx"`, `"Prompt-xxxx"` — o sufixo é gerado por instância, o
  seu vai ser diferente) — é daqui que vêm os IDs usados em
  `build_tweaks()` no gabarito do exercício 1.

### 4. Exportar
Botão **"Export"** (menu do fluxo, ícone de download) → salva um `.json` com
a estrutura completa (nós, arestas, posições, config de cada componente).
Salve como `cap_10/langflow_rag_flow.json`.

### Erros comuns
- **Container reinicia sem subir**: falta `LANGFLOW_SUPERUSER`/
  `LANGFLOW_SUPERUSER_PASSWORD` — ver aviso na seção acima.
- **Chroma DB retorna vazio no Playground**: o nó de indexação (Read
  File→Split Text→Embedding Model→Chroma DB) precisa ser executado
  manualmente uma vez (▶ no Chroma DB) — conectar os componentes não roda a
  indexação sozinho.
- **Não acho "Vector Store" na barra lateral**: não existe esse nome — busque
  diretamente por "chroma" (ou pelo provedor que for usar). O agrupamento de
  categoria na barra lateral varia por versão do Langflow.
- **`run_flow()` do Python dá 404**: `LANGFLOW_FLOW_ID` errado ou o fluxo
  ainda não foi salvo — o ID só existe depois do primeiro save.
- **Prompt Template sem as variáveis `{idioma}`/`{tom_resposta}`**: precisam
  estar escritas literalmente entre chaves no template do componente para o
  Langflow criar os campos de entrada correspondentes.
- **Agent responde "não foi fornecido contexto" mesmo com o Chroma DB
  indexado**: confira o template do **Parser** — se estiver `{content}` em
  vez de `{text}`, ele compila sem erro nenhum e só produz texto vazio. Sem
  nenhum log de erro pra apontar o problema; só dá pra achar inspecionando o
  que cada nó realmente produziu (aba **API** → payload de exemplo, ou
  `GET /api/v1/monitor/builds` se estiver chamando por fora).
- **Embedding Model acusa "An embedding model selection is required"**: o
  dropdown de modelo só lista provedores com uma variável global configurada
  em Settings → Global Variables (`GOOGLE_API_KEY`, `OPENAI_API_KEY`...) — o
  campo `API Key` de dentro do próprio node só *sobrescreve* uma variável
  global já existente, não substitui ela.
- **Uma correção feita "por fora" (API, ou por mim) sumiu depois que você
  editou outra coisa na UI**: campos como `Read File.path` ou o texto de
  notas ficam guardados no estado do React da aba aberta no navegador —  se
  a aba já estava aberta antes da correção, o próximo autosave (ou um
  **Export**) sobrescreve o campo de volta ao valor antigo que o navegador
  ainda tinha em memória. Dê **F5** na aba antes de continuar editando depois
  de qualquer correção externa.

## Exercícios
| # | Arquivo | Dificuldade | Tempo |
|---|---|---|---|
| 1 | `exercicios/ex01_multiplas_entradas.py` | Fácil | ~20 min |
| 2 | `exercicios/ex02_webhook_seguro.py` | Médio | ~45 min |
| 3 | `exercicios/ex03_orquestracao_fallback.py` | Difícil | ~2-3h |

## Alternativa Local
```bash
pip install langchain-ollama
ollama pull qwen3.5:7b
```
O Langflow em si já roda local via Docker — para usar um LLM local *dentro*
do fluxo, troque o componente de modelo pela UI. Ver `local/orquestracao_ollama.py`
para o fallback do exercício 3 (Langflow → Ollama, sem nenhuma API paga).

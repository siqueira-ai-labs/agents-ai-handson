"""
cap_01 — Solução do Exercício 2: Trocando o Mecanismo de Memória
Dificuldade: Médio | Tempo estimado: ~45 min
"""
import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, BaseMessage
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.runnables import RunnableLambda
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

load_dotenv()

llm = ChatOpenAI(
    model=os.getenv("OPENROUTER_MODEL", "openai/gpt-oss-20b:free"),
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY"),
)

MAX_MESSAGES = 6   # janela deslizante sujeita a sumarização
FIXED_INTRO = 2    # primeiras N mensagens preservadas verbatim (apresentação do usuário)


class SummarizingMessageHistory(BaseChatMessageHistory):
    """
    Histórico com sumarização automática e contexto de introdução fixo.

    Estratégia:
    - As primeiras FIXED_INTRO mensagens (apresentação do usuário) ficam em
      `_intro` e NUNCA são sumarizadas — garantindo que nomes, área e
      preferências pessoais sobrevivam a qualquer número de turnos.
    - As demais mensagens ficam em `_messages`. Quando ultrapassam MAX_MESSAGES,
      as mais antigas são resumidas pelo próprio LLM em uma SystemMessage.
    - O resumo é armazenado em `_messages[0]` como SystemMessage e extraído
      pelo `inject_summary` para ser mesclado no system prompt principal,
      evitando que modelos ignorem uma segunda SystemMessage no histórico.
    """

    def __init__(self):
        self._intro: list[BaseMessage] = []
        self._messages: list[BaseMessage] = []

    @property
    def messages(self) -> list[BaseMessage]:
        return self._intro + self._messages

    def add_messages(self, messages: list[BaseMessage]) -> None:
        for msg in messages:
            if len(self._intro) < FIXED_INTRO:
                self._intro.append(msg)
            else:
                self._messages.append(msg)
        if len(self._messages) > MAX_MESSAGES:
            self._summarize_old_messages()

    def _summarize_old_messages(self) -> None:
        to_summarize = self._messages[:-MAX_MESSAGES]
        to_keep = self._messages[-MAX_MESSAGES:]

        # Acumula com resumo anterior se já existir em to_summarize[0]
        existing_summary = ""
        if to_summarize and isinstance(to_summarize[0], SystemMessage) and to_summarize[0].content.startswith("[Resumo"):
            existing_summary = to_summarize[0].content
            to_summarize = to_summarize[1:]

        history_text = "\n".join(
            f"{m.__class__.__name__}: {m.content}"
            for m in to_summarize
            if not isinstance(m, SystemMessage)
        )

        prompt = (
            f"Resuma a conversa abaixo em até 3 frases, preservando os fatos essenciais.\n"
            f"{('Resumo anterior: ' + existing_summary) if existing_summary else ''}\n\n"
            f"Conversa:\n{history_text}"
        )
        summary = llm.invoke(prompt)
        self._messages = [SystemMessage(content=f"[Resumo do histórico anterior]\n{summary.content}")] + list(to_keep)

    def clear(self) -> None:
        self._intro = []
        self._messages = []


store: dict[str, SummarizingMessageHistory] = {}


def get_session_history(session_id: str) -> SummarizingMessageHistory:
    if session_id not in store:
        store[session_id] = SummarizingMessageHistory()
    return store[session_id]


# Extrai o resumo do histórico e injeta no system prompt, evitando
# o problema de modelos que ignoram uma segunda SystemMessage no chat.
def inject_summary(input_dict: dict) -> dict:
    history = input_dict.get("history", [])
    summary_text = ""
    clean_history = []
    for msg in history:
        if isinstance(msg, SystemMessage) and msg.content.startswith("[Resumo"):
            summary_text = msg.content
        else:
            clean_history.append(msg)
    return {
        "input": input_dict["input"],
        "history": clean_history,
        "summary": f"\n\n{summary_text}" if summary_text else "",
    }


prompt = ChatPromptTemplate.from_messages([
    ("system", "Você é um assistente prestativo com memória de longo prazo.{summary}"),
    MessagesPlaceholder(variable_name="history"),
    ("human", "{input}"),
])

chain_with_history = RunnableWithMessageHistory(
    RunnableLambda(inject_summary) | prompt | llm,
    get_session_history,
    input_messages_key="input",
    history_messages_key="history",
)


if __name__ == "__main__":
    turns = [
        "Meu nome é Carlos e trabalho com análise de dados.",
        "Uso Python há 5 anos e estou aprendendo sobre agentes IA.",
        "Qual a diferença entre LangChain e LangGraph?",
        "Quando devo usar CrewAI em vez de LangGraph?",
        "Explique o conceito de Tool Calling em LLMs.",
        "Como funciona o ciclo Percepção-Cognição-Ação?",
        "Quais são os modelos mais usados no OpenRouter?",
        "O que é RAG e como se relaciona com agentes?",
        "Como posso limitar o custo de tokens em produção?",
        "Você ainda se lembra do meu nome e da minha área?",
    ]

    session_id = "sessao_teste_001"
    print("Iniciando conversa com memória por sumarização...")
    print("=" * 60)

    for i, turn in enumerate(turns, 1):
        print(f"\n[Turno {i}] Usuário: {turn}")
        response = chain_with_history.invoke(
            {"input": turn},
            config={"configurable": {"session_id": session_id}},
        )
        print(f"Assistente: {response.content}")
        history = get_session_history(session_id)
        print(f"  [Mensagens no histórico: {len(history.messages)}]")

"""
cap_01 — Exercício 2: Trocando o Mecanismo de Memória
Dificuldade: Médio | Tempo estimado: ~45 min

TAREFA:
O RunnableWithMessageHistory com histórico completo consome tokens rapidamente.
Substitua-o por uma versão com sumarização customizada que mantém apenas as
últimas N mensagens + um resumo das anteriores.

Requisitos:
1. Implemente uma função de sumarização que usa o próprio LLM.
2. Configure um limiar (ex: manter apenas as últimas 6 mensagens).
3. Quando ultrapassar o limiar, resuma as mais antigas em uma SystemMessage.
4. Teste com uma conversa de pelo menos 10 turnos.

DICA: ConversationSummaryMemory foi deprecada. Use RunnableWithMessageHistory
com um custom message_history que implementa a lógica de sumarização.
"""
import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage

load_dotenv()

llm = ChatOpenAI(
    model="nvidia/llama-3.1-nemotron-70b-instruct:free",
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY"),
)

MAX_MESSAGES = 6  # manter as últimas N mensagens antes de sumarizar


# TODO: implemente a classe SummarizingMessageHistory
# Ela deve herdar de BaseChatMessageHistory e sobrescrever add_messages()
# com a lógica de sumarização quando len(messages) > MAX_MESSAGES


# TODO: configure o RunnableWithMessageHistory com SummarizingMessageHistory


if __name__ == "__main__":
    print("Iniciando conversa com memória por sumarização...")
    # TODO: execute uma conversa de 10+ turnos e verifique o resumo

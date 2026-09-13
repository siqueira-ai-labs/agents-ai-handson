"""
cap_07 — Exercício 2: Transição para Processo Hierárquico
Dificuldade: Médio | Tempo estimado: ~45 min

TAREFA:
Converta o analista de ações CrewAI de Process.sequential para Process.hierarchical,
adicionando um gerente (manager) que coordena os analistas.

Requisitos:
1. Configure Process.hierarchical com manager_llm definido.
2. O gerente deve distribuir subtarefas entre os analistas especializados.
3. Adicione um analista de risco ao time.
4. Compare a qualidade dos relatórios: sequential vs hierarchical.
5. Meça o custo em tokens de cada abordagem.
"""
import os
from dotenv import load_dotenv
from crewai import Agent, Task, Crew, Process, LLM

load_dotenv()

llm = LLM(
    model="openai/nvidia/llama-3.1-nemotron-70b-instruct:free",
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY"),
)

# TODO: defina os agentes (pesquisador, analista fundamental, analista de risco)
# TODO: configure o manager_llm
# TODO: implemente Crew com Process.hierarchical
# TODO: compare sequential vs hierarchical com a mesma query


if __name__ == "__main__":
    ticker = "PETR4.SA"
    print(f"Análise hierárquica: {ticker}")
    # TODO: execute e compare

"""
cap_11 — Exercício 1: Adicionando Answer Relevancy ao Pipeline RAGAS
Dificuldade: Fácil | Tempo estimado: ~20 min

TAREFA:
Adicione a métrica `answer_relevancy` do RAGAS ao pipeline de avaliação
existente, que já mede `faithfulness`.

Requisitos:
1. Importe AnswerRelevancy do ragas.metrics.
2. Adicione à lista de métricas do evaluate().
3. Exiba os scores individuais por pergunta além da média.
4. Identifique as 2 perguntas com menor answer_relevancy.
"""
import os
from datasets import Dataset
from dotenv import load_dotenv
from ragas import evaluate
from ragas.metrics import faithfulness, answer_relevancy

load_dotenv()

# Dataset de avaliação mínimo.
# Nomes de coluna do ragas >= 0.2 (versões antigas usavam question/answer/
# contexts/ground_truth): user_input, response, retrieved_contexts, reference.
eval_data = {
    "user_input": [
        "O que é RAG?",
        "Qual a diferença entre LangChain e LangGraph?",
        "Quando usar fine-tuning vs RAG?",
    ],
    "response": [
        # TODO: preencha com respostas do seu agente
        "", "", "",
    ],
    "retrieved_contexts": [
        # TODO: preencha com os documentos recuperados pelo agente
        [""], [""], [""],
    ],
    "reference": [
        "RAG combina recuperação de documentos com geração de texto.",
        "LangChain é um framework de orquestração; LangGraph adiciona grafos de estado.",
        "Use RAG quando o conhecimento muda frequentemente; fine-tuning para estilo/formato.",
    ],
}


if __name__ == "__main__":
    dataset = Dataset.from_dict(eval_data)
    # TODO: execute evaluate() com [faithfulness, answer_relevancy]
    # TODO: exiba scores individuais e identifique os piores

"""
cap_11 — Exercício 2: Construindo um Golden Dataset
Dificuldade: Médio | Tempo estimado: ~45 min

TAREFA:
Crie um golden dataset de 20 perguntas+respostas para o domínio do seu agente,
seguindo as melhores práticas de diversidade e cobertura.

Requisitos:
1. Cubra pelo menos 4 categorias: factual, analítica, comparativa, procedural.
2. Inclua pelo menos 3 perguntas "adversariais" (que testam alucinações).
3. Salve em cap_11/golden_dataset.json com schema validado por Pydantic.
4. Calcule a baseline do seu agente no golden dataset e salve em golden_results.json.
5. A cobertura deve ser: 5 fáceis, 10 médias, 5 difíceis.
"""
import json
from pathlib import Path
from pydantic import BaseModel, Field
from typing import Literal

GOLDEN_DATASET_PATH = Path("cap_11/golden_dataset.json")
RESULTS_PATH = Path("cap_11/golden_results.json")


class GoldenExample(BaseModel):
    id: str
    question: str
    ground_truth: str
    category: Literal["factual", "analytical", "comparative", "procedural", "adversarial"]
    difficulty: Literal["easy", "medium", "hard"]
    context_required: list[str] = Field(default_factory=list)


class GoldenDataset(BaseModel):
    version: str = "1.0"
    examples: list[GoldenExample]


# TODO: crie o golden dataset com 20 exemplos e salve em JSON


if __name__ == "__main__":
    # TODO: crie, valide e salve o dataset
    # TODO: execute o agente em todos os exemplos e salve resultados
    pass

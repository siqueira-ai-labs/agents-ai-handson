"""
cap_12 — Alternativa 100% Local: Invest-bot com NeMo Guardrails via Ollama
Mesma arquitetura de projeto/app.py, reaproveitando toda a config em
cap_12/config/ (prompts, actions, fluxo de detecção de prompt injection) —
só o LLM muda.

Nota: o engine "ollama" nativo do NeMo Guardrails 0.9.1.1 resolve para
langchain_community.llms.ollama.Ollama, uma classe de completions antiga
(não chat) — o mesmo problema do engine "openai" com modelos não-GPT que já
resolvemos em projeto/app.py. Mesma solução: construir o ChatOllama
explicitamente e passar via LLMRails(config, llm=...).

Modelo: qwen3.5:7b
"""
import pathlib

from flask import Flask, jsonify, request
from langchain_ollama import ChatOllama
from nemoguardrails import LLMRails, RailsConfig

app = Flask(__name__)

CONFIG_DIR = pathlib.Path(__file__).parent.parent / "config"
config = RailsConfig.from_path(str(CONFIG_DIR))

llm = ChatOllama(model="qwen3.5:7b", base_url="http://localhost:11434", temperature=0)
rails = LLMRails(config, llm=llm)


@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    if not data or "message" not in data:
        return jsonify({"error": "Campo 'message' é obrigatório"}), 400

    user_message = data["message"]
    response = rails.generate(messages=[{"role": "user", "content": user_message}])
    return jsonify({"response": response})


@app.route("/health")
def health():
    return jsonify({"status": "ok"})


if __name__ == "__main__":
    app.run(port=5000, debug=False)

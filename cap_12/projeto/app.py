"""
cap_12 — Invest-bot com NeMo Guardrails
Aplicação Flask com guardrails de input/output para um chatbot financeiro.
"""
import os
import pathlib

from dotenv import load_dotenv
from flask import Flask, jsonify, request
from langchain_openai import ChatOpenAI
from nemoguardrails import LLMRails, RailsConfig

load_dotenv()

app = Flask(__name__)

CONFIG_DIR = pathlib.Path(__file__).parent.parent / "config"
config = RailsConfig.from_path(str(CONFIG_DIR))

# O engine "openai" do NeMo Guardrails só usa ChatOpenAI automaticamente para
# nomes de modelo "gpt-3.5*"/"gpt-4*" (ver nemoguardrails.llm.providers);
# qualquer outro nome — como os modelos do OpenRouter — cai na classe de
# completions legada, que não funciona com endpoints somente-chat. Por isso
# construímos o ChatOpenAI explicitamente e passamos para o LLMRails.
llm = ChatOpenAI(
    model=os.getenv("OPENROUTER_MODEL", "openai/gpt-oss-20b:free"),
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY"),
    temperature=0,
)
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

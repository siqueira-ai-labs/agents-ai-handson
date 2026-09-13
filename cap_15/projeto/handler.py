"""
cap_15 — Ponto de entrada serverless do Cloud Cost Analyst Agent
Bônus: Agentes na Nuvem (AWS, Azure, GCP)

Cada provedor serverless espera uma assinatura de função diferente. A lógica
de negócio fica isolada em `handle_request`, e cada provedor tem um adapter
fino em cima dela — assim o agente em si (agent.py) não conhece qual nuvem
está rodando.

Deploy:
- AWS Lambda: use `lambda_handler` como Handler. Runtime Python 3.12,
  empacote este diretório + dependências em um .zip ou container image.
- Azure Functions (modelo de programação v2): use `azure_handler`,
  decorado com @app.route em um function_app.py que importe este módulo.
- GCP Cloud Functions (2ª geração, HTTP trigger): use `gcp_handler` como
  entry point (`gcloud functions deploy ... --entry-point=gcp_handler`).
"""
import json

from agent import run_agent


def handle_request(query: str) -> dict:
    """Lógica de negócio comum a todos os provedores serverless."""
    if not query:
        return {"statusCode": 400, "body": {"error": "Campo 'query' é obrigatório"}}
    try:
        resposta = run_agent(query)
        return {"statusCode": 200, "body": {"response": resposta}}
    except Exception as e:
        return {"statusCode": 500, "body": {"error": str(e)}}


def lambda_handler(event: dict, context) -> dict:
    """Entry point para AWS Lambda (via API Gateway ou Function URL)."""
    body = json.loads(event.get("body") or "{}") if isinstance(event.get("body"), str) else (event.get("body") or {})
    query = body.get("query") or event.get("query", "")
    result = handle_request(query)
    return {
        "statusCode": result["statusCode"],
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps(result["body"], ensure_ascii=False),
    }


def azure_handler(req):
    """Entry point para Azure Functions (modelo de programação v2, HTTP trigger)."""
    import azure.functions as func

    try:
        body = req.get_json()
    except ValueError:
        body = {}
    query = body.get("query", "")
    result = handle_request(query)
    return func.HttpResponse(
        json.dumps(result["body"], ensure_ascii=False),
        status_code=result["statusCode"],
        mimetype="application/json",
    )


def gcp_handler(request):
    """Entry point para GCP Cloud Functions (2ª geração, HTTP trigger)."""
    body = request.get_json(silent=True) or {}
    query = body.get("query", "")
    result = handle_request(query)
    return json.dumps(result["body"], ensure_ascii=False), result["statusCode"], {"Content-Type": "application/json"}


if __name__ == "__main__":
    # Simula uma invocação local no formato do evento do API Gateway (AWS).
    evento_teste = {"body": json.dumps({"query": "Qual o custo estimado do meu uso de EC2 nos últimos 30 dias?"})}
    print(lambda_handler(evento_teste, context=None))

"""
cap_15 — Ferramentas de consulta de custos por provedor de nuvem
Bônus: Agentes na Nuvem (AWS, Azure, GCP)

Cada provedor expõe custos de um jeito diferente:
- AWS tem uma API direta (Cost Explorer).
- Azure tem uma API direta equivalente (Cost Management Query).
- GCP não tem uma API de consulta direta de custos históricos — o caminho
  padrão é exportar o billing para o BigQuery e consultar lá (Billing Export).

Todas as funções falham de forma graciosa (SDK ausente, credenciais não
configuradas, permissão negada) retornando uma mensagem explicativa em vez
de derrubar o agente — assim o agente ainda responde sobre os provedores
que estão configurados.
"""
import datetime
import os

from langchain_core.tools import tool


@tool
def get_aws_costs(service: str, days: int = 30) -> str:
    """Consulta custos AWS do serviço especificado nos últimos N dias, via Cost Explorer."""
    try:
        import boto3
    except ImportError:
        return "[AWS] boto3 não instalado. pip install boto3."

    try:
        client = boto3.client("ce", region_name=os.getenv("AWS_REGION", "us-east-1"))
        end = datetime.date.today()
        start = end - datetime.timedelta(days=days)
        response = client.get_cost_and_usage(
            TimePeriod={"Start": start.isoformat(), "End": end.isoformat()},
            Granularity="MONTHLY",
            Metrics=["UnblendedCost"],
            Filter={"Dimensions": {"Key": "SERVICE", "Values": [service]}},
        )
        total = sum(
            float(r["Total"]["UnblendedCost"]["Amount"]) for r in response.get("ResultsByTime", [])
        )
        return f"[AWS] {service}: US$ {total:.2f} (últimos {days} dias)"
    except Exception as e:
        return f"[AWS] Não foi possível consultar custos de {service}: {e}"


@tool
def get_azure_costs(service: str, days: int = 30) -> str:
    """Consulta custos Azure do serviço especificado, via Cost Management Query API."""
    try:
        from azure.identity import DefaultAzureCredential
        from azure.mgmt.costmanagement import CostManagementClient
    except ImportError:
        return "[Azure] azure-mgmt-costmanagement não instalado."

    subscription_id = os.getenv("AZURE_SUBSCRIPTION_ID")
    if not subscription_id:
        return "[Azure] AZURE_SUBSCRIPTION_ID não configurado."

    try:
        client = CostManagementClient(credential=DefaultAzureCredential(), subscription_id=subscription_id)
        scope = f"/subscriptions/{subscription_id}"
        end = datetime.date.today()
        start = end - datetime.timedelta(days=days)
        result = client.query.usage(
            scope=scope,
            parameters={
                "type": "ActualCost",
                "timeframe": "Custom",
                "timePeriod": {"from": start.isoformat(), "to": end.isoformat()},
                "dataset": {
                    "granularity": "None",
                    "aggregation": {"totalCost": {"name": "Cost", "function": "Sum"}},
                    "filter": {
                        "dimensions": {"name": "ServiceName", "operator": "In", "values": [service]}
                    },
                },
            },
        )
        rows = result.rows or []
        total = sum(row[0] for row in rows) if rows else 0.0
        return f"[Azure] {service}: US$ {total:.2f} (últimos {days} dias)"
    except Exception as e:
        return f"[Azure] Não foi possível consultar custos de {service}: {e}"


@tool
def get_gcp_costs(service: str, days: int = 30) -> str:
    """Consulta custos GCP do serviço especificado, via a tabela de billing export no BigQuery.

    Requer billing export para o BigQuery já configurado
    (console.cloud.google.com/billing/export) — o GCP não tem uma API REST
    direta de custos históricos como a AWS/Azure."""
    try:
        from google.cloud import bigquery
    except ImportError:
        return "[GCP] google-cloud-bigquery não instalado."

    billing_table = os.getenv("GCP_BILLING_EXPORT_TABLE")
    if not billing_table:
        return "[GCP] GCP_BILLING_EXPORT_TABLE não configurada (ex: 'projeto.dataset.gcp_billing_export_v1_XXXX')."

    try:
        client = bigquery.Client()
        query = f"""
            SELECT SUM(cost) AS total_cost
            FROM `{billing_table}`
            WHERE service.description = @service
              AND usage_start_time >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL @days DAY)
        """
        job_config = bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ScalarQueryParameter("service", "STRING", service),
                bigquery.ScalarQueryParameter("days", "INT64", days),
            ]
        )
        rows = list(client.query(query, job_config=job_config).result())
        total = rows[0].total_cost or 0.0 if rows else 0.0
        return f"[GCP] {service}: US$ {total:.2f} (últimos {days} dias)"
    except Exception as e:
        return f"[GCP] Não foi possível consultar custos de {service}: {e}"


tool_list = [get_aws_costs, get_azure_costs, get_gcp_costs]

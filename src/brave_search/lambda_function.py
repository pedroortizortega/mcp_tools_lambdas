import json
import logging
import os
from aws_lambda_powertools import Logger
from aws_lambda_powertools.utilities import parameters

import httpx
from dotenv import load_dotenv

load_dotenv()

# Cache del secret en Lambda (evita llamar Secrets Manager en cada invocación)
_brave_api_key_cache: str | None = None


def _is_lambda() -> bool:
    """True si el código corre en AWS Lambda."""
    return bool(os.getenv("AWS_LAMBDA_FUNCTION_NAME"))


def _get_secret_from_manager(secret_id: str) -> str:
    """Obtiene el API key desde AWS Secrets Manager. Resultado cacheado por contenedor Lambda."""
    global _brave_api_key_cache
    if _brave_api_key_cache is not None:
        return _brave_api_key_cache
    import boto3

    client = boto3.client("secretsmanager")
    resp = client.get_secret_value(SecretId=secret_id)
    raw = resp.get("SecretString") or ""
    try:
        data = json.loads(raw)
        # Secret en formato JSON, ej: {"API_KEY_BRAVE": "xxx"}
        _brave_api_key_cache = data.get("API_KEY_BRAVE") or data.get("api_key") or raw
    except json.JSONDecodeError:
        _brave_api_key_cache = raw
    return _brave_api_key_cache or ""


def get_brave_api_key() -> str | None:
    """
    Obtiene el API key de Brave: en Lambda desde Secrets Manager, en local desde env.
    En Lambda usa BRAVE_SECRET_ARN o BRAVE_SECRET_NAME (nombre o ARN del secret).
    """
    # if _is_lambda():
        # secret_id = os.getenv("BRAVE_SECRET_ARN") or os.getenv("BRAVE_SECRET_NAME")
        # if not secret_id:
        #     logging.warning("Lambda: falta BRAVE_SECRET_ARN o BRAVE_SECRET_NAME")
        #     return None
        # return _get_secret_from_manager(secret_id) or None
    secret_value = parameters.get_secret("API_KEY_BRAVE")
    return secret_value


class BraveQuery:
    url = "https://api.search.brave.com/res/v1/web/search"
    country = "US"
    search_lang = "en"
    count = 20

    def __init__(self):
        self.api_key = get_brave_api_key()
        if self.api_key:
            logging.info("API Brave Token agregado correctamente")

    @property
    def headers(self) -> dict:
        return {
            "Accept": "application/json",
            "Accept-Encoding": "gzip",
            "x-subscription-token": self.api_key,
        }

    def build_params(self, query: str) -> dict:
        return {
            "q": query,
            "country": self.country,
            "search_lang": self.search_lang,
            "count": self.count,
        }


def lambda_handler(event, context):
# def lambda_handler(query: str) -> dict:
    """
    Main Lambda handler function
    Parameters:
        event: Dict containing the Lambda function event data
        context: Lambda runtime context
    Returns:
        DThe JSON response from Brave Search.
    """
    try:
        # Parse the input event
        logging.info(f"event: {event}")
        logging.info(f"context: {context}")
        query = event.get("query")
        
        # Access environment variables
        bucket_name = os.environ.get('API_KEY_BRAVE')
        bq = BraveQuery()
        logging.info(f"Se tiene el API KEY de Brave: {bq.api_key is not None}")
        if not bq.api_key:
            raise ValueError(
                "Falta API key: en Lambda define BRAVE_SECRET_ARN (o BRAVE_SECRET_NAME); "
                "en local define API_KEY_BRAVE en .env"
            )
        response = httpx.get(bq.url, headers=bq.headers, params=bq.build_params(query))
        if not response.is_success:
            raise Exception(f"Brave API error {response.status_code}: {response.text}")
        return {
            "statusCode": 200,
            "message": "Receipt processed successfully",
            "brave_response": response.json()
        }
    except Exception as e:
        logging.error(f"El error es: {e}")
        return {
            "statusCode": 501,
            "message": "Erro al correr la función lambda",
            "error": str(e)
        }
        

if __name__ == "__main__":
    q = "Busca información de la empresa coco-cola de méxico"
    print(lambda_handler(q))
    
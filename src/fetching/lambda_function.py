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





def get_brave_api_key() -> str | None:
    """
    Obtiene el API key de Brave: en Lambda desde Secrets Manager, en local desde env.
    En Lambda usa BRAVE_SECRET_ARN o BRAVE_SECRET_NAME (nombre o ARN del secret).
    """
    secret_value = parameters.get_secret("API_KEY_BRAVE")
    return secret_value



import requests

def lambda_handler(event, context):
    url = event.get("url")
    query = event.get("query")
    
    downloaded = requests.get(url)
    if downloaded:
        # Extrae solo el contenido útil
        # text = trafilatura.extract(downloaded)
        text = downloaded.text
        
        return {
            "status": "success",
            "content": f"El usuario buscó '{query}'. La página dice: {text[:8000]}"
        }
    return {"status": "error", "content": "Error al descargar la página."}

if __name__ == "__main__":
    evento = {
        "url": "https://x.com/CocaColaMx/status/1662122263712264192?lang=es",
        "query": "Busca información de la empresa coco-cola de méxico"
    }
    print(lambda_handler(evento, {}))
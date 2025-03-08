import os
import asyncio
from typing import List, Dict, Any

import groq
from groq.types.chat import ChatCompletion

from src.utils.logger import get_logger
from src.utils.config import get_config

logger = get_logger(__name__)

async def generate_response(messages: List[Dict[str, str]]) -> str:
    config = get_config()
    api_key = os.getenv("GROQ_API_KEY")

    if not api_key:
        raise ValueError("GROQ_API_KEY não encontrada nas variáveis de ambiente")

    client = groq.AsyncClient(api_key=api_key)

    try:
        response = await client.chat.completions.create(
            model=config.ai_model,
            messages=messages,
            temperature=config.temperature,
            max_tokens=config.max_tokens,
            timeout=config.response_timeout
        )

        return response.choices[0].message.content
    except Exception as e:
        logger.error(f"Erro ao gerar resposta com Groq: {e}")
        raise
    finally:
        await client.close()

async def get_available_models() -> List[str]:
    api_key = os.getenv("GROQ_API_KEY")

    if not api_key:
        raise ValueError("GROQ_API_KEY não encontrada nas variáveis de ambiente")

    client = groq.AsyncClient(api_key=api_key)

    try:
        models = await client.models.list()
        return [model.id for model in models.data]
    except Exception as e:
        logger.error(f"Erro ao obter modelos disponíveis da Groq: {e}")
        return []
    finally:
        await client.close()

import os
import asyncio
from typing import List, Dict, Any

from openai import AsyncOpenAI
from openai.types.chat import ChatCompletion

from src.utils.logger import get_logger
from src.utils.config import get_config

logger = get_logger(__name__)

async def generate_response(messages: List[Dict[str, str]]) -> str:
    config = get_config()
    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:
        raise ValueError("OPENAI_API_KEY não encontrada nas variáveis de ambiente")

    client = AsyncOpenAI(api_key=api_key)

    try:
        response = await client.chat.completions.create(
            model=config.openai_model,
            messages=messages,
            temperature=config.temperature,
            max_tokens=config.max_tokens,
            timeout=config.response_timeout
        )

        return response.choices[0].message.content
    except Exception as e:
        logger.error(f"Erro ao gerar resposta com OpenAI: {e}")
        raise

async def get_available_models() -> List[str]:
    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:
        raise ValueError("OPENAI_API_KEY não encontrada nas variáveis de ambiente")

    client = AsyncOpenAI(api_key=api_key)

    try:
        models = await client.models.list()
        return [model.id for model in models.data]
    except Exception as e:
        logger.error(f"Erro ao obter modelos disponíveis da OpenAI: {e}")
        return []

import os
import asyncio
from dotenv import load_dotenv

from src.bot.client import create_bot
from src.utils.logger import setup_logger
from src.utils.config import load_config

logger = setup_logger()

async def main():
    try:
        load_dotenv()

        required_env_vars = ["DISCORD_TOKEN", "GROQ_API_KEY", "OPENAI_API_KEY"]
        missing_vars = [var for var in required_env_vars if not os.getenv(var)]

        if missing_vars:
            logger.error(f"Variáveis de ambiente ausentes: {', '.join(missing_vars)}")
            logger.error("Por favor, configure o arquivo .env com as variáveis necessárias.")
            return

        config = load_config()

        bot = create_bot(config)

        token = os.getenv("DISCORD_TOKEN")
        logger.info("Iniciando o bot...")
        await bot.start(token)

    except Exception as e:
        logger.exception(f"Erro ao iniciar o bot: {e}")
        raise

if __name__ == "__main__":
    try:
        logger.info("Iniciando aplicação...")
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Aplicação encerrada pelo usuário.")
    except Exception as e:
        logger.exception(f"Erro não tratado: {e}")

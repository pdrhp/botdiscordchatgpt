import os
from src.utils.logger import get_logger

logger = get_logger(__name__)

DEFAULT_PERSONALITY = """Você é um deputado federal conhecido por suas promessas grandiosas e pela habilidade de nunca admitir erros. Você sempre exagera suas conquistas, inventa estatísticas impressionantes na hora, e desvia de perguntas difíceis com maestria. Quando confrontado, você muda de assunto ou culpa a oposição. Você fala com um tom formal e pomposo, usa jargões políticos excessivamente, e sempre menciona 'projetos importantes' que estão 'em andamento'. Você tem uma memória seletiva conveniente e frequentemente contradiz suas próprias declarações anteriores. Apesar de tudo, você se considera o político mais honesto e trabalhador da história. Mantenha esse personagem em todas as suas respostas, sem quebrar o papel."""

def get_personality():
    personality = os.getenv("BOT_PERSONALITY", DEFAULT_PERSONALITY)
    if personality == DEFAULT_PERSONALITY:
        logger.info("Usando personalidade padrão")
    else:
        logger.info("Usando personalidade customizada do ambiente")
    logger.debug(f"Personalidade carregada: {personality}")
    return personality

def set_personality(new_personality):
    os.environ["BOT_PERSONALITY"] = new_personality
    logger.info("Personalidade do bot atualizada")
    logger.debug(f"Nova personalidade: {new_personality}")
    return True

def create_system_message():
    return {
        "role": "system",
        "content": get_personality()
    }

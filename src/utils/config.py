import os
import json
import yaml
from pathlib import Path
from typing import Dict, Any, Optional

from pydantic import BaseModel, Field
from src.utils.logger import get_logger

logger = get_logger(__name__)

CONFIG_DIR = Path("config")
DEFAULT_CONFIG_FILE = CONFIG_DIR / "config.yaml"

class BotConfig(BaseModel):

    command_prefix: str = Field(default="!", description="Prefixo para comandos tradicionais")
    description: str = Field(default="Bot do Discord integrado com modelos de IA", description="Descrição do bot")

    ai_model: str = Field(default="llama3", description="Modelo de IA padrão para o Groq")
    openai_model: str = Field(default="gpt-3.5-turbo", description="Modelo de IA padrão para o OpenAI (fallback)")
    max_context_messages: int = Field(default=50, description="Número máximo de mensagens para manter no contexto")

    log_level: str = Field(default="INFO", description="Nível de logging")

    response_timeout: int = Field(default=30, description="Tempo máximo (em segundos) para aguardar resposta da IA")
    max_tokens: int = Field(default=1024, description="Número máximo de tokens para geração de resposta")
    temperature: float = Field(default=0.7, description="Temperatura para geração de texto (0.0-1.0)")

_config: Optional[BotConfig] = None

def load_config(config_path: Optional[str] = None) -> BotConfig:

    global _config

    if _config is not None:
        return _config

    config_file = Path(config_path) if config_path else DEFAULT_CONFIG_FILE

    CONFIG_DIR.mkdir(exist_ok=True)

    if not config_file.exists():
        logger.warning(f"Arquivo de configuração {config_file} não encontrado. Criando configuração padrão.")
        _config = BotConfig()

        save_config(_config, config_file)
        return _config

    try:
        if config_file.suffix in ['.yaml', '.yml']:
            with open(config_file, 'r', encoding='utf-8') as f:
                config_data = yaml.safe_load(f)
        elif config_file.suffix == '.json':
            with open(config_file, 'r', encoding='utf-8') as f:
                config_data = json.load(f)
        else:
            logger.error(f"Formato de arquivo de configuração não suportado: {config_file.suffix}")
            logger.info("Usando configuração padrão.")
            _config = BotConfig()
            return _config

        _config = BotConfig(**config_data)
        logger.info(f"Configuração carregada de {config_file}")
        return _config

    except Exception as e:
        logger.error(f"Erro ao carregar configuração: {e}")
        logger.info("Usando configuração padrão.")
        _config = BotConfig()
        return _config

def save_config(config: BotConfig, config_path: Optional[str] = None) -> bool:

    config_file = Path(config_path) if config_path else DEFAULT_CONFIG_FILE

    config_file.parent.mkdir(exist_ok=True)

    try:
        config_dict = config.model_dump()

        if config_file.suffix in ['.yaml', '.yml']:
            with open(config_file, 'w', encoding='utf-8') as f:
                yaml.dump(config_dict, f, default_flow_style=False, sort_keys=False)
        elif config_file.suffix == '.json':
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(config_dict, f, indent=2)
        else:
            yaml_file = config_file.with_suffix('.yaml')
            with open(yaml_file, 'w', encoding='utf-8') as f:
                yaml.dump(config_dict, f, default_flow_style=False, sort_keys=False)
            logger.info(f"Configuração salva como {yaml_file} (formato padrão)")
            return True

        logger.info(f"Configuração salva em {config_file}")
        return True

    except Exception as e:
        logger.error(f"Erro ao salvar configuração: {e}")
        return False

def get_config() -> BotConfig:
    global _config

    if _config is None:
        _config = load_config()

    return _config

def update_config(updates: Dict[str, Any]) -> BotConfig:
    config = get_config()

    valid_updates = {k: v for k, v in updates.items() if hasattr(config, k)}

    if not valid_updates:
        logger.warning("Nenhum campo válido para atualização")
        return config

    for key, value in valid_updates.items():
        setattr(config, key, value)

    save_config(config)

    logger.info(f"Configuração atualizada: {', '.join(valid_updates.keys())}")
    return config

from pydantic import BaseModel
import os
from dotenv import load_dotenv
from typing import Optional

# Загрузка переменных окружения из файла .env
load_dotenv()

class GigaChatConfig(BaseModel):
    """Конфигурация для GigaChat API"""
    client_id: str = os.getenv("GIGACHAT_CLIENT_ID", "")
    client_secret: str = os.getenv("GIGACHAT_CLIENT_SECRET", "")
    auth_key: str = os.getenv("GIGACHAT_AUTH_KEY", "")
    scope: str = os.getenv("GIGACHAT_SCOPE", "GIGACHAT_API_PERS")
    api_base_url: str = "https://gigachat.devices.sberbank.ru/api/v1"
    auth_url: str = "https://ngw.devices.sberbank.ru:9443/api/v2/oauth"
    model: str = os.getenv("GIGACHAT_MODEL", "GigaChat")
    temperature: float = float(os.getenv("GIGACHAT_TEMPERATURE", "0.7"))
    max_tokens: int = int(os.getenv("GIGACHAT_MAX_TOKENS", "1500"))

class AssistantConfig(BaseModel):
    """Конфигурация для ассистента"""
    model: str = os.getenv("ASSISTANT_MODEL", "GigaChat")
    temperature: float = float(os.getenv("ASSISTANT_TEMPERATURE", "0.5"))
    max_tokens: int = int(os.getenv("ASSISTANT_MAX_TOKENS", "1000"))
    platform_info: str = os.getenv("PLATFORM_INFO_PATH", "documentation.md")

class APIConfig(BaseModel):
    """Основная конфигурация API"""
    title: str = "Сервис улучшения текста и ассистент платформы"
    description: str = "API для преобразования обычного текста в красочное, грамотное и продающее описание, а также ассистент для помощи пользователям платформы"
    version: str = "1.0.0"
    host: str = os.getenv("HOST", "0.0.0.0")
    port: int = int(os.getenv("PORT", 8000))
    debug: bool = os.getenv("DEBUG", "False").lower() in ('true', '1', 't')

# Создание экземпляров конфигурации
gigachat_config = GigaChatConfig()
assistant_config = AssistantConfig()
api_config = APIConfig() 
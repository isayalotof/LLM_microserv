import httpx
from typing import Dict, Any, Optional, List
import json
import logging

from app.config import gigachat_config
from app.utils.auth import token_manager

# Настройка логирования
logger = logging.getLogger("gigachat")

class GigaChatService:
    """Сервис для взаимодействия с GigaChat API"""
    
    async def enhance_text(self, text: str, style: Optional[str] = None, length: Optional[str] = None) -> str:
        """
        Улучшает текст с помощью GigaChat API
        
        Args:
            text: Исходный текст для улучшения
            style: Стиль текста (продающий, информационный, эмоциональный и т.д.)
            length: Желаемая длина результата (короткий, средний, длинный)
            
        Returns:
            Улучшенный текст
        """
        # Формируем промпт в зависимости от переданных параметров
        prompt = self._build_prompt(text, style, length)
        
        # Получаем ответ от API
        response = await self._send_chat_request(prompt)
        
        # Извлекаем и возвращаем улучшенный текст
        return response
    
    def _build_prompt(self, text: str, style: Optional[str] = None, length: Optional[str] = None) -> str:
        """
        Формирует промпт для GigaChat API на основе параметров
        """
        prompt = f"Преобразуй следующий текст в красочное, грамотное и продающее описание:"
        
        if style:
            prompt += f"\nСтиль описания: {style}."
            
        if length:
            prompt += f"\nЖелаемая длина: {length}."
            
        prompt += f"\n\nИсходный текст: \"{text}\"\n\nУлучшенный текст:"
        
        return prompt
    
    async def _send_chat_request(self, prompt: str) -> str:
        """
        Отправляет запрос к GigaChat API и возвращает ответ
        """
        max_attempts = 2  # Максимальное количество попыток с обновлением токена
        attempt = 0
        
        while attempt < max_attempts:
            attempt += 1
            try:
                # Получаем токен авторизации
                auth_token = await token_manager.get_token()
                logger.info(f"Отправка запроса к GigaChat API (попытка {attempt}/{max_attempts})")
                
                # Формируем запрос
                request_data = {
                    "model": gigachat_config.model,
                    "messages": [
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    "temperature": gigachat_config.temperature,
                    "max_tokens": gigachat_config.max_tokens
                }
                
                # Отправляем запрос к API
                async with httpx.AsyncClient(verify=False, timeout=60.0) as client:
                    response = await client.post(
                        f"{gigachat_config.api_base_url}/chat/completions",
                        headers={
                            "Authorization": f"Bearer {auth_token}",
                            "Content-Type": "application/json",
                            "Accept": "application/json"
                        },
                        json=request_data
                    )
                    
                    response.raise_for_status()
                    response_data = response.json()
                    
                    # Извлекаем текст ответа
                    if response_data.get("choices") and len(response_data["choices"]) > 0:
                        message = response_data["choices"][0].get("message", {})
                        return message.get("content", "").strip()
                        
                    return "Не удалось получить ответ от ассистента."
                    
            except httpx.HTTPStatusError as e:
                if e.response.status_code == 401 and attempt < max_attempts:
                    # Если токен истек, принудительно обновляем его и повторяем запрос
                    logger.warning("Получена ошибка авторизации 401. Принудительное обновление токена...")
                    await token_manager.refresh_token()
                    continue
                else:
                    logger.error(f"HTTP ошибка при запросе к API: {e.response.status_code} {e.response.text}")
                    raise Exception(f"Ошибка взаимодействия с GigaChat API: {str(e)}")
            except Exception as e:
                logger.error(f"Неожиданная ошибка при запросе к API: {str(e)}")
                raise Exception(f"Ошибка взаимодействия с GigaChat API: {str(e)}")
        
        # Если мы дошли до этой точки, значит все попытки исчерпаны
        raise Exception("Превышено максимальное количество попыток запроса к GigaChat API")

# Глобальный экземпляр сервиса
gigachat_service = GigaChatService() 
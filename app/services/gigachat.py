import httpx
from typing import Dict, Any, Optional, List
import json

from app.config import gigachat_config
from app.utils.auth import token_manager

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
        # Получаем токен авторизации
        auth_token = await token_manager.get_token()
        
        # Формируем запрос
        request_data = {
            "model": "GigaChat",
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": 0.7,
            "max_tokens": 1500
        }
        
        try:
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
                    
                return "Не удалось получить ответ от нейросети."
                
        except Exception as e:
            raise Exception(f"Ошибка взаимодействия с GigaChat API: {str(e)}")

# Глобальный экземпляр сервиса
gigachat_service = GigaChatService() 
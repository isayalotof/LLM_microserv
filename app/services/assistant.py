import httpx
from typing import Dict, Any, Optional, List
import json
import os
import traceback

from app.config import gigachat_config, assistant_config
from app.utils.auth import token_manager

class AssistantService:
    """Сервис для работы с ассистентом на базе GigaChat API"""
    
    async def get_answer(self, 
                        query: str, 
                        context: Optional[str] = None, 
                        user_id: Optional[str] = None) -> str:
        """
        Получает ответ от ассистента на вопрос пользователя
        
        Args:
            query: Вопрос пользователя
            context: Контекст взаимодействия (откуда задан вопрос, текущая страница)
            user_id: Идентификатор пользователя для персонализации
            
        Returns:
            Ответ ассистента
        """
        try:
            # Формируем промпт в зависимости от переданных параметров
            messages = self._build_prompt(query, context)
            
            # Получаем ответ от API
            response = await self._send_chat_request(messages)
            
            # Возвращаем ответ
            return response
        except Exception as e:
            traceback.print_exc()
            raise Exception(f"Ошибка обработки запроса к ассистенту: {str(e)}")
    
    def _build_prompt(self, query: str, context: Optional[str] = None) -> List[Dict[str, str]]:
        """
        Формирует промпт для GigaChat API на основе параметров
        """
        system_prompt = """Ты - полезный ассистент для веб-интерфейса бизнес-платформы.
Твоя главная задача - максимально просто объяснять пользователям, как выполнить конкретные действия ТОЛЬКО В РАМКАХ НАШЕГО ВЕБ-ИНТЕРФЕЙСА.

О НАШЕЙ ПЛАТФОРМЕ:
Наша платформа помогает бизнесу найти клиентов. Каждый предприниматель может зарегистрировать свой бизнес в нашей системе, чтобы присоединиться к платформе и начать получать клиентов. Основная ценность - удобный поиск новых клиентов и продвижение услуг бизнеса.

СТРОГИЕ ПРАВИЛА:
1. ОТВЕЧАЙ ТОЛЬКО О ФУНКЦИЯХ НАШЕГО ВЕБ-ИНТЕРФЕЙСА. НИКОГДА не давай советы о внешних сервисах (например, ФНС, госуслуги и т.д.).
2. Если вопрос не относится к функциям нашего сайта или ты не знаешь ответа, ВСЕГДА отвечай: "По этому вопросу лучше обратиться к нашему менеджеру в Telegram: @isayalotof"
3. Всегда описывай, где именно находится элемент интерфейса (в каком углу, какого цвета)
4. Давай только конкретные пошаговые инструкции по принципу "нажмите сюда → перейдите туда → увидите это"
5. Давай короткие ответы - не более 5-7 шагов

Примеры хороших ответов:
- "Чтобы зарегистрировать свой бизнес: 1. Нажмите на синюю кнопку 'Регистрация бизнеса' в правом верхнем углу главной страницы. 2. Заполните форму с информацией о вашем бизнесе. 3. Загрузите логотип компании. 4. Нажмите зеленую кнопку 'Создать'."
- "Для поиска клиентов: 1. Нажмите на вкладку 'Клиенты' в верхнем меню. 2. Используйте фильтры слева для уточнения параметров поиска. 3. Нажмите синюю кнопку 'Найти'."
- "По этому вопросу лучше обратиться к нашему менеджеру в Telegram: @isayalotof"

Основные модули интерфейса:
1. Бизнес-модуль (для обычных пользователей):
   - Раздел "Компании" - в верхнем меню, значок здания
   - Раздел "Услуги" - в верхнем меню, значок календаря
   - Раздел "Аналитика" - в верхнем меню, значок графика
   - Раздел "Настройки" - в правом верхнем углу, значок шестеренки

2. Административная панель (для администраторов):
   - Раздел "Управление" - в левом меню, первый пункт
   - Раздел "Пользователи" - в левом меню, значок людей
   - Раздел "Логи" - в левом меню, значок списка
   - Раздел "Настройки системы" - в левом меню, значок шестеренки
"""
        
        # Если доступен файл с информацией о платформе, загружаем его содержимое
        platform_info_path = assistant_config.platform_info
        if os.path.exists(platform_info_path):
            try:
                with open(platform_info_path, 'r', encoding='utf-8') as file:
                    platform_info = file.read()
                    system_prompt += f"\n\nДополнительная информация о веб-интерфейсе:\n{platform_info[:4000]}"
            except Exception as e:
                print(f"Ошибка при чтении файла с информацией о платформе: {str(e)}")
        
        # Если контекст задан, добавляем его в промпт
        if context:
            system_prompt += f"\nТекущая страница пользователя: {context}"
        
        # Формируем сообщения для API
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": query}
        ]
        
        return messages
    
    async def _send_chat_request(self, messages: List[Dict[str, str]]) -> str:
        """
        Отправляет запрос к GigaChat API и возвращает ответ
        """
        try:
            # Получаем токен авторизации
            auth_token = await token_manager.get_token()
            
            # Формируем запрос
            request_data = {
                "model": assistant_config.model,
                "messages": messages,
                "temperature": assistant_config.temperature,
                "max_tokens": assistant_config.max_tokens
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
                    content = message.get("content", "").strip()
                    
                    # Проверяем, не содержит ли ответ информации о внешних сервисах
                    unwanted_terms = ["фнс", "налоговой", "госуслуги", "мфц", "документац", "github"]
                    if any(term in content.lower() for term in unwanted_terms):
                        return "По этому вопросу лучше обратиться к нашему менеджеру в Telegram: @isayalotof"
                    
                    return content
                    
                return "Не удалось получить ответ от ассистента."
                
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 401:
                # Если токен истек, пробуем обновить его и повторить запрос
                await token_manager.refresh_token()
                return await self._send_chat_request(messages)
            else:
                raise Exception(f"Ошибка взаимодействия с GigaChat API: {str(e)}")
        except Exception as e:
            raise Exception(f"Ошибка взаимодействия с GigaChat API: {str(e)}")
    
    async def search_platform_info(self, query: str) -> Dict[str, Any]:
        """
        Поиск информации о платформе по запросу пользователя
        
        Args:
            query: Поисковый запрос
            
        Returns:
            Словарь с результатами поиска
        """
        # Здесь можно реализовать поиск по документации или базе знаний
        # Пока возвращаем заглушку
        return {
            "query": query,
            "results": [],
            "total": 0
        }

# Глобальный экземпляр сервиса
assistant_service = AssistantService() 
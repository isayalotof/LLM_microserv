import httpx
import base64
from typing import Optional, Dict, Any
import time
from app.config import gigachat_config
import certifi
import ssl
import uuid
import logging

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("auth")

class TokenManager:
    """Класс для управления токенами аутентификации GigaChat API"""
    
    def __init__(self):
        self.access_token: Optional[str] = None
        self.token_expires_at: Optional[float] = None
        self.config = gigachat_config
        # Отключаем проверку SSL для тестовых сертификатов
        self.verify_ssl = False
        self.token_refresh_attempts = 0
        self.max_refresh_attempts = 3
        logger.info("Инициализация TokenManager")
        
    async def get_token(self) -> str:
        """Получение токена авторизации, с обновлением при необходимости"""
        if not self.access_token or time.time() >= self.token_expires_at:
            logger.info("Токен отсутствует или истек, получаем новый")
            await self.refresh_token()
        return self.access_token
    
    async def refresh_token(self) -> str:
        """Обновление токена доступа через API GigaChat"""
        self.token_refresh_attempts += 1
        try:
            logger.info(f"Попытка обновления токена #{self.token_refresh_attempts} (планировщик или API запрос)")
            headers = {
                "Content-Type": "application/x-www-form-urlencoded",
                "Accept": "application/json",
                "RqUID": str(uuid.uuid4())
            }

            if self.config.auth_key:
                # Используем Authorization Key
                auth_string = f"{self.config.client_id}:{self.config.client_secret}"
                auth_bytes = auth_string.encode('ascii')
                base64_auth = base64.b64encode(auth_bytes).decode('ascii')
                headers["Authorization"] = f"Basic {base64_auth}"
                data = {
                    "scope": self.config.scope,
                    "grant_type": "client_credentials"
                }
            else:
                # Используем Client ID и Client Secret
                data = {
                    "scope": self.config.scope,
                    "grant_type": "client_credentials",
                    "client_id": self.config.client_id,
                    "client_secret": self.config.client_secret
                }

            # Создаем клиент с отключенной проверкой SSL
            async with httpx.AsyncClient(verify=self.verify_ssl) as client:
                logger.info(f"Отправка запроса на получение токена к {self.config.auth_url}")
                response = await client.post(
                    self.config.auth_url,
                    headers=headers,
                    data=data,
                    timeout=30.0
                )
                response.raise_for_status()
                token_data = response.json()
                
                self.access_token = token_data["access_token"]
                
                # Проверяем наличие поля expires_in в ответе
                if "expires_in" in token_data:
                    self.token_expires_at = time.time() + token_data["expires_in"]
                    expiry_seconds = token_data["expires_in"]
                elif "expires_at" in token_data:
                    # Если есть поле expires_at, используем его
                    self.token_expires_at = token_data["expires_at"]
                    expiry_seconds = self.token_expires_at - time.time()
                else:
                    # Если нет ни одного поля, устанавливаем время истечения по умолчанию (30 минут)
                    self.token_expires_at = 1800
                    expiry_seconds = 1800
                
                logger.info(f"Получен новый токен, истекает через {int(expiry_seconds)} секунд (осталось {int(expiry_seconds/60)} минут)")
                self.token_refresh_attempts = 0  # Сбрасываем счетчик попыток после успеха
                return self.access_token

        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP ошибка при получении токена: {e.response.status_code} {e.response.text}")
            if e.response.status_code == 429 and self.token_refresh_attempts < self.max_refresh_attempts:
                wait_time = 5 * self.token_refresh_attempts
                logger.warning(f"Слишком много запросов. Ожидание {wait_time} секунд перед следующей попыткой")
                time.sleep(wait_time)
                return await self.refresh_token()
            raise
        except Exception as e:
            logger.error(f"Неожиданная ошибка при получении токена: {str(e)}")
            if self.token_refresh_attempts < self.max_refresh_attempts:
                wait_time = 5 * self.token_refresh_attempts
                logger.warning(f"Ожидание {wait_time} секунд перед следующей попыткой")
                time.sleep(wait_time)
                return await self.refresh_token()
            raise

# Глобальный экземпляр менеджера токенов
token_manager = TokenManager() 
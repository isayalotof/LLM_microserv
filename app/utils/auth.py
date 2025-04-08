import httpx
import base64
from typing import Optional, Dict, Any
import time
from app.config import gigachat_config
import certifi
import ssl
import uuid

class TokenManager:
    """Класс для управления токенами аутентификации GigaChat API"""
    
    def __init__(self):
        self.access_token: Optional[str] = None
        self.token_expires_at: Optional[float] = None
        self.config = gigachat_config
        # Отключаем проверку SSL для тестовых сертификатов
        self.verify_ssl = False
        
    async def get_token(self) -> str:
        """Получение токена авторизации, с обновлением при необходимости"""
        if not self.access_token or time.time() >= self.token_expires_at:
            await self.refresh_token()
        return self.access_token
    
    async def refresh_token(self) -> str:
        """Обновление токена доступа через API GigaChat"""
        try:
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
                response = await client.post(
                    "https://ngw.devices.sberbank.ru:9443/api/v2/oauth",
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
                elif "expires_at" in token_data:
                    # Если есть поле expires_at, используем его
                    self.token_expires_at = token_data["expires_at"]
                else:
                    # Если нет ни одного поля, устанавливаем время истечения по умолчанию (30 минут)
                    self.token_expires_at = time.time() + 1800
                
                return self.access_token

        except Exception as e:
            print(f"Ошибка при получении токена: {str(e)}")
            raise

# Глобальный экземпляр менеджера токенов
token_manager = TokenManager() 
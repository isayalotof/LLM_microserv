from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
import warnings
import ssl
import traceback

from app.config import api_config
from app.routers import text_enhancer, assistant

# Отключаем предупреждения SSL
warnings.filterwarnings("ignore", category=DeprecationWarning)
ssl._create_default_https_context = ssl._create_unverified_context

# Создаем экземпляр FastAPI
app = FastAPI(
    title=api_config.title,
    description=api_config.description,
    version=api_config.version,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Добавляем middleware для CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Регистрируем роутеры
app.include_router(text_enhancer.router)
app.include_router(assistant.router)

# Обработчик исключений
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Глобальный обработчик исключений"""
    error_message = f"Внутренняя ошибка сервера: {str(exc)}"
    traceback.print_exc()
    return JSONResponse(
        status_code=500,
        content={"error": error_message}
    )

# Корневой эндпоинт API
@app.get("/")
async def root():
    """Корневой эндпоинт с информацией о сервисе"""
    return {
        "name": api_config.title,
        "version": api_config.version,
        "description": api_config.description,
        "documentation": "/docs"
    }

# Эндпоинт проверки работоспособности
@app.get("/health")
async def health_check():
    """Эндпоинт проверки работоспособности API"""
    return {"status": "ok"}

# Запуск приложения
if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host=api_config.host,
        port=api_config.port,
        reload=api_config.debug
    ) 
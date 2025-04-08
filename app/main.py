from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
import warnings
import ssl
import traceback
import time
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
import asyncio

from app.config import api_config
from app.routers import text_enhancer, assistant
from app.utils.auth import token_manager

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

# Создаем планировщик
scheduler = AsyncIOScheduler()

# Функция для обновления токена
async def refresh_token_job():
    """Задача для планировщика по обновлению токена"""
    try:
        await token_manager.refresh_token()
        print(f"[Планировщик] Токен успешно обновлен в {time.strftime('%H:%M:%S')}")
    except Exception as e:
        print(f"[Планировщик] Ошибка обновления токена: {str(e)}")

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
        "service": api_config.title,
        "version": api_config.version,
        "description": api_config.description,
        "status": "running"
    }

# Эндпоинт проверки работоспособности
@app.get("/health")
async def health_check():
    """Проверка работоспособности сервиса"""
    token_status = "active" if token_manager.access_token and token_manager.token_expires_at > time.time() else "expired"
    return {
        "status": "ok",
        "token_status": token_status,
        "expires_in": int(token_manager.token_expires_at - time.time()) if token_manager.token_expires_at else None,
        "scheduler": "running" if scheduler.running else "stopped"
    }

@app.on_event("startup")
async def startup_event():
    """Действия при запуске приложения"""
    # Добавляем задачу обновления токена каждую минуту
    scheduler.add_job(
        refresh_token_job,
        IntervalTrigger(minutes=1),
        id="refresh_token_job",
        replace_existing=True
    )
    # Запускаем планировщик
    scheduler.start()
    print("Запущен планировщик обновления токена (каждую минуту)")
    
    # Получаем первоначальный токен
    await token_manager.refresh_token()

@app.on_event("shutdown")
async def shutdown_event():
    """Действия при остановке приложения"""
    # Останавливаем планировщик
    if scheduler.running:
        scheduler.shutdown()
        print("Планировщик обновления токена остановлен")

# Запуск приложения
if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    ) 
from fastapi import APIRouter, Query, HTTPException, Depends, Body
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
import traceback

from app.services.assistant import assistant_service

# Создаем роутер
router = APIRouter(prefix="/api/assistant", tags=["assistant"])

# Модели данных
class AssistantRequest(BaseModel):
    """Модель запроса к ассистенту"""
    query: str = Field(..., description="Вопрос пользователя")
    context: Optional[str] = Field(None, description="Контекст взаимодействия (страница, раздел сайта)")
    user_id: Optional[str] = Field(None, description="Идентификатор пользователя для персонализации")

class AssistantResponse(BaseModel):
    """Модель ответа ассистента"""
    answer: str = Field(..., description="Ответ ассистента")
    user_query: str = Field(..., description="Исходный вопрос пользователя")
    context: Optional[str] = Field(None, description="Контекст взаимодействия")

class SearchRequest(BaseModel):
    """Модель запроса поиска информации"""
    query: str = Field(..., description="Поисковый запрос")

class SearchResponse(BaseModel):
    """Модель ответа с результатами поиска"""
    query: str = Field(..., description="Исходный поисковый запрос")
    result: str = Field(..., description="Результат поиска")
    relevant_sections: List[str] = Field([], description="Релевантные разделы платформы")

# Базовый эндпоинт для получения ответа от ассистента
@router.post("/ask", response_model=AssistantResponse)
async def ask_assistant(
    request: AssistantRequest
) -> AssistantResponse:
    """
    Получает ответ от ассистента на вопрос пользователя.
    
    Args:
        request: Параметры запроса (вопрос, контекст, идентификатор пользователя)
    
    Returns:
        Ответ ассистента
    """
    try:
        # Вызываем сервис для получения ответа
        answer = await assistant_service.get_answer(
            query=request.query,
            context=request.context,
            user_id=request.user_id
        )
        
        # Формируем и возвращаем ответ
        return AssistantResponse(
            answer=answer,
            user_query=request.query,
            context=request.context
        )
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Ошибка обработки запроса к ассистенту: {str(e)}")

# Альтернативный GET эндпоинт для более простых запросов
@router.get("/ask", response_model=AssistantResponse)
async def ask_assistant_get(
    query: str = Query(..., description="Вопрос пользователя"),
    context: Optional[str] = Query(None, description="Контекст взаимодействия"),
    user_id: Optional[str] = Query(None, description="Идентификатор пользователя")
) -> AssistantResponse:
    """
    GET-версия эндпоинта для получения ответа от ассистента.
    
    Args:
        query: Вопрос пользователя
        context: Контекст взаимодействия
        user_id: Идентификатор пользователя
    
    Returns:
        Ответ ассистента
    """
    try:
        # Вызываем сервис для получения ответа
        answer = await assistant_service.get_answer(
            query=query,
            context=context,
            user_id=user_id
        )
        
        # Формируем и возвращаем ответ
        return AssistantResponse(
            answer=answer,
            user_query=query,
            context=context
        )
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Ошибка обработки запроса к ассистенту: {str(e)}")

# Эндпоинт для поиска информации по платформе
@router.post("/search", response_model=SearchResponse)
async def search_info(
    request: SearchRequest
) -> SearchResponse:
    """
    Ищет информацию по платформе на основе запроса пользователя.
    
    Args:
        request: Параметры поиска (поисковый запрос)
    
    Returns:
        Результаты поиска с релевантной информацией
    """
    try:
        # Вызываем сервис для поиска информации
        search_results = await assistant_service.search_platform_info(request.query)
        
        # Формируем и возвращаем ответ
        return SearchResponse(
            query=request.query,
            result=search_results["result"],
            relevant_sections=search_results["relevant_sections"]
        )
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Ошибка поиска информации: {str(e)}")

# Альтернативный GET эндпоинт для поиска
@router.get("/search", response_model=SearchResponse)
async def search_info_get(
    query: str = Query(..., description="Поисковый запрос")
) -> SearchResponse:
    """
    GET-версия эндпоинта для поиска информации по платформе.
    
    Args:
        query: Поисковый запрос
    
    Returns:
        Результаты поиска с релевантной информацией
    """
    try:
        # Вызываем сервис для поиска информации
        search_results = await assistant_service.search_platform_info(query)
        
        # Формируем и возвращаем ответ
        return SearchResponse(
            query=query,
            result=search_results["result"],
            relevant_sections=search_results["relevant_sections"]
        )
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Ошибка поиска информации: {str(e)}") 
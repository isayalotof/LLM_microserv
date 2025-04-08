from fastapi import APIRouter, Query, HTTPException, Depends
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional, Dict, Any
import traceback

from app.services.gigachat import gigachat_service

# Создаем роутер
router = APIRouter(prefix="/api", tags=["text-enhancement"])

# Модели данных
class EnhancedTextResponse(BaseModel):
    """Модель ответа с улучшенным текстом"""
    original_text: str
    enhanced_text: str

# Базовый эндпоинт для улучшения текста
@router.get("/enhance", response_model=EnhancedTextResponse)
async def enhance_text(
    text: str = Query(..., description="Текст для улучшения")
) -> EnhancedTextResponse:
    """
    Улучшает текст, делая его более красочным, грамотным и продающим.
    
    Args:
        text: Исходный текст для улучшения
    
    Returns:
        Исходный и улучшенный тексты
    """
    try:
        # Вызываем сервис для улучшения текста
        enhanced_text = await gigachat_service.enhance_text(text)
        
        # Формируем и возвращаем ответ
        return EnhancedTextResponse(
            original_text=text,
            enhanced_text=enhanced_text
        )
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Ошибка обработки текста: {str(e)}")

# Расширенный эндпоинт с дополнительными параметрами
@router.get("/enhance/advanced", response_model=EnhancedTextResponse)
async def enhance_text_advanced(
    text: str = Query(..., description="Текст для улучшения"),
    style: Optional[str] = Query(None, description="Стиль текста (продающий, информационный, эмоциональный и т.д.)"),
    length: Optional[str] = Query(None, description="Желаемая длина результата (короткий, средний, длинный)")
) -> EnhancedTextResponse:
    """
    Улучшает текст с дополнительными настройками стиля и длины.
    
    Args:
        text: Исходный текст для улучшения
        style: Стиль текста (продающий, информационный, эмоциональный и т.д.)
        length: Желаемая длина результата (короткий, средний, длинный)
    
    Returns:
        Исходный и улучшенный тексты
    """
    try:
        # Вызываем сервис для улучшения текста с дополнительными параметрами
        enhanced_text = await gigachat_service.enhance_text(text, style, length)
        
        # Формируем и возвращаем ответ
        return EnhancedTextResponse(
            original_text=text,
            enhanced_text=enhanced_text
        )
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Ошибка обработки текста: {str(e)}")

# Эндпоинт для улучшения описаний компаний
@router.get("/enhance/company", response_model=EnhancedTextResponse)
async def enhance_company_description(
    text: str = Query(..., description="Описание компании для улучшения"),
    industry: Optional[str] = Query(None, description="Отрасль компании"),
    target_audience: Optional[str] = Query(None, description="Целевая аудитория"),
    unique_features: Optional[str] = Query(None, description="Уникальные особенности компании")
) -> EnhancedTextResponse:
    """
    Улучшает описание компании, делая его более привлекательным и информативным.
    
    Args:
        text: Исходное описание компании
        industry: Отрасль компании
        target_audience: Целевая аудитория
        unique_features: Уникальные особенности компании
    
    Returns:
        Исходное и улучшенное описание компании
    """
    try:
        # Формируем промпт с учетом специфики компании
        prompt = "Улучши описание компании, сделав его более привлекательным и информативным. "
        
        if industry:
            prompt += f"\nОтрасль: {industry}"
        if target_audience:
            prompt += f"\nЦелевая аудитория: {target_audience}"
        if unique_features:
            prompt += f"\nУникальные особенности: {unique_features}"
            
        prompt += f"\n\nИсходное описание: \"{text}\"\n\nУлучшенное описание:"
        
        # Вызываем сервис для улучшения текста
        enhanced_text = await gigachat_service.enhance_text(prompt)
        
        # Формируем и возвращаем ответ
        return EnhancedTextResponse(
            original_text=text,
            enhanced_text=enhanced_text
        )
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Ошибка обработки описания компании: {str(e)}") 
# Микросервис улучшения текста с GigaChat API

Микросервис на FastAPI для преобразования обычного текста в красочное, грамотное и продающее описание с использованием GigaChat API. Также включает ассистента для помощи пользователям платформы.

## Возможности

- Улучшение текста: преобразование обычного текста в продающее описание
- Два эндпоинта: базовый GET-эндпоинт и расширенный с дополнительными параметрами
- Интеграция с GigaChat API для нейросетевой обработки текста
- Ассистент для помощи пользователям платформы
- Контейнеризация с Docker для простого деплоя

## Установка и запуск

### Варианты установки

#### 1. Установка в виртуальное окружение

1. Клонируйте репозиторий
2. Установите зависимости:
```
pip install -r requirements.txt
```
3. Создайте файл `.env` на основе `.env.example` и заполните его вашими данными GigaChat API
4. Запустите приложение:
```
uvicorn app.main:app --reload
```

#### 2. Запуск с помощью Docker

1. Клонируйте репозиторий
2. Создайте файл `.env` на основе `.env.example` и заполните его вашими данными GigaChat API
3. Запустите сервис с помощью скрипта:
```
chmod +x start.sh
./start.sh
```

### Управление Docker-контейнером

Для управления Docker-контейнером используйте следующие скрипты:

- `start.sh` - запуск микросервиса
- `stop.sh` - остановка микросервиса
- `restart.sh` - перезапуск микросервиса

## API эндпоинты

### 1. Базовое улучшение текста

```
GET /api/enhance?text={ваш_текст}
```

### 2. Расширенное улучшение текста

```
GET /api/enhance/advanced?text={ваш_текст}&style={стиль}&length={длина}
```

Где:
- `style`: Стиль текста (продающий, информационный, эмоциональный и т.д.)
- `length`: Желаемая длина результата (короткий, средний, длинный)

### 3. Ассистент: получение ответа на вопрос

```
GET /api/assistant/ask?query={вопрос}&context={контекст}
```

```
POST /api/assistant/ask

{
  "query": "Как забронировать услугу?",
  "context": "Страница бронирования",
  "user_id": "123"
}
```

### 4. Ассистент: поиск информации о платформе

```
GET /api/assistant/search?query={поисковый_запрос}
```

```
POST /api/assistant/search

{
  "query": "Управление компанией"
}
```

## Примеры использования

### Улучшение текста

```
GET /api/enhance?text=Продаем синие джинсы
```

Ответ:
```json
{
  "original_text": "Продаем синие джинсы",
  "enhanced_text": "Идеальные синие джинсы премиум-качества для вашего стильного образа. Эксклюзивный крой подчеркнет вашу фигуру, а мягкий деним обеспечит комфорт на весь день. Станьте обладателем идеальной пары, которая прослужит вам не один сезон!"
}
```

### Запрос к ассистенту

```
POST /api/assistant/ask

{
  "query": "Как добавить новую компанию?",
  "context": "Административная панель"
}
```

Ответ:
```json
{
  "answer": "Для добавления новой компании в административной панели выполните следующие шаги:\n1. Перейдите в раздел 'Управление компаниями'\n2. Нажмите кнопку 'Добавить новую компанию'\n3. Заполните все необходимые поля в форме\n4. Нажмите 'Сохранить'\n\nПосле этого компания будет добавлена в систему и появится в списке.",
  "user_query": "Как добавить новую компанию?",
  "context": "Административная панель"
}
```

## Деплой

### Требования для деплоя

- Docker
- Docker Compose

### Порты

По умолчанию микросервис запускается на порту 8000. Вы можете изменить порт в файле `.env` или в `docker-compose.yml`.

### Конфигурация

Для настройки микросервиса используются переменные окружения в файле `.env`:

```
# GigaChat API Credentials
GIGACHAT_CLIENT_ID=...
GIGACHAT_CLIENT_SECRET=...
GIGACHAT_AUTH_KEY=...
GIGACHAT_SCOPE=GIGACHAT_API_PERS

# Assistant Settings
ASSISTANT_MODEL=GigaChat
ASSISTANT_TEMPERATURE=0.5
ASSISTANT_MAX_TOKENS=1000
PLATFORM_INFO_PATH=documentation.md

# API Settings
HOST=0.0.0.0
PORT=8000
DEBUG=True
``` 
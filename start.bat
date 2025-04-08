@echo off
echo Проверка наличия файла .env...

if not exist .env (
    echo Ошибка: Файл .env не найден. Создайте его на основе .env.example
    exit /b 1
)

echo Проверка наличия файла документации...

if not exist documentation.md (
    echo Предупреждение: Файл documentation.md не найден. Ассистент не сможет использовать информацию о платформе.
    echo Создайте файл документации или измените путь в .env
)

echo Запуск микросервиса в Docker...
docker-compose up -d --build

if %ERRORLEVEL% EQU 0 (
    echo Микросервис успешно запущен и доступен по адресу http://localhost:8000
    echo Документация API доступна по адресу http://localhost:8000/docs
) else (
    echo Ошибка при запуске микросервиса. Проверьте логи для получения дополнительной информации.
    exit /b 1
)

echo Вывод логов микросервиса:
docker-compose logs --tail=30 app 
pause
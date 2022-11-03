## Телеграм бот для опроса сервиса Yandex API о статусе выполнения домашнего задания
[![Python](https://img.shields.io/badge/-Python-464646?style=flat-square&logo=Python)](https://www.python.org/)
[![Telegram](https://img.shields.io/badge/-Telegram-464646?style=flat-square&logo=Telegram)](https://pypi.org/project/python-telegram-bot/)

Телеграм-бот для отслеживания статуса проверки домашней работы на Яндекс.Практикум.

Присылает сообщения, когда статус изменен - взято в проверку, есть замечания, зачтено.

**Как запустить проект**

- Клонировать репозиторий и перейти в него в командной строке:
```
git clone https://github.com/basyna/Telegram_bot.git
cd Telegram_bot
```
- Cоздать и активировать виртуальное окружение:
```
python -m venv venv
source venv/Script/activate
```
- Выполнить обновление пакетов
```
python -m pip install --upgrade pip
```
- Установить зависимости из файла requirements.txt:
```
pip install -r requirements.txt
```

Записать в переменные окружения (файл .env) необходимые ключи:
* `API_YANDEX_URL`  url адрес сервера api яндекс практикума
([https://practicum.yandex.ru/api/user_api/homework_statuses/](https://practicum.yandex.ru/api/user_api/homework_statuses/))
* `PRAKTIKUM_TOKEN` токен аутентификации Яндекс.Практикума
* `TELEGRAM_TOKEN`  телеграмм токен созданного вами бота
* `CHAT_ID`         id чата с вами

Запустить проект 
```
python homework.py
```

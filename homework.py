import logging
import os
import sys
import time
from http import HTTPStatus
from logging import StreamHandler

import requests
import telegram
from dotenv import load_dotenv

from exceptions import (
    EndpointError,
    ExceptionWithSendingError,
    HomeworksTypeError,
    SendingError
)

load_dotenv()


PRACTICUM_TOKEN = os.getenv('PRACTICUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

RETRY_TIME = 600
ENDPOINT = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}


HOMEWORK_VERDICTS = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена: у ревьюера есть замечания.'
}


def set_logging():
    """Функция формирует и возвращает логгер согласно задания."""
    logging.basicConfig(
        format='%(asctime)s, %(levelname)s, %(message)s'
    )
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)
    handler = StreamHandler()
    handler.setStream(sys.stdout)
    logger.addHandler(handler)
    formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s'
    )
    handler.setFormatter(formatter)
    return logger


logger = set_logging()


def send_message(bot, message):
    """Функция отправки сообщения с проверкой."""
    logger.info(f'Начало отправки сообщения "{message}"')
    try:
        bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message)
    except Exception as error:
        raise SendingError(
            f'Не удалось отправить сообщение "{message}". Ошибка:{error}'
        )
    else:
        logger.info(
            f'Бот отправил сообщение "{message}"'
        )


def get_api_answer(current_timestamp):
    """Получение ответа API, проверка статуса ответа."""
    timestamp = current_timestamp or int(time.time())
    params = {'from_date': timestamp}
    logger.debug(
        f'Начале запроса к эндпойнту {ENDPOINT}  с параметром {params}'
    )
    response = requests.get(ENDPOINT, headers=HEADERS, params=params)
    if response.status_code != HTTPStatus.OK:
        raise EndpointError(
            f'Сбой в работе программы: Эндпоинт {ENDPOINT} недоступен.'
            f'Код ответа API: {response.status_code}'
        )
    else:
        return response.json()


def check_response(response):
    """Проверка ответа сервера."""
    if not isinstance(response, dict):
        raise TypeError(
            'В ответе пришёл не словарь'
        )
    try:
        hw_list = response['homeworks']
        hw_date = response['current_date']
    except KeyError as error:
        raise KeyError(
            f'Ключ {error} не обнаружен на момент времени {hw_date}.'
        )
    if not isinstance(hw_list, list):
        raise HomeworksTypeError(
            'Объект homeworks не является списком.'
        )
    return hw_list


def parse_status(homework):
    """Проверяет статус входящего словаря и возвращает сообщение."""
    try:
        homework_status = homework['status']
        homework_name = homework['homework_name']
        verdict = HOMEWORK_VERDICTS[homework_status]
    except KeyError as error:
        raise KeyError(
            f'Ошибка получения данных по ключу "{error}"'
            f' в функции parse_status.'
        )
    return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def check_tokens():
    """Функция проверки наличия необходимых данных."""
    return all([PRACTICUM_TOKEN, TELEGRAM_TOKEN, TELEGRAM_CHAT_ID])


def main():
    """Основная логика работы бота."""
    if not check_tokens():
        logger.critical('Токены не доступны. Работа не возможна!')
        sys.exit('Токены не доступны. Работа не возможна!')
    current_timestamp = int(time.time())
    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    last_error = ''
    while True:
        try:
            response = get_api_answer(current_timestamp)
            homeworks = check_response(response)
            if homeworks:
                message = parse_status(homeworks[0])
                send_message(bot, message)
            else:
                logger.debug('Нет новых записей')
            current_timestamp = response.get(
                'current_date', current_timestamp
            )
        except (ExceptionWithSendingError, KeyError, TypeError) as error:
            if error != last_error:
                send_message(bot, error)
                last_error = error
            logger.error(error)
        except Exception as error:
            error_message = f'Сбой в работе программы: {error}'
            logger.error(error_message)
        finally:
            time.sleep(RETRY_TIME)


if __name__ == '__main__':
    main()

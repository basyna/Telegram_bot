import logging
import os
import sys
import time
from logging import StreamHandler

import requests
import telegram
from dotenv import load_dotenv

from exceptions import EndpointError, HomeworksKeyError, HomeworksListError

load_dotenv()


PRACTICUM_TOKEN = os.getenv('PRACTICUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

RETRY_TIME = 15
ENDPOINT = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}


HOMEWORK_STATUSES = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена: у ревьюера есть замечания.'
}


def set_logging():
    """Функция формирует и возвращает логгер."""
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
    try:
        bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message)
    except Exception as error:
        logger.error(
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
    response = requests.get(ENDPOINT, headers=HEADERS, params=params)
    if response.status_code != 200:
        raise EndpointError(
            f'Сбой в работе программы: Эндпоинт {ENDPOINT} недоступен.'
            f'Код ответа API: {response.status_code}'
        )
    else:
        return(response.json())


def check_response(response):
    """Проверка ответа сервера."""
    try:
        hw_list = response['homeworks']
    except KeyError:
        raise HomeworksKeyError(
            'Ключ homeworks не обнаружен.'
        )
    if not isinstance(hw_list, list):
        raise HomeworksListError(
            'Объект homeworks не является списком.'
        )
    return(hw_list)


def parse_status(homework):
    """Проверяет статус входящего словаря и возвращает сообщение."""
    try:
        homework_status = homework['status']
        homework_name = homework['homework_name']
        verdict = HOMEWORK_STATUSES[homework_status]
    except KeyError:
        raise KeyError(
            'Ошибка получения данных по ключу в функции parse_status.'
        )
    return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def check_tokens():
    """Функция проверки наличия необходимых данных."""
    if PRACTICUM_TOKEN and TELEGRAM_TOKEN and TELEGRAM_CHAT_ID:
        return True
    else:
        return False


def main():
    """Основная логика работы бота."""
    if not check_tokens():
        logger.critical('Токены не доступны. Работа не возможна!')
        raise SystemExit
    current_timestamp = int(time.time())
    not_ready_to_exit = True
    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    last_error = ''
    while not_ready_to_exit:
        try:
            response = get_api_answer(current_timestamp)
            last_hw = check_response(response)[0]
            message = parse_status(last_hw)
        except IndexError:
            logger.debug('Нет новых записей')
        except Exception as error:
            error_message = f'Сбой в работе программы: {error}'
            logger.error(error_message)
            if last_error != error:
                send_message(bot, error_message)
                last_error = error
        else:
            send_message(bot, message)
            if last_hw['status'] == 'approved':
                not_ready_to_exit = False
            current_timestamp = response.get('current_date', current_timestamp)
        finally:
            time.sleep(RETRY_TIME)


if __name__ == '__main__':
    main()

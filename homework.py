import logging
import os
import requests
import time
import telegram
from http import HTTPStatus

from dotenv import load_dotenv

import exceptions

load_dotenv()


PRACTICUM_TOKEN = os.getenv('PRACTICUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

RETRY_TIME = 600
ENDPOINT = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}


HOMEWORK_STATUSES = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена: у ревьюера есть замечания.'
}

logging.basicConfig(
    level=logging.INFO,
    filename='main.log',
    format='%(asctime)s, %(levelname)s, %(message)s'
)


def send_message(bot, message):
    """Отправляет сообщение в Телеграм бот."""
    bot.send_message(TELEGRAM_CHAT_ID, message)
    logging.info('Сообщение успешно доставлено')


def get_api_answer(current_timestamp):
    """Делает запрос к единственному эндпоинту API-сервис."""
    timestamp = current_timestamp or int(time.time())
    params = {'from_date': timestamp}
    try:
        homework_status = requests.get(ENDPOINT,
                                       headers=HEADERS,
                                       params=params
                                       )
    except exceptions.ExceptionApiStausCode:
        raise exceptions.ExceptionApiStausCode(
            f'Ошибка запроса: {homework_status.status_code}'
        )
    if homework_status.status_code != HTTPStatus.OK:
        status_code = homework_status.status_code
        raise exceptions.ExceptionApiStausCode(f'Ошибка: {status_code}')
    return homework_status.json()


def check_response(response):
    """Проверяет API на корректность."""
    homework_list = response['homeworks']
    if homework_list is None or not isinstance(homework_list, list):
        raise TypeError('Ответ API отличен от словаря')
    if homework_list is None or not isinstance(homework_list, list):
        raise TypeError('Ошибка словаря по ключу "homeworks"')
    if len(homework_list) == 0:
        raise IndexError('Список домашек пуст')
    return homework_list


def parse_status(homework):
    """Извлекает из информации о домашней работе статус этой работы."""
    if 'homework_name' not in homework:
        raise KeyError('отсутсвует ключ словаря "homework_name"')
    if 'status' not in homework:
        raise KeyError('Отсутсвует ключ словаря "homework_status"')
    homework_name = homework['homework_name']
    homework_status = homework['status']
    if homework_status not in HOMEWORK_STATUSES:
        raise exceptions.UnknownStatusHomeWork(
            f'Некорректный статус: {homework_status}'
        )
    verdict = HOMEWORK_STATUSES[homework_status]
    return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def check_tokens():
    """Проверяет доступность переменных окружения."""
    return all([PRACTICUM_TOKEN, TELEGRAM_TOKEN, TELEGRAM_CHAT_ID])


def main():
    """Основная логика работы бота."""
    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    current_timestamp = int(time.time()) - RETRY_TIME

    while True:
        try:
            response = get_api_answer(current_timestamp)
            message = parse_status(check_response(response))
        except exceptions.IncorrectAPIResponse as error:
            if message == str(error):
                send_message(bot, error)
            logging.error(error)
            time.sleep(RETRY_TIME)
            continue
        try:
            homeworks = check_response(response)
            homeworks_status = homeworks.get('status')
            if homeworks_status:
                message = parse_status(homeworks[0])
                send_message(bot, message)
            else:
                logging.debug('Обновляшки нет')
            time.sleep(RETRY_TIME)

        except Exception as error:
            message = f'Ошибка в проге: {error}'
            logging.exception(message)
            try:
                bot.send_message(TELEGRAM_CHAT_ID, message)
            except Exception as error:
                message = f'Сообщение не доставлено: {error}'
                logging.exception(message)
            time.sleep(RETRY_TIME)


if __name__ == '__main__':
    main()

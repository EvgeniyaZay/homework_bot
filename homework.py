import logging
import os
import requests
import time
import telegram
from http import HTTPStatus

from dotenv import load_dotenv

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
    try:
        bot.send_message(TELEGRAM_CHAT_ID, message)
        logging.info('Сообщение успешно доставлено')
    except telegram.TelegramError as error:
        message = f'Сообщение не доставлено: {error}'
        logging.error(message)


def get_api_answer(current_timestamp):
    """Делает запрос к единственному эндпоинту API-сервис."""
    timestamp = current_timestamp or int(time.time())
    params = {'from_date': timestamp}
    headers = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}
    try:
        homework_status = requests.get(ENDPOINT,
                                       headers=headers,
                                       params=params
                                       )
    except Exception as error:
        message = f'Ошибка запроса: {homework_status.status_code}'
        logging.error(message)
        return error
    if homework_status.status_code != HTTPStatus.OK:
        status_code = homework_status.status_code
        logging.error(f'Ошибка: {status_code}')
        raise Exception(f'Ошибка: {status_code}')
    try:
        return homework_status.json()
    except ValueError:
        logging.error('Ошибка ответа из формата json')
        raise ValueError('Ошибка ответа из формата json')


def check_response(response):
    """Проверяет API на корректность."""
    if type(response) is not dict:
        raise TypeError('Ответ API отличен от словаря')
    try:
        homework_list = response['homeworks']
    except KeyError:
        logging.error('Ошибка словаря по ключу homeworks')
        raise KeyError('Ошибка словаря по ключу homeworks')
    try:
        homework = homework_list[0]
    except IndexError:
        logging.error('Список домашек пуст')
        raise IndexError('Список домашек пуст')
    return homework


def parse_status(homework):
    """Извлекает из информации о конкретной домашней работе статус этой работы.
    """
    if 'homework_name' not in homework:
        raise KeyError('отсутсвует ключ словаря "homework_name"')
    if 'status' not in homework:
        raise Exception('Отсутсвует ключ словаря "homework_status"')
    homework_name = homework['homework_name']
    homework_status = homework['status']
    if homework_status not in HOMEWORK_STATUSES:
        raise Exception(f'Некорректный статус: {homework_status}')
    verdict = HOMEWORK_STATUSES[homework_status]
    return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def check_tokens():
    """Проверяет доступность переменных окружения."""
    env_params = [PRACTICUM_TOKEN, TELEGRAM_TOKEN, TELEGRAM_CHAT_ID]
    for env_var in env_params:
        if env_var is None:
            logging.critical('Всё упало')
            return False
    logging.info('Всё прошло успешно')
    return True


def main():
    """Основная логика работы бота."""
    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    current_timestamp = int(time.time()) - RETRY_TIME
    while True:
        try:
            response = get_api_answer(current_timestamp)
            current_timestamp = response.get('current_date')
            message = parse_status(check_response(response))
            send_message(bot, message)
            time.sleep(RETRY_TIME)
        except Exception as error:
            message = str(error)
            logging.error(error)
            send_message(bot, message)
        time.sleep(RETRY_TIME)


if __name__ == '__main__':
    main()

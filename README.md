# homework_bot
# hw04_tests

## homework_bot
Python telegram bot for Yandex.Homework Telegram-бот на Python использующий API Яндекс.Домашка для отслеживания статусов сданных работ

Бот раз в 10 минут опрашивает API сервиса Практикум.Домашка и проверяет статус отправленной на ревью домашней работы; при обновлении статуса анализирует ответ API и отправляет соответствующее уведомление в Telegram; логирует свою работу и сообщает о важных проблемах сообщением в Telegram.


## Инструкция по установке
##### Клонируем репозиторий

git clone git@github.com:EvgeniyaZay/homework_bot.git

##### Переходим в папку с проектом

homework_bot/

##### Устанавливаем отдельное виртуальное окружение для проекта

python3 -m venv venv

##### Активируем виртуальное окружение

source venv/bin/activate

##### Устанавливаем модули необходимые для работы проекта

pip install -r requirements.txt

##### Запустить проект
python3 manage.py runserver
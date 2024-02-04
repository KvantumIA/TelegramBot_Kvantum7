import os
import telebot
import time
from data import TelBot
from telebot import types
from selenium.common.exceptions import WebDriverException

bot = telebot.TeleBot('6880345844:AAFBkJ0GQruvvMIyOMcseNVIboVXM_icTns')
start = TelBot()

try:
    @bot.message_handler(commands=['start'])
    def send_welcome(message):
        bot.reply_to(message, "Привет! Я бот помощник. Для начала работы выберите пункт меню.")
        print(message.chat.id)

    # Выбор загрузки файла в процессе работы
    def question_upload_file(message):
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton('Загрузить новый файл. Он автоматически конвертируется в архив.', callback_data='send_file'))
        markup.add(types.InlineKeyboardButton('Загрузить созданный архив.', callback_data='next_step_upload_file'))
        bot.send_message(message.chat.id, "Пожалуйста выберите пункт меню.", reply_markup=markup)
        print("Выбор способа загрузки файла.")

    # Начало работы загрузки данных на сайт
    @bot.message_handler(commands=['upload_file'])
    def echo_all(message):
        start.chat_id = message.chat.id
        if message.text == "/upload_file":
            bot.send_message(message.chat.id, "Начал работать. Подождите...")
            attempts = 0
            start.start_step()
            answer_capcha(message)
            time.sleep(15)  # Время для ответа на капчу
            start.two_step()

            while start.capcha_error and attempts < 5:
                bot.send_message(message.chat.id, "Вы неверно ввели Capcha. Пожалуйста повторите.")
                answer_capcha(message)
                time.sleep(15)  # Время для ответа на капчу
                start.two_step()
                attempts += 1

            if attempts == 5:  # Если прошло 5 попыток
                bot.send_message(message.chat.id, "Прошло 5 попыток ввода Capcha. Пожалуйста, повторите позже. Приложение закрыто.")
                start.browser.close()
                start.browser.quit()
                return

            # send_file(message)
            bot.send_message(message.chat.id, "Вы успешно прошли капчу.")
            question_upload_file(message)
            time.sleep(45)
            print("Загрузка файла.")
            next_step(message)

    # Проверяем капчу
    def answer_capcha(message):
        bot.send_message(message.chat.id, "Расшифруйте 4 буквы из картинки и отправьте мне.")
        bot.register_next_step_handler(message, returning)


    def returning(message):
        start.answer = message.text

    # Продолжаем работать, следующий шаг
    def next_step(message):
        attempts = 0
        while len(start.answer_date) == 0 and attempts < 5:
            get_date(message)
            time.sleep(60)  # Время для записи наименования ссылки на сайте
            attempts += 1
        if attempts == 5:  # Если прошло 5 попыток
            bot.send_message(message.chat.id, "Прошло 5 попыток ввода имени файла. Пожалуйста, повторите позже. Приложение закрыто.")
            start.answer_date = ''
            start.browser.close()
            start.browser.quit()
            return

        bot.send_message(message.chat.id, "Наименование для ссылки успешно добавлено. Дальше работаю сам. Остались последние шаги.")
        time.sleep(5)  # поменял время, было 30
        start.three_step()

        message_text = (f"Все прошло успешно, данные загружены на [сайт](https://ykt-dou35.obr.sakha.gov.ru/sveden/organizatsiya-pitaniya-v-obrazovatelynoy-organizatsii"
                        f"/ezhednevnoe-menyu-goryachego-pitaniya)")
        bot.send_message(message.chat.id, message_text, parse_mode='MarkdownV2')
        return

    # Получаем название для записи на сайте
    def get_date(message):
        bot.send_message(message.chat.id, "Пожалуйста введите название для файла на сайте. У вас 60 секунд.")
        print("Отправлен запрос на наименование ссылки для сайта.")
        bot.register_next_step_handler(message, returning_get_date)


    def returning_get_date(message):
        start.answer_date = message.text

    # Проверяем ответ на кнопки выбора загрузки файла
    @bot.callback_query_handler(func=lambda callback: True)
    def callback_message(callback):
        if callback.data == "next_step_upload_file":
            if os.path.exists(start.file_zip_path) and os.path.isfile(start.file_zip_path) and start.file_zip_path.endswith('.rar'):
                print("Выбрана загрузка файла с сервера.")
                start.upload_file(start.file_zip_path)
                time.sleep(5)
            else:
                bot.send_message(1624502869, "Вы предварительно не создали архив! Пожалуйста выберите в меню 'Добавьте файлы в архив.' и затем снова попробуйте загрузить данные "
                                             "на сайт. Либо выберите 'Загрузить новый файл в формате архива.' Программа завершена.")
                start.browser.close()
                start.browser.quit()
                return
        elif callback.data == "send_file":
            send_file(callback.message)

    # Сохраняем файлы в архив по одному в процессе работы
    def send_file(message):
        bot.send_message(message.chat.id, "Пожалуйста отправьте файл.")
        bot.register_next_step_handler(message, get_file)
        print("Выбрана загрузка файла пользователем.")

    def get_file(message):
        # Проверяем, есть ли у сообщения файл
        if message.document:
            file_info = bot.get_file(message.document.file_id)
            downloaded_file = bot.download_file(file_info.file_path)

            file_download = message.document
            file_name = file_download.file_name
            start.name_file_zip = file_name

            file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'temp', file_name)
            with open(file_path, 'wb') as file:
                file.write(downloaded_file)
            bot.send_message(message.chat.id, f'Файл успешно сохранен. Подождите немного для загрузки файла на сервер...')
            start.add_to_zip(file_path)
            time.sleep(5)
            start.upload_file(start.file_zip_path)
            time.sleep(5)
        else:
            bot.send_message(1624502869, f'Вы отправили не файл. Пожалуйста повторите.')
            get_file(message)

    # Сохраняем файлы в общий архив
    @bot.message_handler(commands=['add_zip_file'])
    def add_zip_file(message):
        bot.send_message(message.chat.id, "Пожалуйста отправьте файлы по одному, что бы сохранить в архив.")
        bot.register_next_step_handler(message, add_zip)

    def add_zip(message):
        if message.document:
            file_info = bot.get_file(message.document.file_id)
            downloaded_file = bot.download_file(file_info.file_path)

            file_download = message.document
            file_name = file_download.file_name
            start.name_file_zip = file_name

            file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'temp', file_name)
            with open(file_path, 'wb') as file:
                file.write(downloaded_file)

            start.add_to_zip(file_path)
            # Отправляем пользователю сообщение, что файл загружен
            bot.send_message(message.chat.id, f'Файл успешно сохранен и добавлен в архив.')

except Exception as ex:
    print(ex)

while True:
    try:
        bot.polling()
    except WebDriverException as e:
        bot.send_message(start.chat_id, "Произошла ошибка WebDriver. Повторите попытку позже.")
        print("Произошла ошибка WebDriver:")
        print(e)
    except Exception as e:
        bot.send_message(start.chat_id, "Произошла неизвестная ошибка. Повторите попытку позже.")
        print("Произошла неизвестная ошибка:")
        print(e)

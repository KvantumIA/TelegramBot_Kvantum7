import os
import telebot
import time
import Token_ID
from data import TelBot
from telebot import types
from selenium.common.exceptions import WebDriverException


class TelegramBot:
    def __init__(self):
        self.token = Token_ID.TokenId()
        self.token2 = self.token.id_token()
        self.bot = telebot.TeleBot(self.token2)
        self.start = TelBot()
        self.command_in_progress = False

        @self.bot.message_handler(commands=['self.start'])
        def send_welcome(message):
            self.bot.reply_to(message, "Привет! Я бот помощник. Для начала работы выберите пункт меню.")
            print(message.chat.id)

        # Начало работы загрузки данных на сайт
        @self.bot.message_handler(commands=['upload_file'])
        def bot_one_step(message):
            # Проверяем на повторную команду
            if self.command_in_progress:
                self.bot.send_message(message.chat.id, "Не нажимайте команду повторно. Работа уже идет.")
                return
            else:
                self.command_in_progress = True
                self.bot.send_message(message.chat.id, "Начал работать. Подождите...")
                print("Начал работать.")
            self.start.chat_id = message.chat.id

            # Начало работы
            if message.text == "/upload_file":
                # Заходим с куки
                if os.path.exists('cookies'):
                    self.start.create_windows()
                    self.start.checking_cookies()
                    if self.start.cookies_check:
                        bot_two_step(message)
                    else:
                        print("Бот: Куки недействительны. Закрываю приложение. Начата загрузка сайта с вводом куки.")
                        return

                # Заходим без куки
                else:
                    attempts = 0
                    self.start.create_windows()
                    time.sleep(3)
                    self.start.start_step()
                    answer_capcha(message)
                    time.sleep(15)  # Время для ответа на капчу
                    self.start.two_step()

                    # Проверка капчи
                    while self.start.capcha_error and attempts < 5:
                        self.bot.send_message(message.chat.id, "Вы неверно ввели Capcha. Пожалуйста повторите.")
                        answer_capcha(message)
                        time.sleep(15)  # Время для ответа на капчу
                        self.start.two_step()
                        attempts += 1

                    if attempts == 5:  # Если прошло 5 попыток
                        self.bot.send_message(message.chat.id, "Прошло 5 попыток ввода Capcha. Пожалуйста, повторите позже. Приложение закрыто.")
                        self.start.browser.close()
                        self.start.browser.quit()
                        return

                    bot_two_step(message)

        def bot_two_step(message):
            self.start.three_step()
            time.sleep(5)
            question_upload_file(message)
            time.sleep(45)
            print("Загрузка файла.")
            while len(self.start.answer_next_step) == 0:
                time.sleep(1)  # Даём время для получения ответа
            bot_three_step(message)

        # Продолжаем работать, следующий шаг
        def bot_three_step(message):
            attempts = 0
            # Проверка на название файла. 5 попыток.
            while len(self.start.answer_date) == 0 and attempts < 5:
                get_date(message)
                time.sleep(60)  # Время для записи наименования ссылки на сайте
                attempts += 1
            if attempts == 5:  # Если прошло 5 попыток
                self.bot.send_message(message.chat.id, "Прошло 5 попыток ввода имени файла. Пожалуйста, повторите позже. Приложение закрыто.")
                self.start.answer_date = ''
                self.start.browser.close()
                self.start.browser.quit()
                return

            self.bot.send_message(message.chat.id, "Наименование для ссылки успешно добавлено. Дальше работаю сам. Остались последние шаги.")
            time.sleep(1)
            self.start.four_step()

            message_text = (f"Все прошло успешно, данные загружены на [сайт](https://ykt-dou35.obr.sakha.gov.ru/sveden/organizatsiya-pitaniya-v-obrazovatelynoy-organizatsii"
                            f"/ezhednevnoe-menyu-goryachego-pitaniya)")
            self.bot.send_message(message.chat.id, message_text, parse_mode='MarkdownV2')
            self.command_in_progress = False
            return

        # Проверяем капчу
        def answer_capcha(message):
            self.bot.send_message(message.chat.id, "Расшифруйте 4 буквы из картинки и отправьте мне.")
            self.bot.register_next_step_handler(message, returning)

        def returning(message):
            self.start.answer = message.text

        # Выбор загрузки файла в процессе работы
        def question_upload_file(message):
            markup = types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton('Загрузить новый файл.', callback_data='send_file'))
            markup.add(types.InlineKeyboardButton('Отправить созданный архив.', callback_data='next_step_upload_file'))
            self.bot.send_message(message.chat.id, "Пожалуйста выберите способ загрузки файлов на сайт.", reply_markup=markup)
            print("Выбор способа загрузки файла.")

        # Получаем название для записи на сайте
        def get_date(message):
            self.bot.send_message(message.chat.id, "Пожалуйста введите название для файла на сайте. У вас 60 секунд.")
            print("Отправлен запрос на наименование ссылки для сайта.")
            self.bot.register_next_step_handler(message, returning_get_date)

        def returning_get_date(message):
            self.start.answer_date = message.text

        # Проверяем ответ на кнопки выбора загрузки файла
        @self.bot.callback_query_handler(func=lambda callback: True)
        def callback_message(callback):
            if callback.data == "next_step_upload_file":
                if os.path.exists(self.start.file_zip_path) and os.path.isfile(self.start.file_zip_path) and self.start.file_zip_path.endswith('.rar'):
                    print("Выбрана загрузка файла с сервера.")
                    self.start.upload_file(self.start.file_zip_path)
                    time.sleep(5)
                else:
                    self.bot.send_message(self.start.chat_id,
                                          "Вы предварительно не создали архив! Пожалуйста выберите в меню 'Добавьте файлы в архив.' и затем снова попробуйте загрузить данные "
                                          "на сайт. Либо выберите 'Загрузить новый файл в формате архива.' Программа завершена.")
                    self.start.browser.close()
                    self.start.browser.quit()
                    return
            elif callback.data == "send_file":
                send_file(callback.message)

        # Сохраняем файлы в архив по одному в процессе работы
        def send_file(message):
            self.bot.send_message(message.chat.id, "Пожалуйста отправьте файл.")
            self.bot.register_next_step_handler(message, get_file)
            print("Выбрана загрузка файла пользователем.")

        def get_file(message):
            # Проверяем, есть ли у сообщения файл
            if message.document:
                file_info = self.bot.get_file(message.document.file_id)
                downloaded_file = self.bot.download_file(file_info.file_path)

                # Получение наименования файла
                file_download = message.document
                file_name = file_download.file_name
                self.start.name_file_zip = file_name

                file_path = os.path.join('.', file_name)
                with open(file_path, 'wb') as file:
                    file.write(downloaded_file)
                self.bot.send_message(message.chat.id, f'Файл успешно сохранен. Подождите немного для загрузки файла на сервер...')
                self.start.add_to_zip(file_path)
                time.sleep(5)
                self.start.upload_file(self.start.file_zip_path)
                time.sleep(5)
            else:
                self.bot.send_message(message.chat.id, f'Вы отправили не файл. Пожалуйста повторите.')
                send_file(message)

        # Сохраняем файлы в общий архив
        @self.bot.message_handler(commands=['add_zip_file'])
        def add_zip_file(message):
            self.command_in_progress = True
            self.bot.send_message(message.chat.id, "Пожалуйста отправьте файлы по одному, что бы сохранить в архив.")
            self.bot.register_next_step_handler(message, add_zip)

        def add_zip(message):
            if message.document:
                file_info = self.bot.get_file(message.document.file_id)
                downloaded_file = self.bot.download_file(file_info.file_path)

                file_download = message.document
                file_name = file_download.file_name
                self.start.name_file_zip = file_name

                file_path = os.path.join('.', file_name)
                with open(file_path, 'wb') as file:
                    file.write(downloaded_file)

                self.start.add_to_zip(file_path)
                # Отправляем пользователю сообщение, что файл загружен
                self.bot.send_message(message.chat.id, f'Файл успешно сохранен и добавлен в архив.')
            else:
                self.bot.send_message(message.chat.id, 'Вы отправили не файл! Пожалуйста отправьте файл.')
                add_zip_file(message)

    def start_bot(self):
        while True:
            try:
                self.bot.polling()
            except WebDriverException as e:
                self.bot.send_message(self.start.chat_id, "Произошла ошибка WebDriver. Повторите попытку позже.")
                print("Произошла ошибка WebDriver:")
                print(e)
                self.start.browser.close()
                self.start.browser.quit()
            except Exception as e:
                self.bot.send_message(self.start.chat_id, "Произошла неизвестная ошибка. Повторите попытку позже.")
                print("Произошла неизвестная ошибка:")
                print(e)
                self.start.browser.close()
                self.start.browser.quit()


if __name__ == "__main__":
    bot = TelegramBot()
    bot.start_bot()

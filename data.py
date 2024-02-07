import requests
from selenium import webdriver
import os
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time
from selenium.webdriver.chrome.options import Options
from datetime import datetime
from PIL import Image
from selenium.common.exceptions import NoAlertPresentException
import zipfile
import pickle

import Token_ID

token = Token_ID.TokenId()
token2 = token.id_token()


class TelBot:
    try:
        def __init__(self, original_window=None, browser=None):
            self.answer = ''
            self.answer_date = ''
            self.original_window = original_window
            self.browser = browser
            self.capcha_error = False
            self.wait_upload = False
            current_dir = os.path.dirname(os.path.abspath(__file__))
            self.current_date = datetime.now().date()
            self.file_zip_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), f"menu_archive_{self.current_date}.rar")
            self.name_file_zip = ''
            self.chat_id = ''
            self.bot_token = token2
            self.answer_next_step = ''

        # Начало работы. Первый шаг.
        def start_step(self):
            o = Options()
            # o.add_argument("--headless")  # скрытый режим без окна браузера
            # o.add_argument("--no-sandbox")
            # o.add_argument("--disable-gpu")
            # o.page_load_strategy = 'eager'     # не ждать окончания загрузки страницы
            o.add_experimental_option("detach", True)
            self.browser = webdriver.Chrome(options=o)
            self.browser.maximize_window()
            self.browser.get('https://ykt-dou35.obr.sakha.gov.ru/user/frontLogin')
            time.sleep(3)

            try:
                self.browser.find_element(By.CLASS_NAME, 'cookie-popup-accept-cookies').click()
            except Exception:
                print("Оповещение о куки не найдено")

            time.sleep(3)
            # image_path = os.path.join(self.temp_dir, 'all_screen.png')
            self.browser.save_screenshot("all_screen.png")
            print("Первоначальный снимок экрана сделан.")

            self.original_window = self.browser.current_window_handle

            print("Вводим логин.")
            login_input = self.browser.find_element(By.ID, 'UserLogin_username')
            login_input.clear()
            login_input.send_keys('ykt-dou35')
            time.sleep(1)

            print("Вводим пароль.")
            password_input = self.browser.find_element(By.ID, 'UserLogin_password')
            password_input.clear()
            password_input.send_keys('Sever35S')
            time.sleep(1)

            self.browser.save_screenshot('screen_display.png')
            print("Общий снимок экрана сделан.")
            self.browser.find_element(By.ID, 'yw0').screenshot('capcha_screen.png')
            time.sleep(2)
            print("Отправляем капчу.")
            self.send_image_to_bot()

        # Продолжение работы. Второй шаг.
        def two_step(self):
            self.browser.switch_to.window(self.original_window)
            answer_capcha = self.answer
            try:
                capcha_input = self.browser.find_element(By.ID, 'UserLogin_verifyCode')
                capcha_input.clear()
                capcha_input.send_keys(answer_capcha)
                time.sleep(2)

                capcha_input.send_keys(Keys.ENTER)
                time.sleep(3)

                # Проверяем чтобы не было ошибки капчи
                elements = self.browser.find_elements(By.CLASS_NAME, 'errorMessage')
                # Переходим на всплывающее окно для загрузки файла
                if not elements:
                    print("Капча принята")
                    # pickle.dump(self.browser.get_cookies(), open("cookies", "wb"))      # Сохранение куки
                    self.capcha_error = False
                    self.browser.get('https://ykt-dou35.obr.sakha.gov.ru/pages/back/update?type=0&id=531799')
                    time.sleep(5)
                    print("Нажатие на кнопку создания ссылки")
                    self.browser.find_element(By.CLASS_NAME, 'cke_button__link_icon').click()
                    time.sleep(3)
                    print("Переход на страничку загрузки файла")
                    self.browser.find_element(By.ID, 'cke_upload_205').click()
                    time.sleep(2)

                    # for cookies in pickle.load(open("cookies", "rb")):            # Загрузка куки
                    #     self.browser.add_cookie(cookies)

                else:
                    self.find_error()
            except Exception as e:
                print(e)

        # Продолжение работы. Третий шаг.
        def three_step(self):
            self.browser.switch_to.window(self.original_window)
            print("Переключился на основной экран браузера.")
            time.sleep(3)
            self.browser.find_element(By.ID, 'cke_96_textInput').send_keys(self.answer_date)
            print("Наименование ссылки успешно добавлено.")
            time.sleep(5)
            self.browser.find_element(By.ID, 'cke_207_label').click()
            time.sleep(5)
            name_iframe = self.browser.find_element(By.XPATH, "//iframe[@title='Визуальный текстовый редактор, StaticPage_description']")
            self.browser.switch_to.frame(name_iframe)
            print("Переход на iframe текстового окна.")

            paragraphs = self.browser.find_elements(By.TAG_NAME, 'p')
            # Проверяем, есть ли 12-ый элемент в списке
            if len(paragraphs) > 12:
                paragraph_one = paragraphs[0]
                paragraph_one.send_keys(Keys.HOME)
                time.sleep(1)
                paragraph_one.send_keys(Keys.ENTER)
                time.sleep(2)
                print("Передвинута 1 строчка")

                paragraph = paragraphs[10]  # Индекс 11 соответствует 12-ому элементу
                paragraph.clear()
                time.sleep(1)
                time.sleep(5)
                print("Удалена 11 строчка")

            else:
                print("На странице нет 12-ой строки.")

            self.browser.switch_to.default_content()
            print("Выход из iframe текстового окна.")
            self.answer_date = ''
            self.browser.find_element(By.XPATH, "(//button[@class='btn icon icon-ok'])[2]").click()
            print("Все успешно. Программа завершена.")
            time.sleep(5)

            self.browser.close()
            self.browser.quit()

        # Обрезаем изображение капчи. Функция отключена.
        # def crop_image(self):
        #     image = Image.open("temp/screen_display.png", "r")
        #     # width, height = image.size     # Отправляет размер скриншота общего экрана
        #     # print(width)
        #     # print(height)
        #     left = 180
        #     top = 420
        #     right = 290
        #     bottom = 530
        #
        #     # Вырезаем область изображения
        #     cropped_image = image.crop((left, top, right, bottom))
        #     print("Капча обрезана.")
        #     image_path = os.path.join(self.temp_dir, 'cropped_image.png')
        #     cropped_image.save(image_path)

        # Отправляем капчу в телеграмм бот
        def send_image_to_bot(self):
            chat_id = self.chat_id  # Идентификатор чата, куда вы хотите отправить изображение
            bot_api_url = f'https://api.telegram.org/bot{self.bot_token}/sendPhoto'
            image_path = os.path.join('.', 'capcha_screen.png')
            time.sleep(3)
            # Открываем изображение
            with open(image_path, 'rb') as image_file:
                files = {'photo': image_file}
                data = {'chat_id': chat_id}
                response = requests.post(bot_api_url, files=files, data=data)

            if response.status_code == 200:
                print("Изображение успешно отправлено в чат бота.")
            else:
                print("Произошла ошибка при отправке изображения в чат бота.")

        # Проверяем ответ пользователя на валидность капчи
        def find_error(self):
            self.capcha_error = True
            print("Капча не принята. Делаем повторный скриншот капчи.")
            time.sleep(2)
            self.browser.find_element(By.ID, 'yw0').screenshot('capcha_screen.png')
            self.browser.save_screenshot('screen_display.png')
            time.sleep(2)
            print("Отправляем капчу.")
            self.send_image_to_bot()

        # Загрузка файла на сайт
        def upload_file(self, file_path):
            self.browser.switch_to.frame("cke_200_fileInput")
            print("Перешли на iframe окна для загрузки файлов.")
            file_input = self.browser.find_element(By.CSS_SELECTOR, "input[type='file'][id='cke_200_fileInput_input']")
            file_input.send_keys(file_path)
            print("Файл загружен на сервер.")
            time.sleep(3)
            self.browser.switch_to.default_content()
            print("Произошел переход на основной экран.")
            time.sleep(3)
            self.browser.find_element(By.ID, 'cke_202_label').click()
            print("Произошел клик на загрузку файла.")
            time.sleep(10)

            # Проверка на всплывающее окно Alert
            try:
                alert_obj = self.browser.switch_to.alert
                print("Обнаружено всплывающее окно Alert.")
                time.sleep(3)
                alert_obj.accept()  # Принять (нажать "ОК") на всплывающем окне
                time.sleep(5)
                print("Окно закрыто.")
            except NoAlertPresentException:
                print("Alert не найден.")
            print("Начинается удаление файла.")
            self.delete_file(file_path)
            # удаляем файл
            self.answer_next_step = 'start'
            print('answer_next_step = "start"')

        # Удаляет использованные файлы
        @staticmethod
        def delete_file(file_path):
            if os.path.exists(file_path):
                os.remove(file_path)
                print(f"Файл {file_path} успешно удален.")
            else:
                print(f"Файл {file_path} не существует.")

        # Создаёт и добавляет файлы в архив
        def add_to_zip(self, file_to_add):
            del_file_path = os.path.join('.', self.name_file_zip)
            arcname = os.path.basename(file_to_add)
            if os.path.exists(self.file_zip_path) and os.path.isfile(self.file_zip_path) and self.file_zip_path.endswith('.rar'):
                with zipfile.ZipFile(self.file_zip_path, 'a') as zipf:
                    zipf.write(file_to_add, arcname=arcname)
                    print("Файл добавлен в архив.")
                    time.sleep(5)
            else:
                with zipfile.ZipFile(self.file_zip_path, 'w') as zipf:
                    zipf.write(file_to_add, arcname=arcname)
                    print("Файл добавлен в архив.")
                    time.sleep(5)

            self.delete_file(del_file_path)

    except Exception as ex:
        print(ex)

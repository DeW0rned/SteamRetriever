from chrome_driver_base import ChromeDriverBase
from sda_controller import SdaController
from firstmail import Firstmail
from loguru import logger
import os
import logging


class SteamRetriever(ChromeDriverBase, SdaController, Firstmail):
    def __init__(
            self,
            account_path: str,
            templates_path: str,
            screenshot_path: str,
            emails_path: str,
            output_path: str,
            firstmail_api_key: str
    ):
        """
        Основной класс ретривера

        :param account_path: путь к аккаунтам
        :param templates_path: путь к тимплейтам для sda controller
        :param screenshot_path: путь к скриншоту для sda controller
        """

        ChromeDriverBase.__init__(self)
        SdaController.__init__(self, templates_path, screenshot_path)
        Firstmail.__init__(self, api_key=firstmail_api_key)

        self._accounts_path = account_path
        self._emails_path = emails_path
        self._output_path = output_path
        self._current_account = None

    def _show_log(self, text):
        """
        Логгирует от лица имени аккаунта

        :param text: текст лога
        """

        logger.info(f'{self._current_account}: {text}')

    def _get_accounts(self) -> dict:
        """
        Получение аккаунтов в виде словаря

        :return: dict из названий аккаунтов в виде ключа и данных в виде значения
        """

        accounts_files = [
            file for file in os.listdir(self._accounts_path)
            if file.endswith('.maFile') or file.endswith('.txt')
        ]
        accounts = {}

        for account_file in accounts_files:
            account_name = account_file.split('.')[0]

            if account_name not in accounts:
                accounts[account_name] = {}

            if account_file.endswith('.maFile'):
                accounts[account_name]['maFile'] = f'{os.getcwd()}/{self._accounts_path}/{account_file}'

            elif account_file.endswith('.txt'):
                with open(f'{self._accounts_path}/{account_file}', 'r', encoding='utf-8') as file:
                    file_text = file.read()

                login = file_text.split(':')[0]
                password = file_text.split(':')[1].rstrip()

                accounts[account_name]['txt'] = f'{os.getcwd()}/{self._accounts_path}/{account_file}'
                accounts[account_name]['login'] = login
                accounts[account_name]['password'] = password


        return accounts

    def _get_emails(self) -> list:
        """
        Получение почт из файла

        :return: массив из почт
        """

        with open(self._emails_path, 'r', encoding='utf-8') as file:
            emails = [email.rstrip() for email in file.readlines()]

        return emails

    def _remove_account(self, account_name: str, accounts: dict):
        """
        Удаление аккаунта из папки аккаунтов

        :param account_name: имя аккаунта
        """

        for format_ in ['txt', 'maFile']:
            os.remove(accounts[account_name][format_])

    def _remove_first_email(self, emails: list) -> list:
        """
        Удаление email из файла

        :param email: почта
        :return: новый список почт без первой
        """

        with open(self._emails_path, 'w', encoding='utf-8') as file:
            file.write('\n'.join(email for email in emails[1:]))

        return emails[1:]

    def _sign_in_account(self, login: str, password: str):
        """
        Войти в аккаунт в steam

        :param login: логин
        :param password: пароль
        """

        self._enter_text(
            xpath='//*[@id="responsive_page_template_content"]/div[3]/div[1]/div/div/div/div[2]/div/form/div[1]/input',
            text=login
        )
        self._enter_text(
            xpath='//*[@id="responsive_page_template_content"]/div[3]/div[1]/div/div/div/div[2]/div/form/div[2]/input',
            text=password
        )
        self._click_element(
            xpath='//*[@id="responsive_page_template_content"]/div[3]/div[1]/div/div/div/div[2]/div/form/div[4]/button'
        )

        current_code = self._get_sda_code()
        code_xpaths = [
            '//*[@id="responsive_page_template_content"]/div[3]/div[1]/div/div/div/div[2]/form/div/div[2]/div[1]/div/input[1]',
            '//*[@id="responsive_page_template_content"]/div[3]/div[1]/div/div/div/div[2]/form/div/div[2]/div[1]/div/input[2]',
            '//*[@id="responsive_page_template_content"]/div[3]/div[1]/div/div/div/div[2]/form/div/div[2]/div[1]/div/input[3]',
            '//*[@id="responsive_page_template_content"]/div[3]/div[1]/div/div/div/div[2]/form/div/div[2]/div[1]/div/input[4]',
            '//*[@id="responsive_page_template_content"]/div[3]/div[1]/div/div/div/div[2]/form/div/div[2]/div[1]/div/input[5]'
        ]

        for char, xpath in zip(list(current_code), code_xpaths):
            self._enter_text(
                xpath=xpath,
                text=char
            )

        self._wait_element(
            xpath='//*[@id="account_pulldown"]'
        )

    def _change_email(self, password: str, email: str, email_password: str):
        """
        Изменение почты аккаунта

        :param password: пароль
        :param email: почта
        :param email_password: пароль от почты
        """

        self._follow_link(url='https://store.steampowered.com/account/')
        self._click_element(
            xpath='//*[@id="main_content"]/div[2]/div[4]/div[1]/div[3]/a'
        )
        self._click_element(
            xpath='//*[@id="wizard_contents"]/div/a[2]'
        )
        self._accept_sda_confirmation()
        self._click_element(
            xpath='//*[@id="wizard_contents"]/div/a[3]'
        )
        self._enter_text(
            xpath='//*[@id="verify_password"]',
            text=password
        )
        self._click_element(
            xpath='// *[ @ id = "verify_password_submit"] / input'
        )
        self._enter_text(
            xpath='//*[@id="email_reset"]',
            text=email
        )
        self._click_element(
            xpath='//*[@id="change_email_area"]/input'
        )
        email_code = self._get_email_code(
            email=email,
            password=email_password
        )
        self._enter_text(
            xpath='//*[@id="email_change_code"]',
            text=email_code
        )
        self._click_element(
            xpath='//*[@id="confirm_email_form"]/div[2]/input'
        )
        self._wait_element(
            xpath='//*[@id="wizard_contents"]/div/div[2]/a'
        )

    def _remove_number(self, email: str, email_password: str):
        """
        Удаление номера с аккаунта

        :param email: почта
        :param email_password: пароль от почты
        """

        self._follow_link(url='https://store.steampowered.com/phone/manage')
        self._click_element(
            xpath='//*[@id="responsive_page_template_content"]/div[4]/div/div[2]/div[4]/div[2]/a'
        )
        self._click_element(
            xpath='//*[@id="wizard_contents"]/div/a[2]'
        )
        self._accept_sda_confirmation()
        self._click_element(
            xpath='//*[@id="wizard_contents"]/div/a[2]'
        )

        email_code = self._get_email_code(
            email=email,
            password=email_password
        )
        self._enter_text(
            xpath='//*[@id="forgot_login_code"]',
            text=email_code
        )
        self._click_element(
            xpath='//*[@id="forgot_login_code_form"]/div[3]/input'
        )
        self._click_element(
            xpath='//*[@id="reset_phonenumber_form"]/div[2]/input'
        )
        self._wait_element(
            xpath='//*[@id="responsive_page_template_content"]/div[3]/div/h2'
        )

    def _logout_account(self):
        """
        Выход из аккаунта
        """

        self._click_element(
            xpath='//*[@id="account_pulldown"]'
        )
        self._click_element(
            xpath='//*[@id="account_dropdown"]/div/a[4]'
        )
        self._wait_element(
            xpath='//*[@id="global_action_menu"]/a[2]'
        )

    def _add_account_2_output(
        self,
        login: str,
        password: str,
        email: str,
        email_password: str
    ):
        """
        Добавление данных аккаунта в файл вывода

        :param login: логин steam
        :param password: пароль steam
        :param email: email
        :param email_password: пароль от email
        """
        with open(self._output_path, 'a', encoding='utf-8') as file:
            file.write(f'\n{login}:{password}:{email}:{email_password}')

    def retrieve_processing(self):
        """
        Основной цикл отработки аккаунтов
        """

        try:
            accounts = self._get_accounts()
            emails = self._get_emails()

            for account_name, account_data in accounts.items():
                self._current_account = account_name

                self._show_log('импортируем аккаунт в SDA')
                self._import_sda_account(
                    mafile_path=account_data['maFile'],
                    password=account_data['password']
                )

                self._show_log('входим в аккаунт')
                self._follow_link(url='https://store.steampowered.com/login/')
                self._sign_in_account(
                    login=account_data['login'],
                    password=account_data['password']
                )

                email_data = emails[0]
                email = email_data.split(':')[0]
                email_password = email_data.split(':')[1]

                self._show_log(f'меняем email на {email}')
                self._change_email(
                    password=account_data['password'],
                    email=email,
                    email_password=email_password
                )

                self._show_log('удаляем номер телефона')
                self._remove_number(
                    email=email,
                    email_password=email_password
                )

                self._show_log(f'сохраняем данные')
                self._add_account_2_output(
                    login=account_data['login'],
                    password=account_data['password'],
                    email=email,
                    email_password=email_password
                )

                self._show_log('удаляем аккаунт, почту и выходим из аккаунта')
                emails = self._remove_first_email(emails=emails)
                self._remove_account(account_name=account_name, accounts=accounts)
                self._remove_sda_account()
                self._logout_account()

        except Exception as ex:
            logger.error('Произошла ошибка, посмотрите файл logs.log')
            logging.exception(ex)

        finally:
            self._driver.quit()

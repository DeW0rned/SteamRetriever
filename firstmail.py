import requests
import time
import re


class Firstmail:
    def __init__(self, api_key: str):
        """
        Запросы к firstmail для получения кодов

        :param api_key: апи ключ от firstmail
        """

        self._session = requests.session()
        self._session.headers.update(
            {
                'X-API-KEY': api_key
            }
        )
        self._last_codes = []

    def _get_email_code(self, email: str, password: str) -> str:
        """
        Получение последнего кода

        :param email: почта
        :param password: пароль от почты
        :return: код
        """

        params = {
            'username': email,
            'password': password
        }

        while True:
            try:
                response = self._session.get(
                    url='https://api.firstmail.ltd/v1/mail/one',
                    params=params
                ).json()

                try:
                    code = response['text'].split(
                        'Код подтверждения вашего аккаунта:'
                    )[1]
                except IndexError:
                    code = response['text'].split(
                        'Код подтверждения, необходимый для\r\nизменения адреса эл. почты:'
                    )[1]

                code = re.sub('\s+', '', code)[:5]

                if code not in self._last_codes:
                    self._last_codes.append(code)
                    return code

            except Exception as ex:
                continue

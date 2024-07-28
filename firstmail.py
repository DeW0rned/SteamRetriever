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
        code = ''

        while not code:
            response = self._session.get(
                url='https://api.firstmail.ltd/v1/market/get/message',
                params=params
            ).json()

            try:
                code = re.findall(r'[A-Z0-9]{5}', response['message'])[6]
                return code
            except Exception as ex:
                time.sleep(1)
                continue

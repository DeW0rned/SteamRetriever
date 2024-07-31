import re

text = "\r\nЗдравствуйте, bomba13334.\r\n\r\nКод для смены пароля вашего аккаунта Steam:\r\n\r\nКод подтверждения вашего аккаунта:    97TPB\r\n\r\nЕсли вы не"
code = text.split('Код подтверждения вашего аккаунта:')[1]
code = code = re.sub('\s+', '', code)[:5]


print(code)
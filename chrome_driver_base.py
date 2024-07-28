from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import undetected_chromedriver as uc
import os
import shutil


class CustomChromeDriver(uc.Chrome):
    def quit(self):
        """
        Переопределение метода quit в Chrome для корректного выхода
        """

        try:
            self.service.process.kill()
        except (AttributeError, RuntimeError, OSError):
            pass

        try:
            self.reactor.event.set()
        except AttributeError:
            pass

        try:
            os.kill(self.browser_pid, 15)
        except Exception as e:  # noqa
            pass

        if (
                hasattr(self, "keep_user_data_dir")
                and hasattr(self, "user_data_dir")
                and not self.keep_user_data_dir
        ):
            for _ in range(5):
                try:
                    shutil.rmtree(self.user_data_dir, ignore_errors=False)
                except FileNotFoundError:
                    pass
                except (RuntimeError, OSError, PermissionError) as e:
                    pass
                else:
                    break

        self.patcher = None


class ChromeDriverBase:
    def __init__(self):
        """
        Класс работает с методами selenium
        """

        driver_options = webdriver.ChromeOptions()
        option_args = ['--disable-images']

        for arg in option_args:
            driver_options.add_argument(arg)

        self._driver = CustomChromeDriver(options=driver_options)
        self._driver.implicitly_wait(50)

    def _follow_link(self, url: str):
        """
        Переходит по ссылке

        :param url: ссылка
        """

        self._driver.get(url)

    def _enter_text(self, xpath: str, text: str):
        """
        Ввод текста в элемент(поле)

        :param xpath: xpath элемента
        :param text: вводимый тектс
        """

        input_element = self._driver.find_element(By.XPATH, xpath)
        input_element.send_keys(text)

    def _click_element(self, xpath: str):
        """
        Нажатие на элемент

        :param xpath: xpath элемента
        :return:
        """

        element = self._driver.find_element(By.XPATH, xpath)
        element.click()

    def _wait_element(self, xpath: str, visibility: bool = True):
        """
        Ожидание появления элемента

        :param xpath: xpath элемента
        """

        WebDriverWait(self._driver, 15).until(
            EC.presence_of_element_located((By.XPATH, xpath)) if visibility
            else EC.invisibility_of_element((By.XPATH, xpath))
        )


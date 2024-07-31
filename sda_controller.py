from types import FunctionType
from loguru import logger
import pyautogui as pg
import pyscreenshot
import cv2 as cv
import numpy as np
import win32clipboard
import win32con
import win32gui
import time


class SdaController:
    def __init__(self, templates_path: str, screenshot_path: str):
        """
        Класс отвечает за управление SDA

        :param templates_path: путь к директории с тимлейтами
        """

        self._templates_path = templates_path
        self._screenshot_path = screenshot_path

    @staticmethod
    def _find_window_by_title(title):
        def enum_windows_callback(hwnd, results):
            window_text = win32gui.GetWindowText(hwnd)

            if title in window_text:
                results.append(hwnd)

        windows = []
        win32gui.EnumWindows(enum_windows_callback, windows)

        return windows

    def _update_screenshot(self):
        """
        Обновление скриншота
        """

        screenshot = pyscreenshot.grab()
        screenshot.save(self._screenshot_path)

    def _find_template_location(self, template_path: str, offsets: tuple) -> list:
        """
        Поиск элемента на скрине

        :param template_path: тимплейт искомого элемента
        :param offsets: смещения(в процентах)
        :return: список координат
        """

        current_attempt = 0

        while current_attempt < 5:
            current_attempt += 1

            self._update_screenshot()

            screenshot_rgb = cv.imread(self._screenshot_path)
            screenshot_gray = cv.cvtColor(screenshot_rgb, cv.COLOR_BGR2GRAY)
            template = cv.imread(template_path, 0)

            matching_result = cv.matchTemplate(
                screenshot_gray,
                template,
                cv.TM_CCOEFF_NORMED
            )
            result_location = np.where(matching_result >= 0.8)
            template_locations = [list(pt) for pt in zip(*result_location[::-1])]

            if not template_locations:
                logger.error(f'Невозможно найти элемент: {template_path},\nпопытка: {current_attempt}')
                time.sleep(2)
                continue

            template_w, template_h = template.shape[::-1]
            template_locations[0][0] += template_w * offsets[0]
            template_locations[0][1] += template_h * offsets[1]

            return template_locations[0]

        raise ValueError('Не удалось найти элемент!')

    def _import_sda_account(self, mafile_path: str, password: str):
        """
        Метод импортирует аккаунт с помощью mafile

        :param mafile_path: путь к mafile
        :param password: пароль от аккаунта
        """

        mafile_filename = mafile_path.split('/')[-1]
        mafile_dir = '/'.join(mafile_path.split('/')[:-1])
        templates = {
            'import_account': f'{self._templates_path}/import_account.png',
            'searching_field': f'{self._templates_path}/searching_field.png',
            'filename_field': f'{self._templates_path}/filename_field.png',
            'password_field': f'{self._templates_path}/password_field.png',
            'login_button': f'{self._templates_path}/login_button.png'
        }

        import_account_x, import_account_y = self._find_template_location(
            template_path=templates['import_account'],
            offsets=(0.5, 0.5)
        )
        pg.click(import_account_x, import_account_y)

        searching_field_x, searching_field_y = self._find_template_location(
            template_path=templates['searching_field'],
            offsets=(0.2, 0.5)
        )
        pg.click(searching_field_x, searching_field_y)
        pg.write(mafile_dir)
        pg.press('enter')

        filename_field_x, filename_field_y = self._find_template_location(
            template_path=templates['filename_field'],
            offsets=(0.4, 0.5)
        )
        pg.click(filename_field_x, filename_field_y)
        pg.write(mafile_filename)
        pg.press('enter')

        password_field_x, password_field_y = self._find_template_location(
            template_path=templates['password_field'],
            offsets=(0.5, 0.25)
        )
        pg.click(password_field_x, password_field_y)
        pg.write(password)
        pg.press('enter')

        login_button_x, login_button_y = self._find_template_location(
            template_path=templates['login_button'],
            offsets=(0.5, 0.5)
        )
        pg.click(login_button_x, login_button_y)

        account_imported = False

        while not account_imported:
            time.sleep(1)

            password_windows = self._find_window_by_title('Enter a password')

            if not password_windows:
                account_imported = True

    def _remove_sda_account(self):
        """
        Удаление аккаунта из SDA
        """

        templates = {
            'account_panel': f'{self._templates_path}/account_panel.png'
        }

        account_panel_x, account_panel_y = self._find_template_location(
            template_path=templates['account_panel'],
            offsets=(0.1, 0.5)
        )
        pg.click(account_panel_x, account_panel_y, button='right')
        pg.click(account_panel_x+10, account_panel_y+50)

    def _get_sda_code(self) -> str:
        """
        Получение кода SDA

        :return: код в виде строки
        """

        templates = {
            'copy_button': f'{self._templates_path}/copy_button.png'
        }

        copy_button_x, copy_button_y = self._find_template_location(
            template_path=templates['copy_button'],
            offsets=(0.5, 0.5)
        )

        last_code = None

        while True:
            time.sleep(0.5)

            pg.click(copy_button_x, copy_button_y)

            win32clipboard.OpenClipboard()
            clipboard_text = win32clipboard.GetClipboardData()
            win32clipboard.CloseClipboard()

            if last_code is None:
                last_code = clipboard_text
                continue

            if clipboard_text != last_code:
                break

            last_code = clipboard_text

        return clipboard_text

    def _accept_sda_confirmation(self):
        """
        Подтвержение запроса на аккаунте
        """

        templates = {
            'account_panel': f'{self._templates_path}/account_panel.png',
            'confirmation_panel': f'{self._templates_path}/confirmation_panel.png'
        }

        account_panel_x, account_panel_y = self._find_template_location(
            template_path=templates['account_panel'],
            offsets=(0.5, 0.5)
        )
        pg.doubleClick(account_panel_x, account_panel_y)

        time.sleep(0.5)

        confirmation_panel_x, confirmation_panel_y = self._find_template_location(
            template_path=templates['confirmation_panel'],
            offsets=(0.75, 0.5)
        )
        pg.click(confirmation_panel_x, confirmation_panel_y)

        confirmations_handle = win32gui.FindWindow(None, 'Confirmations')
        win32gui.PostMessage(confirmations_handle, win32con.WM_CLOSE, 0, 0)

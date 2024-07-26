from sda_controller import SdaController
import time


def main():
    sda_controller = SdaController(
        templates_path='data/templates/',
        screenshot_path='data/screen.png'
    )
    # sda_controller.import_account(
    #     mafile_path='D:/lolz/steam_accounts/21jvYqYl2d.maFile',
    #     password='|S_3kb1EaY|'
    # )
    #code = sda_controller.get_code()
    #print(code)
    #sda_controller.accept_confirmation()



if __name__ == '__main__':
    main()

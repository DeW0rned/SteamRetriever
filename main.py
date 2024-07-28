from steam_retriever import SteamRetriever
import logging
import configparser


def main():
    config = configparser.ConfigParser()
    config.read('config.ini')
    firstmail_api_key = config.get('GENERAL', 'FIRSTMAIL_API_KEY')

    logging.basicConfig(
        level=logging.INFO,
        filename='logs.log',
        filemode='w'
    )

    steam_retriever = SteamRetriever(
        account_path='data/accounts/',
        templates_path='data/sda_templates/',
        screenshot_path='data/screen.png',
        emails_path='data/emails.txt',
        output_path='data/output.txt',
        firstmail_api_key=firstmail_api_key
    )
    steam_retriever.retrieve_processing()


if __name__ == '__main__':
    main()

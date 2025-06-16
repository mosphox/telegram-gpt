import os

from dotenv import load_dotenv

from telegram_gpt import TelegramBot


load_dotenv()

TELEGRAM_API_KEY = os.getenv('TELEGRAM_API_KEY')


if __name__ == '__main__':
    bot = TelegramBot(token=TELEGRAM_API_KEY)
    bot.run()

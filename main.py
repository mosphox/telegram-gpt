import logging
import os

from dotenv import load_dotenv

from telegram_gpt.logger import Logger
from telegram_gpt.plugs import GPTPlug, SettingsPlug, PromptPlug
from telegram_gpt.telegram import TelegramBot


# Load environment variables from .env file
load_dotenv()

# API keys
TELEGRAM_API_KEY = os.getenv('TELEGRAM_API_KEY')
GROQ_API_KEY = os.getenv('GROQ_API_KEY')

# Configuration file paths
settings = "settings.yaml"
prompt = "prompt.txt"

if __name__ == '__main__':
    # Set up logging
    logger = Logger(level=logging.INFO)

    # Validate critical environment variables
    if not TELEGRAM_API_KEY or not GROQ_API_KEY:
        logger.error(
            module='Main',
            scope='Check .env',
            message="Missing TELEGRAM_API_KEY or GROQ_API_KEY. Check your .env file."
        )
        raise SystemExit("Environment variables missing. Aborting.")

    # Initialize plugs
    gptplug = GPTPlug(logger=logger, token=GROQ_API_KEY)
    settingsplug = SettingsPlug(logger=logger, filepath=settings).load(settings)
    promptplug = PromptPlug(logger=logger, filepath=prompt).load(prompt)

    # Start the bot
    bot = TelegramBot(
        logger=logger,
        token=TELEGRAM_API_KEY,
        gptplug=gptplug,
        settingsplug=settingsplug,
        promptplug=promptplug
    )

    bot.run()

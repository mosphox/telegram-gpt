import logging
import os

from dotenv import load_dotenv

from constants import MODELS_LIST
from structures import Model


load_dotenv()

GROQ_API_KEY = os.getenv('GROQ_API_KEY')


class GPTPlug:
    def __init__(self, logger: logging.Logger):
        self.logger = logger

    def list_models(self) -> list[Model]:
        self.logger.set(module='GPT Plug', scope='List models')

        headers = {"Authorization" : f"Bearer {GROQ_API_KEY}"}
        response = requests.get(MODELS_LIST, headers=headers)

        if response.status_code != 200:
            self.logger.warning(message=f"Response code '{response.status_code}' from groq API")
            return []

        else:
            self.logger.debug(message="Fetched models list from groq API")

        data = response.json().get('data')

        if not data or not isinstance(data, list) or not all(isinstance(item, dict) for item in data):
            self.logger.warning(message="Failed to parse response from groq API")
            return []

        models = [
            Model(
                model_id=model.get('id'),
                created=model.get('created'),
                owned_by=model.get('owned_by'),
                context_window=model.get('context_window'),
                max_completion_tokens=model.get('max_completion_tokens')
            )

            for model in data if model.get('active')
        ]

        return [model for model in models if model.clean_and_validate(logger=self.logger)]

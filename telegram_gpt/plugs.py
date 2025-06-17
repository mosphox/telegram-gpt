import os
import requests
from typing import Self

from groq import Groq

from telegram_gpt.constants import MODELS_LIST, DEFAULT_MODEL, DEFAULT_PROMPT
from telegram_gpt.logger import Logger
from telegram_gpt.structures import Model, Settings, Prompt


class Plug:
    """
    Base class for all plug components.

    Handles common fields such as logger and config filepath.
    """
    module = 'Plug'

    def __init__(self, logger: Logger, filepath: str = None):
        self.logger = logger
        self.filepath = filepath


class GPTPlug(Plug):
    """
    Handles Groq API interactions: model listing and chat completions.
    """
    module = 'GPT Plug'

    def __init__(self, logger: Logger, token: str):
        super().__init__(logger=logger)
        self.token = token

        self.models_list()

    def models_list(self) -> list[Model]:
        """
        Fetch the list of available models from Groq API and return validated Model objects.

        Returns:
            list[Model]: A list of usable model instances.
        """
        scope = 'List models'

        headers = {"Authorization": f"Bearer {self.token}"}
        response = requests.get(MODELS_LIST, headers=headers)

        if response.status_code != 200:
            self.logger.warning(
                module=self.module,
                scope=scope,
                message=f"Response code '{response.status_code}' from groq API"
            )

            return []

        self.logger.debug(
            module=self.module,
            scope=scope,
            message="Fetched models list from groq API"
        )

        data = response.json().get('data')

        if not data or not isinstance(data, list) or not all(isinstance(item, dict) for item in data):
            self.logger.warning(
                module=self.module,
                scope=scope,
                message="Failed to parse response from groq API"
            )

            return []

        models = [
            Model(
                model=model.get('id'),
                created=model.get('created'),
                owned_by=model.get('owned_by'),
                context_window=model.get('context_window'),
                max_completion_tokens=model.get('max_completion_tokens')
            )

            for model in data if model.get('active')
        ]

        self.models = [model for model in models if model.clean_and_validate(logger=self.logger)]
        return self.models

    def connect(self) -> Groq:
        """
        Initialize or return an existing Groq client.

        Returns:
            Groq: A connected Groq client instance.
        """
        return self.client if hasattr(self, 'client') else Groq(api_key=self.token)

    def chat(self, query: str, settings: Settings, prompt: Prompt) -> tuple[bool, str | None]:
        """
        Perform a chat completion using Groq API.

        Args:
            query (str): The user prompt.
            settings (Settings): Model and generation parameters.
            prompt (Prompt): System prompt.

        Returns:
            tuple[bool, str | None]: (success status, response text or None)
        """
        self.client = self.connect()

        try:
            chat = self.client.chat.completions.create(
                messages=[
                    {"role": "system", "content": prompt.text},
                    {"role": "user", "content": query},
                ],

                model=settings.model,
                temperature=settings.temperature,
                frequency_penalty=settings.frequency_penalty,
                presence_penalty=settings.presence_penalty,
                top_p=settings.top_p,
            )

            return True, chat.choices[0].message.content.strip()

        except Exception as e:
            self.logger.warning(
                module=self.module,
                scope='Chat',
                message="Unable to connect to groq API or API returned an error"
            )

            return False, None


class PropertyPlug(Plug):
    """
    Abstract base for pluggable config structures like Settings or Prompt.

    Provides loading, updating, saving, and resetting support.
    """
    def load(self, filepath: str | None = None) -> Self:
        """
        Load configuration from file or fall back to defaults.

        Args:
            filepath (str | None): Optional path override.

        Returns:
            Self: The initialized PropertyPlug.
        """
        successfull, configuration = self.structure.load(filepath or self.filepath)
        self.configuration = configuration if successfull else self.structure(self.default)
        return self

    def update(self, **kwargs):
        """
        Update configuration with given keyword args and persist to file.

        Returns:
            dict: Mapping of updated fields to success status.
        """
        response = self.configuration.update(logger=self.logger, **kwargs)
        self.configuration.save(self.filepath)
        return response

    def preset(self) -> None:
        """
        Reset configuration to default values and save.
        """
        self.configuration = self.structure(self.default)
        self.configuration.save(self.filepath)


class SettingsPlug(PropertyPlug):
    """
    Plug for managing Settings structure with dynamic model validation.
    """
    module = 'Settings Plug'
    structure = Settings
    default = DEFAULT_MODEL


class PromptPlug(PropertyPlug):
    """
    Plug for managing Prompt structure and file persistence.
    """
    module = 'Prompt Plug'
    structure = Prompt
    default = DEFAULT_PROMPT

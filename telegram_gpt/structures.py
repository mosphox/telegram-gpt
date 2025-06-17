from dataclasses import dataclass, asdict
import logging
import time
from typing import Self

import yaml

from telegram_gpt.logger import Logger
from telegram_gpt.validators import Validators


@dataclass
class Model:
    """
    Represents metadata about a language model.
    """
    model: str
    created: int | None = None
    owned_by: str | None = None
    context_window: int | None = None
    max_completion_tokens: int | None = None

    module = 'Model'

    @staticmethod
    def _log(logger: Logger, field: str, value: int | float) -> None:
        """
        Log invalid value for a specific field.
        """
        logger.debug(
            module=Model.module,
            scope=f'Validate {field}',
            message=f"Invalid value: '{value}'"
        )

    def clean_and_validate(self, logger: Logger) -> bool:
        """
        Validate and sanitize the model metadata.

        Converts valid timestamps and drops invalid values.
        Logs issues using the provided logger.
        """
        if not Validators.validate_str(value=self.model):
            logger.warning(
                module=self.module,
                scope='Validate id',
                message=f"Expected string for model, got '{type(self.model)}'"
            )

            return False

        if Validators.validate_range(margins=(0, time.time()), value=self.created):
            self.created = self._to_datestring(self.created)
        else:
            self._log(logger, 'created', self.created)
            self.created = None

        if not Validators.validate_str(value=self.owned_by):
            self._log(logger, 'owned_by', self.owned_by)
            self.owned_by = None

        if not Validators.validate_range((0, 1024 * 1024), self.context_window):
            self._log(logger, 'context_window', self.context_window)
            self.context_window = None

        if not Validators.validate_range((0, 1024 * 1024), self.max_completion_tokens):
            self._log(logger, 'max_completion_tokens', self.max_completion_tokens)
            self.max_completion_tokens = None

        return True

    @staticmethod
    def _to_datestring(timestamp: int) -> str:
        """
        Convert a UNIX timestamp into a human-readable date.
        """
        return time.strftime('%d/%m/%Y', time.localtime(timestamp))


@dataclass
class Settings:
    """
    Holds and manages configuration for model inference parameters.
    """
    model: str
    temperature: float = 1.0
    frequency_penalty: float = 0.0
    presence_penalty: float = 0.0
    top_p: float = 1.0

    module = 'Settings'

    def _update_model(self, logger: Logger, value: str, onloading: bool = False) -> bool:
        """
        Validate and optionally set model name.
        """
        if not Validators.validate_str(value=value):
            logger.warning(
                module=self.module,
                scope='Validate model_id',
                message=f"Expected model as string instance, got '{type(value)}'"
            )

            return False

        if onloading:
            logger.debug(
                module=self.module,
                scope='Validation',
                message="Settings configuration is valid"
            )

        else:
            self.model = value

        return True

    def _validate_range(self, logger: Logger, margins: tuple[int | float, int | float],
                        value: int | float, default: int | float, varname: str) -> tuple[bool, int | float]:
        """
        Validate that a value is within a given range.
        """
        if not Validators.validate_range(margins, value):
            logger.debug(
                module=self.module,
                scope='Validate range',
                message=f"Invalid value in {varname} field: '{value}'"
            )

            return False, default

        return True, value

    def _update_temperature(self, logger: Logger, value: int | float) -> bool:
        return self._validate_and_assign(logger, value, 'temperature', (0.0, 2.0), 1.0)

    def _update_frequency(self, logger: Logger, value: int | float) -> bool:
        return self._validate_and_assign(logger, value, 'frequency_penalty', (-2.0, 2.0), 0.0)

    def _update_presence(self, logger: Logger, value: int | float) -> bool:
        return self._validate_and_assign(logger, value, 'presence_penalty', (-2.0, 2.0), 0.0)

    def _update_top(self, logger: Logger, value: int | float) -> bool:
        return self._validate_and_assign(logger, value, 'top_p', (0.0, 1.0), 1.0)

    def _validate_and_assign(self, logger: Logger, value: float, attr: str,
                             bounds: tuple[float, float], default: float) -> bool:
        """
        Internal helper to validate and set an attribute value.
        """
        status, result = self._validate_range(logger, bounds, value, default, attr)
        setattr(self, attr, result)

        return status

    def clean_and_validate(self, logger: Logger) -> bool:
        """
        Validate all fields in settings and log any invalid entries.
        """
        self._update_temperature(logger, self.temperature)
        self._update_frequency(logger, self.frequency_penalty)
        self._update_presence(logger, self.presence_penalty)
        self._update_top(logger, self.top_p)

        return self._update_model(logger, self.model, onloading=True)

    def update(self, logger: Logger, **kwargs) -> dict[str, tuple[bool, str | float]]:
        """
        Dynamically update one or more fields in the settings.

        Returns:
            dict[str, tuple[bool, value]]: Map of update status per field.
        """
        response = {}

        for attribute, value in kwargs.items():
            if attribute == 'models':
                continue

            if attribute != 'model':
                if Validators.validate_numeric(value):
                    value = round(float(value), 2)
                    method = getattr(self, f'_update_{attribute}', None)
                    if method:
                        response[attribute] = (method(logger, value), value)

                else:
                    logger.debug(
                        module=self.module,
                        scope='Validate numeric',
                        message=f"Numeric value is required for '{attribute}', got '{value}'"
                    )

                    response[attribute] = (False, value)

            else:
                models = [model.model for model in kwargs.get('models', [])]

                if not models or value in models:
                    response['model'] = (self._update_model(logger, value), value)

                else:
                    logger.debug(
                        module=self.module,
                        scope='Validate model',
                        message=f"Unable to find model '{value}'"
                    )

                    response['model'] = (False, value)

        return response

    @staticmethod
    def load(yamlfile: str) -> tuple[bool, Self | Exception]:
        """
        Load settings from a YAML file.
        """
        try:
            with open(yamlfile, 'r', encoding='utf-8') as f:
                return True, Settings(**yaml.safe_load(f))

        except Exception as e:
            return False, e

    def save(self, yamlfile: str) -> tuple[bool, None | Exception]:
        """
        Save settings to a YAML file.
        """
        try:
            with open(yamlfile, 'w', encoding='utf-8') as f:
                yaml.dump(asdict(self), f)
                return True, None

        except Exception as e:
            return False, e


@dataclass
class Prompt:
    """
    Stores and manages the system prompt used in LLM interactions.
    """
    text: str

    module = 'Prompt'

    def _update_text(self, logger: Logger, value: str, onloading: bool = False) -> bool:
        """
        Update the system prompt after validating the input.
        """
        if not Validators.validate_str(value):
            logger.warning(
                module=self.module,
                scope='Validate prompt',
                message=f"Expected prompt as string instance, got '{type(value)}'"
            )

            return False

        if onloading:
            logger.debug(
                module=self.module,
                scope='Validation',
                message="Prompt configuration is valid"
            )

        else:
            self.text = value

        return True

    def clean_and_validate(self, logger: Logger) -> bool:
        """
        Validate the current prompt value.
        """
        return self._update_text(logger, self.text, onloading=True)

    def update(self, logger: Logger, **kwargs) -> tuple[bool, str]:
        """
        Update the prompt with the first value from kwargs.
        """
        for _, value in kwargs.items():
            return self._update_text(logger, value), value

        return tuple()

    def reset(self) -> None:
        """
        Reset the prompt to an empty string.
        """
        self.text = ""

    @staticmethod
    def load(textfile: str) -> tuple[bool, Self | Exception]:
        """
        Load a prompt from a plain text file.
        """
        try:
            with open(textfile, 'r', encoding='utf-8') as f:
                return True, Prompt(text=f.read())

        except Exception as e:
            return False, e

    def save(self, textfile: str) -> tuple[bool, None | Exception]:
        """
        Save the current prompt to a text file.
        """
        try:
            with open(textfile, 'w', encoding='utf-8') as f:
                f.write(self.text)
                return True, None

        except Exception as e:
            return False, e

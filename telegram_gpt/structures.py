from dataclasses import dataclass, asdict
import logging
import time

from validators import Validators


@dataclass
class Model:
    model: str
    created: int | None = None
    owned_by: str | None = None
    context_window: int | None = None
    max_completion_tokens: int | None = None

    def clean_and_validate(self, logger: logging.Logger) -> bool:
        logger.set(module='Model structure', scope='Validation')

        if not Validators.validate_str(value=self.model):
            logger.warning(message=f"Expected string for model, got '{type(self.model)}'")
            return False

        if Validators.validate_range(margins=(0, time.time()), value=self.created):
            self.created = self._to_datestring(self.created)
        else:
            logger.debug(message=f"Invalid value in created field: '{self.created}'")
            self.created = None

        if not Validators.validate_str(value=self.owned_by):
            logger.debug(message=f"Invalid value in owned_by field: '{self.owned_by}'")
            self.owned_by = None

        if not Validators.validate_range(margins=(0, 1024 * 1024), value=self.context_window):
            logger.debug(message=f"Invalid value in context_window field: '{self.context_window}'")
            self.context_window = None

        if not Validators.validate_range(margins=(0, 1024 * 1024), value=self.max_completion_tokens):
            logger.debug(message=f"Invalid value in max_completion_tokens field: '{self.max_completion_tokens}'")
            self.max_completion_tokens = None

        return True


@dataclass
class Settings:
    model: str
    temperature: float = 1.0
    frequency_penalty: float = 0.0
    presence_penalty: float = 0.0
    top_p: float = 1.0

    def _update_model(self, logger: logging.Logger, value: str) -> bool:
        if not Validators.validate_str(value=value):
            logger.warning(message=f"Expected model as string instance, got '{type(value)}'")
            return False

        return True

    def _validate_range(self, logger: logging.Logger, margins: tuple[int | float, int | float],
                        value: int | float, default: int | float, varname: str) -> tuple[bool, int | float]:
        if not Validators.validate_range(margins=margins, value=value):
            logger.debug(message=f"Invalid value in {varname} field: '{value}'")
            return False, default

        return True, value

    def _update_temperature(self, logger: logging.Logger, value: int | float) -> bool:
        status, self.temperature = self._validate_range(
            logger=logger,
            margins=(0.0, 2.0),
            value=value,
            default=1.0,
            varname='temperature'
        )

        return status

    def _update_frequency_penalty(self, logger: logging.Logger, value: int | float) -> bool:
        status, self.frequency_penalty = self._validate_range(
            logger=logger,
            margins=(-2.0, 2.0),
            value=value,
            default=0.0,
            varname='frequency_penalty'
        )

        return status

    def _update_presence_penalty(self, logger: logging.Logger, value: int | float) -> bool:
        status, self.presence_penalty = self._validate_range(
            logger=logger,
            margins=(-2.0, 2.0),
            value=value,
            default=0.0,
            varname='presence_penalty'
        )

        return status

    def _update_top_p(self, logger: logging.Logger, value: int | float) -> bool:
        status, self.top_p = self._validate_range(
            logger=logger,
            margins=(0.0, 1.0),
            value=value,
            default=1.0,
            varname='top_p'
        )

        return status

    def clean_and_validate(self, logger: logging.Logger) -> bool:
        logger.set(module='Settings structure', scope='Validation')

        self._update_temperature(logger=logger, temperature=self.temperature)
        self._update_frequency_penalty(logger=logger, frequency_penalty=self.frequency_penalty)
        self._update_presence_penalty(logger=logger, presence_penalty=self.presence_penalty)
        self._update_top_p(logger=logger, top_p=self.top_p)

        return self._update_model(logger=logger, model=self.model)

    def update(self, logger: logging.Logger, **kwargs) -> tuple[bool, str]:
        return {key: (getattr(self, f'_update_{key}')(logger=logger, value=value), value)
                for key, value in kwargs.items() if hasattr(self, f'_update_{key}')}

    def dump(self) -> dict:
        return asdict(self)

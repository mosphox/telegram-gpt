import re

from telegram_gpt.constants import DOCS
from telegram_gpt.structures import Model, Settings, Prompt


def escape(value: str | None) -> str:
    """
    Escape special characters for Telegram MarkdownV2 formatting.

    Args:
        value (str | None): The string to escape.

    Returns:
        str: Escaped string or 'N/A' if None.
    """
    return re.sub(r'([_*[\]()~`>#+=|{}.!-])', r'\\\1', str(value)) if value is not None else "N/A"


class Formatters:
    """
    Collection of static formatters for bot responses in Telegram.
    Each method returns MarkdownV2-safe strings.
    """

    @staticmethod
    def models_help() -> str:
        """
        Returns usage help for /models command.

        Returns:
            str: Formatted help message.
        """
        return (
            "`/models usage`\n"
            "`Read the docs at`\n"
            f"`{DOCS}`\n\n"
            "`/models get`\n"
            "`/models list`\n"
            "`/models default`\n\n"
            "`/models set model <str>`\n"
            "`/models set temperature <float[0:2]>`\n"
            "`/models set frequency <float[-2:2]>`\n"
            "`/models set presence <float[-2:2]>`\n"
            "`/models set top <float[0:1]>`\n"
        )

    @staticmethod
    def models_list(models: list[Model]) -> str:
        """
        Format the list of models.

        Args:
            models (list[Model]): List of model objects.

        Returns:
            str: Formatted model info list or error message.
        """
        return "`Models`\n\n" + "\n".join(
            f"`{escape(model.model)}`\n"
            f"    `{escape(model.created)} \\- {escape(model.owned_by)} \\| "
            f"[{escape(model.context_window)} / {escape(model.max_completion_tokens)}]`\n"
            for model in models
        ) if models else "`Failed to fetch models`"

    @staticmethod
    def models_get(settings: Settings) -> str:
        """
        Format the current settings.

        Args:
            settings (Settings): Current configuration.

        Returns:
            str: MarkdownV2-formatted settings output.
        """
        return (
            "`Settings`\n\n"
            f"`model \\- {escape(settings.model)}`\n"
            f"`temperature \\- {escape(settings.temperature)}`\n"
            f"`frequency penalty \\- {escape(settings.frequency_penalty)}`\n"
            f"`presence penalty \\- {escape(settings.presence_penalty)}`\n"
            f"`top p \\- {escape(settings.top_p)}`\n"
        )

    @staticmethod
    def models_set(response: dict[str, tuple[bool, str | int | float]]) -> str:
        """
        Format result of /models set command.

        Args:
            response (dict): Field -> (success, value)

        Returns:
            str: MarkdownV2-formatted result for each field.
        """
        return "\n".join(
            f"`Attribute {key}`\n`Update {'successfull' if zipped[0] else 'failed'} \\- {escape(zipped[1])}`\n"
            for key, zipped in response.items()
        )

    @staticmethod
    def models_default() -> str:
        """
        Response for resetting to default settings.

        Returns:
            str: MarkdownV2-formatted confirmation.
        """
        return "`Default settings are set`"

    @staticmethod
    def prompt_help() -> str:
        """
        Help text for the /prompt command.

        Returns:
            str: MarkdownV2-formatted usage message.
        """
        return (
            "`/prompt usage`\n"
            "`Read the docs at`\n"
            f"`{DOCS}`\n\n"
            "`/prompt get`\n"
            "`/prompt default`\n\n"
            "`/prompt set <str>`\n"
            "`/prompt reset`\n"
        )

    @staticmethod
    def prompt_get(prompt: Prompt) -> str:
        """
        Show current prompt configuration.

        Args:
            prompt (Prompt): Current prompt object.

        Returns:
            str: MarkdownV2-safe prompt string.
        """
        return (
            "`Prompt`\n\n"
            f"`{escape(prompt.text) if prompt.text else 'Empty. Use /prompt set some_text'}`\n"
        )

    @staticmethod
    def prompt_set(response: tuple[bool, str]) -> str:
        """
        Format result of prompt update.

        Args:
            response (tuple): (success, updated_value)

        Returns:
            str: MarkdownV2-formatted update result.
        """
        return (
            f"`Prompt update {'successfull' if response[0] else 'failed'}`\n\n"
            f"`{escape(response[1])}`\n"
        )

    @staticmethod
    def prompt_reset() -> str:
        """
        Response for /prompt reset command.

        Returns:
            str: Confirmation text.
        """
        return "`Prompt settings cleared`"

    @staticmethod
    def prompt_default() -> str:
        """
        Response for resetting to default prompt.

        Returns:
            str: Confirmation text.
        """
        return "`Default prompt is set`"

    @staticmethod
    def chat_help() -> str:
        """
        Usage guide for the /chat command.

        Returns:
            str: Help text.
        """
        return "`/chat your_prompt_here`"

    @staticmethod
    def chat_reply(response: tuple[bool, str]) -> str:
        """
        Format the result of a chat reply.

        Args:
            response (tuple): (success, content)

        Returns:
            str: LLM response or error message.
        """
        return escape(response[1]) if response[0] else "`Something went wrong...`"

from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

from telegram_gpt.formatters import Formatters
from telegram_gpt.logger import Logger
from telegram_gpt.plugs import GPTPlug, SettingsPlug, PromptPlug


class TelegramBot:
    """
    Telegram bot wrapper for chat interaction using LLMs, 
    with configurable settings and prompts.
    """

    def __init__(self, logger: Logger, token: str, gptplug: GPTPlug,
                 settingsplug: SettingsPlug, promptplug: PromptPlug):
        """
        Initialize the bot with logger, token, and plug modules.

        Args:
            logger (Logger): Logger instance.
            token (str): Telegram bot token.
            gptplug (GPTPlug): Groq API interaction plug.
            settingsplug (SettingsPlug): Model settings plug.
            promptplug (PromptPlug): System prompt plug.
        """
        self.logger = logger
        self.gptplug = gptplug
        self.settingsplug = settingsplug
        self.promptplug = promptplug

        self.app = ApplicationBuilder().token(token).build()
        self._register_handlers()

    def _register_handlers(self):
        """
        Register Telegram bot command handlers.
        """
        self.app.add_handler(CommandHandler("chat", self.chat))
        self.app.add_handler(CommandHandler("models", self.models))
        self.app.add_handler(CommandHandler("prompt", self.prompt))

    def _log(self, update: Update, scope: str) -> None:
        """
        Log incoming message with metadata.

        Args:
            update (Update): Incoming update.
            scope (str): Scope label for the log entry.
        """
        self.logger.debug(
            module='Telegram Bot',
            scope=scope,
            message=(
                f"Received '{update.message.text}' "
                f"from '{update.effective_user.first_name}' / '{update.effective_user.id}'"
            )
        )

    async def models(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """
        Handle the /models command for querying, listing, or updating model settings.
        """
        self._log(update=update, scope='Models')

        attributes = ('model', 'temperature', 'frequency', 'presence', 'top')

        if len(context.args) == 1 and context.args[0] in ('get', 'list', 'default'):
            match context.args[0]:
                case 'get':
                    await update.message.reply_text(
                        Formatters.models_get(self.settingsplug.configuration),
                        parse_mode='MarkdownV2'
                    )
                case 'list':
                    await update.message.reply_text(
                        Formatters.models_list(self.gptplug.models_list()),
                        parse_mode='MarkdownV2'
                    )
                case 'default':
                    self.settingsplug.preset()
                    await update.message.reply_text(
                        Formatters.models_default(),
                        parse_mode='MarkdownV2'
                    )

            return

        elif len(context.args) == 3 and context.args[0] == 'set' and context.args[1] in attributes:
            response = self.settingsplug.update(
                **{context.args[1]: context.args[2],
                'models': self.gptplug.models}
            )

            await update.message.reply_text(
                Formatters.models_set(response),
                parse_mode='MarkdownV2'
            )

            return

        await update.message.reply_text(Formatters.models_help(), parse_mode='MarkdownV2')

    async def prompt(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """
        Handle the /prompt command for viewing or modifying the system prompt.
        """
        self._log(update=update, scope='Prompt')

        if len(context.args) == 1 and context.args[0] in ('get', 'reset', 'default'):
            match context.args[0]:
                case 'get':
                    await update.message.reply_text(
                        Formatters.prompt_get(self.promptplug.configuration),
                        parse_mode='MarkdownV2'
                    )
                case 'reset':
                    self.promptplug.update(prompt="")
                    await update.message.reply_text(
                        Formatters.prompt_reset(),
                        parse_mode='MarkdownV2'
                    )
                case 'default':
                    self.promptplug.preset()
                    await update.message.reply_text(
                        Formatters.prompt_default(),
                        parse_mode='MarkdownV2'
                    )

            return

        elif len(context.args) > 1 and context.args[0] == 'set':
            response = self.promptplug.update(prompt=" ".join(context.args[1:]))
            await update.message.reply_text(Formatters.prompt_set(response), parse_mode='MarkdownV2')

            return

        await update.message.reply_text(Formatters.prompt_help(), parse_mode='MarkdownV2')

    async def chat(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Handle the /chat command and respond with model output.
        """
        self._log(update=update, scope='Chat')

        query = update.message.text.partition(' ')[2]

        if not query:
            await update.message.reply_text(Formatters.chat_help(), parse_mode='MarkdownV2')
            return

        response = self.gptplug.chat(
            query=query,
            settings=self.settingsplug.configuration,
            prompt=self.promptplug.configuration
        )

        await update.message.reply_text(Formatters.chat_reply(response), parse_mode='MarkdownV2')

    def run(self):
        """
        Start polling for Telegram updates.
        """
        self.logger.info(module='Telegram Bot', scope='Setup', message="Bot is up and running")
        self.app.run_polling()

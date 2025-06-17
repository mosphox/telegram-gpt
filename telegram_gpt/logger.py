from datetime import datetime
import logging


class Logger:
    """
    Custom logger that lets you set a module and scope so your logs actually make sense.
    Outputs logs like a proper adult: with timestamps and labeled sections.

    Example output:
    |INFO    | 15/06/2025 03:48:58 | [Module Name] [Scope Name] Something happened

    Use .set(module='YourModule', scope='SomeFunction') before logging like a civilized human.
    """

    def __init__(self, name: str = __name__, level: int = logging.DEBUG, logfile: str = None):
        """
        Initializes the Logger instance. Sets up handlers for stdout and optional logfile.

        Args:
            name (str): Name for the logger. Usually just __name__ unless you're being fancy.
            level (int): Minimum logging level to show. Defaults to DEBUG, because you clearly want chaos.
            logfile (str, optional): Path to a log file. Leave it None if you like living dangerously.
        """
        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)

        handlers = [logging.StreamHandler()]
        if logfile:
            handlers.append(logging.FileHandler(logfile))

        for handler in handlers:
            handler.setLevel(level)
            handler.setFormatter(logging.Formatter("%(message)s"))
            self.logger.addHandler(handler)

        self.module, self.scope = None, None

    def _validate_log(self, **kwargs) -> None:
        """
        Checks if module, scope, and message are set.
        If not, logs a warning about your incompetence.

        Args:
            logmessage (str): The message you were *trying* to log.
        """
        if self.module is None and not kwargs.get('module'):
            self.warning(
                message="Module is unset, use Logger.set(module='Module Name')",
                module="Logger",
                scope="Validator",
            )

        if self.scope is None and not kwargs.get('scope'):
            self.warning(
                message="Scope is unset, use Logger.set(scope='Scope Name')",
                module="Logger",
                scope="Validator",
            )

        if not kwargs.get('message'):
            self.warning(
                message="Message is unset, use Logger.level(message='Message')",
                module="Logger",
                scope="Validator",
            )

    def _create_log(self, *args, **kwargs) -> None:
        """
        Does the actual dirty work: builds and spits out the log message.

        Keyword Args:
            level (str): One of 'debug', 'info', 'warning', 'error', 'critical'.
            message (str): The thing you're trying to say.
            module (str, optional): Temporary override if you're two-timing your current module.
            scope (str, optional): Same as above, but for the scope.
            ignore_validation (bool): Skip the lecture about missing context. Use with caution.
        """
        self._validate_log(**kwargs)

        timestamp = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        module = kwargs.get("module") or self.module or "Unknown"
        scope = kwargs.get("scope") or self.scope or "Unknown"
        message = kwargs.get("message") or "Empty message"
        level = kwargs["level"].upper().ljust(8)

        formatted = f"| {level} | {timestamp} | [{module}] [{scope}] {message}"
        getattr(self.logger, kwargs["level"].lower())(formatted)

    def set(self, module=None, scope=None) -> None:
        """
        Set default module and/or scope for future log messages.

        Args:
            module (str, optional): Who's talking?
            scope (str, optional): Where exactly did it happen?

        Usage:
            logger.set(module="PaymentService", scope="charge_card")
        """
        if module:
            self.module = module
        if scope:
            self.scope = scope

    def reset(self) -> None:
        """
        Forgets the current module and scope, like you forget passwords.
        Call this when context changes.
        """
        self.module, self.scope = None, None

    def debug(self, *args, **kwargs) -> None:
        """
        DEBUG: For when things are mostly fine but you're paranoid and wanna see under the hood.
        """
        self._create_log(*args, **kwargs, level="debug")

    def info(self, *args, **kwargs) -> None:
        """
        INFO: Everything's working. You just want to brag.
        """
        self._create_log(*args, **kwargs, level="info")

    def warning(self, *args, **kwargs) -> None:
        """
        WARNING: Something smells off but hasn’t caught fire... yet.
        """
        self._create_log(*args, **kwargs, level="warning")

    def error(self, *args, **kwargs) -> None:
        """
        ERROR: Something broke. Time to act like you know what you're doing.
        """
        self._create_log(*args, **kwargs, level="error")

    def critical(self, *args, **kwargs) -> None:
        """
        CRITICAL: Everything’s on fire. Blame someone. Preferably not yourself.
        """
        self._create_log(*args, **kwargs, level="critical")

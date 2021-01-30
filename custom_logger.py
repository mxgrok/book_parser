import logging


class CustomLoggerSingleton:
    """
    Log levels:
        CRITICAL = 50
        FATAL = CRITICAL
        ERROR = 40
        WARNING = 30
        WARN = WARNING
        INFO = 20
        DEBUG = 10
        NOTSET = 0
    """

    _instance = None

    def __new__(cls, *args, **kwargs):
        if not isinstance(cls._instance, cls):
            cls._instance = object.__new__(cls)

        return cls._instance

    def __init__(self,
                 logger_name,
                 logger_level='debug'):

        self.logger_name = logger_name
        self.logger_level = logger_level.upper()
        self.logger = self.start_logger()

    def start_logger(self):

        formatter = logging.Formatter(
            fmt='%(asctime)s %(levelname)-8s %(message)s',
            datefmt='%m-%d-%y %H:%M:%S'
        )

        current_logger = logging.getLogger(self.logger_name)
        current_logger.setLevel(self.logger_level)

        stdout_logger = logging.StreamHandler()
        stdout_logger.setFormatter(formatter)

        current_logger.addHandler(stdout_logger)

        return current_logger

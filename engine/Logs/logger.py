# Устанавливает систему логирования
# Автоматический создает логгеры для всех приложений из settings.py
# Можно создать логгер вручную, указав путь к файлу, уровень логирования и вывод в консоль
# 
# Использование в других модулях:
# from .logger import database_logger, api_logger  # и т.п.

import logging
from logging.handlers import RotatingFileHandler

from engine.Settings import LOG_CONFIGS


class CustomLogger:
    @classmethod
    def get_logger(cls, name, log_file=None, level="INFO", console_output=True):
        if log_file is None:
            raise ValueError(f"Specify log file {name}")
        
        return cls._setup_logger(
            name=name,
            log_file=log_file,
            level=level,
            console_output=console_output
        )

    @classmethod
    def get_logger_auto(cls, name):
        if name not in LOG_CONFIGS["APPS"]:
            raise ValueError(f"Unknown app name: {name}")
            
        return cls._setup_logger(
            name=name,
            log_file=LOG_CONFIGS["APPS"][name]["FILE"],
            level=LOG_CONFIGS["APPS"][name]["LEVEL"],
            console_output=LOG_CONFIGS["APPS"][name]["CONSOLE_OUTPUT"]
        )

    @staticmethod
    def _setup_logger(name, log_file, level, console_output):
        logger = logging.getLogger(name)
        
        if logger.handlers:
            return logger

        logger.setLevel(getattr(logging, level))
        logger.propagate = False

        formatter = logging.Formatter(LOG_CONFIGS["SIMPLE_FORMAT"])

        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=10 * 1024 * 1024,
            backupCount=5,
            encoding="utf-8"
        )
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

        if console_output:
            console_handler = logging.StreamHandler()
            console_handler.setFormatter(formatter)
            logger.addHandler(console_handler)

        return logger


# Создаём логгеры динамически
for app in LOG_CONFIGS["APPS"].keys():
    globals()[f"{app.lower()}"] = CustomLogger.get_logger_auto(app)

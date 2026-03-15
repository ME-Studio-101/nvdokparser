from pathlib import Path


RUN = [
    "tg_bot.py",
]

APP_NAME = "nvparser"
VERSION = "0.1"
BASE_DIR = Path(__file__).resolve().parent.parent

PATHS = {
    "SETTINGS": BASE_DIR / "Settings",
    "SCRIPTS": BASE_DIR / "Scripts",
    "DATA": BASE_DIR / "Data",
    "DB": BASE_DIR / "Data" / "app.db",
    "LOGS": BASE_DIR / "Logs",
}

LOG_CONFIGS = {
    "SIMPLE_FORMAT": "%(asctime)s - %(levelname)s - %(message)s",
    "APPS": {
        f"MAIN": {
            "FILE": PATHS["LOGS"] / f"main.log",
            "LEVEL": "INFO",
            "CONSOLE_OUTPUT": True,
        },
        "DEBUG": {
            "FILE": PATHS["LOGS"] / "debug.log",
            "LEVEL": "DEBUG",
            "CONSOLE_OUTPUT": True,
        },
        "ERP": {
            "FILE": PATHS["LOGS"] / "erp.log",
            "LEVEL": "INFO",
            "CONSOLE_OUTPUT": True,
        },
        "TG_BOT": {
            "FILE": PATHS["LOGS"] / "tg_bot.log",
            "LEVEL": "INFO",
            "CONSOLE_OUTPUT": True,
        },
        "GS_SERVER": {
            "FILE": PATHS["LOGS"] / "gs_server.log",
            "LEVEL": "INFO",
            "CONSOLE_OUTPUT": True,
        },
    }
}

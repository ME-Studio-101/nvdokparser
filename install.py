# Этот скрипт:
# 1. Устанавливает виртуальное окружение
# 2. Обновляет pip
# 3. Устанавливает зависимости


import os
import subprocess
import sys
import platform

from engine.Settings.settings import BASE_DIR, PATHS

REQUIREMENTS = PATHS["SETTINGS"] / "requirements.txt"

# Определяем путь к интерпретатору Python в виртуальном окружении
if platform.system() == "Windows":
    PYTHON_EXECUTABLE = BASE_DIR / "venv" / "Scripts" / "python.exe"
else:
    PYTHON_EXECUTABLE = BASE_DIR / "venv" / "bin" / "python"

# 1. Создание виртуального окружения
try:
    subprocess.check_call([
        sys.executable,
        "-m",
        "venv",
        str(BASE_DIR / "venv")
    ])
    mt1 = "Installing venv | SUCCESS\n"
except subprocess.CalledProcessError as e:
    mt1 = f"Installing venv | ERROR\n{e}"
print(mt1)

# 2. Обновление pip
try:
    subprocess.check_call([
        PYTHON_EXECUTABLE,
        "-m",
        "pip",
        "install",
        "--upgrade",
        "pip",
    ])
    mt2 = f"Updating pip | SUCCESS\n"
except subprocess.CalledProcessError as e:
    mt2 = f"Updating pip | ERROR\n{e}"
print(mt2)

# 3. Установка зависимостей
try:
    if os.path.exists(REQUIREMENTS):
        subprocess.check_call([
            PYTHON_EXECUTABLE,
            "-m",
            "pip",
            "install",
            "-r",
            REQUIREMENTS,
        ])
    mt3 = f"Installing requirements | SUCCESS\n"
except subprocess.CalledProcessError as e:
    mt3 = f"Installing requirements | ERROR\n{e}"
print(mt3)

# 4. Установка внутренних пакетов
try:
    subprocess.check_call([
        PYTHON_EXECUTABLE,
        "-m",
        "pip",
        "install",
        "-e",
        BASE_DIR,
    ])
    mt4 = f"Installing internal packages | SUCCESS\n"
except subprocess.CalledProcessError as e:
    mt4 = f"Installing internal packages | ERROR\n{e}"
print(mt4)

# 5. Создание базы данных
try:
    subprocess.check_call([
        PYTHON_EXECUTABLE,
        "engine/Data/create_db.py",
    ])
    mt5 = f"Creating database | SUCCESS\n"
except subprocess.CalledProcessError as e:
    mt5 = f"Creating database | ERROR\n{e}"
print(mt5)

# 6. Итоги
print(
    "RESUME:\n",
    mt1,
    mt2,
    mt3,
    mt4,
    mt5,
)

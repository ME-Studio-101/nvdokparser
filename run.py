# Запуск всех указанных в настройках скриптов из под venv

import subprocess
import platform

from engine.Settings import BASE_DIR, PATHS, RUN


if platform.system() == "Windows":
    PYTHON_EXECUTABLE = BASE_DIR / "venv" / "Scripts" / "python.exe"
else:
    PYTHON_EXECUTABLE = BASE_DIR / "venv" / "bin" / "python"

if not PYTHON_EXECUTABLE.exists():
    raise FileNotFoundError(f"Виртуальное окружение не найдено: {PYTHON_EXECUTABLE}")

processes = []

try:
    for script in RUN:
        script_path = PATHS["SCRIPTS"] / script
        print(f"ЗАПУСК: {script_path}")
        process = subprocess.Popen(
            [str(PYTHON_EXECUTABLE), str(script_path)]
        )
        processes.append(process)

    print("Все скрипты запущены.")
    
    for process in processes:
        process.wait()
        
except KeyboardInterrupt:
    print("\nПолучен сигнал остановки. Завершение работы...")
    for process in processes:
        try:
            process.terminate()
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()
        except Exception as e:
            print(f"Ошибка при остановке: {e}")
    print("Все завершено")

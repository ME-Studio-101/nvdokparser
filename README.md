Предзапуск настройки
- в engine.Scripts.erp_api.base_api заполнить константы аутентификации
- в engine.Scripts.tg_bot.instance внести токен бота

Запуск
* все команды выполняются из корневой директории проекта
- `python install.py` (установка инфраструктуры)
- `python -m engine.Data.database.db_parser` (создать и заполнить БД) (если БД уже создана - удалить её перед этим, иначе города в БД задвоятся) (пока так)
- `python -m engine.Scripts.run_tgbot` (запустить бота)
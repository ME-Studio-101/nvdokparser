# Структура команд:
# 1. Если сообщение начинается с команды (brb, brs, getbrb, getbrs) — вызываем соответствующую функцию.
# 2. Иначе разбираем запрос как loyal: «город направление_сайт [ставка]».
# 3. Последнее слово: если число — ставка (установка курса), иначе — просто выдача (проверить как стоим).
# 4. Город: первое слово или несколько для исключений (Красная Поляна, Минеральные Воды, Набережные Челны, Нижний Новгород, Ростов на Дону, Старый Оскол).
# 5. То что посередине — направление_сайт (тр/рт + сайт: Е, СВЦ, Ф, ЙО, К и т.д.).


from aiogram import types, F
from aiogram.enums import ParseMode
from aiogram.dispatcher.router import Router
from aiogram.filters import Command

from .inctance import bot
from engine.Data.database.db import get_db
from engine.Data.database.models import Site, Town
from engine.Data.database.orm import find_site_by_alias

from engine.Scripts.erp_api.handlers import correct_bankrub_buy, correct_bankrub_sell, correct_cashrub
from engine.Scripts.erp_api.base_api import get_directions, get_direction, parse_direction4install_rate, parse_direction4br


router = Router()
COMMAND_HANDLERS = {}


def cmd(name: str):
    """Добавляем команду в словарь"""
    def decorator(func):
        COMMAND_HANDLERS[name.lower()] = func
        return func
    return decorator


@router.message(Command(commands=["start"]))
async def send_welcome(message: types.Message):
    message_text = (
        "*Установка курсов*.\n"
        "\\* Базовая установка курса: `город направление_сайт ставка`.\n"
        " пример: `Москва трЕ 1,2`.\n"
        " город - как записан в ERP - Ростов на Дону.\n"
        " направление_сайт - тр для покупки, рт для продажи; сайты: Е, СВЦ, Ф, ЙО, КОИН; пишем слитно - `трЕ`"
        " ставка - знак как при установке сейчас, можно и запятую и точку.\n"
        "\\* Проверить как стоим - `get город направление_сайт`.\n"
        "\\* Bank RUB покупки - `brb ставка`.\n"
        "\\* Bank RUB продажи - `brs ставка`.\n"
    )
    chat_id = message.chat.id
    await bot.send_message(
        chat_id,
        message_text,
        parse_mode="Markdown",
    )


# _____________________РУЧКИ_______________________


async def loyal(message: types.Message, args: list[str]):
    """
    Разбор: «город направление_сайт [ставка]».
    Без ставки — выдача; со ставкой — установка и выдача.
    Города-исключения (несколько слов) задаются по первому слову.
    """
    # исключение - город состоит из нескольких слов
    MULTI_WORD_TOWN_LABELS = {
        "Красная": "Красная Поляна",
        "Минеральные": "Минеральные Воды",
        "Набережные": "Набережные Челны",
        "Нижний": "Нижний Новгород",
        "Ростов": "Ростов на Дону",
        "Старый": "Старый Оскол",
    }
    db = get_db()

    # 1. Ставка - последний аргумент
    rate = args[-1]
    try:
        value = float(rate.replace(",", ".").strip())
        args = args[:-1]
    except (TypeError, ValueError):
        rate = None

    # 2. Город: по первому слову
    town = args[0]
    if town in MULTI_WORD_TOWN_LABELS:
        town_label = MULTI_WORD_TOWN_LABELS[town]
    else:
        town_label = town
    town_obj = db.query(Town).filter(Town.label == town_label).first()
    if town_obj is None:
        await message.reply(f"Город `{town}` не найден.", parse_mode=ParseMode.HTML)
        return

    # 3. Направление и сайт
    mode_site = args[1]
    # 3.1 Направление
    mode_raw = mode_site[:2]
    if mode_raw == "тр":
        mode = "buy_only"
        give = 550
        get = town_obj.erp_id
    elif mode_raw == "рт":
        mode = "sell_only"
        give = town_obj.erp_id
        get = 550
    else:
        await message.reply(f"Направление `{mode_raw}` не найдено.", parse_mode=ParseMode.HTML)
        return

    # 3.2 Сайт
    site_raw = mode_site[2:]
    site_obj = find_site_by_alias(db, site_raw)
    if site_obj is None:
        await message.reply(f"Сайт `{site_raw}` не найден.", parse_mode=ParseMode.HTML)
        return
    site = site_obj.erp_id

    # 4. Текущий курс
    def get_actual_rate():
        try:
            direction = parse_direction4install_rate(
                get_direction(
                    site=site,
                    group=town_obj.group,
                    subgroup=town_obj.subGroup,
                    give=give,
                    get=get,
                )
            )
            return f"{direction['site']} {direction['currencyFrom']} {direction['currencyTo']} {direction['rateSource']} {direction['feePercent']}", direction["feePercent"]
        except Exception as e:
            print(f"ERP error in loyal(): {e}")
            return "Не удалось получить направление из ERP (возможна ошибка 500 на стороне ERP).", None

    msg1, _ = get_actual_rate()
    if msg1 is None:
        await message.reply("Не удалось получить направление из ERP (возможна ошибка 500 на стороне ERP).", parse_mode=ParseMode.HTML)
        return
    if rate is None:
        await bot.send_message(message.chat.id, f"<pre>{msg1}</pre>", parse_mode=ParseMode.HTML)
        return

    # 5. Установка курса
    try:
        result = correct_cashrub(town, mode, site, value)
    except Exception as e:
        print(f"ERP error in correct_cashrub(): {e}")
        await message.reply("Не удалось установить курс в ERP (возможна ошибка 500 на стороне ERP).", parse_mode=ParseMode.HTML)
        return

    msg2, feePercent = get_actual_rate()
    if msg2 is None:
        await message.reply("Не удалось получить направление из ERP (возможна ошибка 500 на стороне ERP).", parse_mode=ParseMode.HTML)
        return
    await bot.send_message(message.chat.id, f"{result}\n<pre>{msg1} -> {feePercent}</pre>", parse_mode=ParseMode.HTML)


@cmd("brb")
async def cmd_brb(message: types.Message, args: list[str]):
    """brb <ставка> — например: brb 1"""
    rate = args[0] if args else None
    if rate:
        try:
            value = float(rate.replace(",", ".").strip())
        except (TypeError, ValueError):
            await message.reply("ставка должна быть числом", parse_mode=ParseMode.HTML)
            return

        result = correct_bankrub_buy(value)
    else:
        result = ""

    # проверка направлений
    check1 = parse_direction4br(get_direction(site=1, group=1, subgroup=15, give=550, get=138))
    check2 = parse_direction4br(get_direction(site=6, group=1, subgroup=15, give=550, get=138))
    check3 = parse_direction4br(get_direction(site=2, group=1, subgroup=15, give=550, get=138))
    
    # Вычисляем максимальную длину первой колонки (название сайта) для выравнивания
    max_len = max(len(str(check1["site"])), len(str(check2["site"])), len(str(check3["site"])))

    message_text = (
        f"{result}\n"
        "<pre>"
        f"{check1['site']:<{max_len}} {check1['currencyFrom']} {check1['currencyTo']} {check1['feePercent']} {check1['rateSource']}\n"
        f"{check2['site']:<{max_len}} {check2['currencyFrom']} {check2['currencyTo']} {check2['feePercent']} {check2['rateSource']}\n"
        f"{check3['site']:<{max_len}} {check3['currencyFrom']} {check3['currencyTo']} {check3['feePercent']} {check3['rateSource']}"
        "</pre>"
    )
    chat_id = message.chat.id
    await bot.send_message(
        chat_id,
        message_text,
        parse_mode=ParseMode.HTML,
    )


@cmd("brs")
async def cmd_brs(message: types.Message, args: list[str]):
    """brs <ставка> — например: brs 1"""
    rate = args[0] if args else None
    if rate:
        try:
            value = float(rate.replace(",", ".").strip())
        except (TypeError, ValueError):
            await message.reply("ставка должна быть числом", parse_mode=ParseMode.HTML)
            return

        result = correct_bankrub_sell(value)
    else:
        result = ""

    # проверка направлений
    check1 = parse_direction4br(get_direction(site=1, group=1, subgroup=15, give=138, get=550))
    check2 = parse_direction4br(get_direction(site=6, group=1, subgroup=15, give=138, get=550))

    # Вычисляем максимальную длину первой колонки (название сайта) для выравнивания
    max_len = max(len(str(check1["site"])), len(str(check2["site"])))

    message_text = (
        f"{result}\n"
        "<pre>"
        f"{check1['site']:<{max_len}} {check1['currencyFrom']} {check1['currencyTo']} {check1['feePercent']} {check1['rateSource']}\n"
        f"{check2['site']:<{max_len}} {check2['currencyFrom']} {check2['currencyTo']} {check2['feePercent']} {check2['rateSource']}\n"
        "</pre>"
    )
    chat_id = message.chat.id
    await bot.send_message(
        chat_id,
        message_text,
        parse_mode=ParseMode.HTML,
    )


# __________________Роутер_________________


@router.message(F.text)
async def text_command_router(message: types.Message):
    """Единая точка входа: парсит текст и перенаправляет на нужную ручку."""
    parts = message.text.strip().split()
    if not parts:
        return
    command = parts[0].lower()
    handler = COMMAND_HANDLERS.get(command)
    if handler is None:
        args = parts
        await loyal(message, args)
    else:
        args = parts[1:]
        await handler(message, args)

from .models import Site, Town
from .db import get_db, init_db
from .crud import CRUDBase
from engine.Scripts.erp_api.base_api import get_currencies, get_directions
from pathlib import Path
import json


DATA_DIR = Path(__file__).resolve().parent.parent  # engine/Data
RAW_DIR = DATA_DIR / "raw"


## сохранить данные в файл
def save_data_to_file(data, savename="_"):
    RAW_DIR.mkdir(exist_ok=True)
    file_path = RAW_DIR / f"{savename}.json"
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    return None


# ______________________0________________________________________


def db_add_sites():
    db = get_db()
    # for site in get_sites():
    #     pass
    sites = [
        Site(
            names="|E-change|Е|",
            label="E-change",
            erp_id=1,
        ),
        Site(
            names="|SpbWMCasher|СВЦ|",
            label="SpbWMCasher",
            erp_id=6,
        ),
        Site(
            names="|YoChange|ЙО|",
            label="YoChange",
            erp_id=3,
        ),
        Site(
            names="|Fast|Ф|",
            label="Fast",
            erp_id=2,
        ),
        Site(
            names="|Coinshop24|К|",
            label="Coinshop24",
            erp_id=5,
        ),
    ]
    for site in sites:
        db.add(site)

    # newsite = Site(
    #     label="Ozon",
    #     erp_id=4,
    # )
    # newsite.names_list = ["Ozon", "ozon", "озон"]
    # db.add(newsite)
    db.commit()
    return None


def db_get_sites():
    db = get_db()
    sites = db.query(Site).all()
    for site in sites:
        print(site.label+" "*(11-len(site.label)), site.erp_id, site.names)
    db.close()
    return None


# ______________________1________________________________________


def db_choose_group_for_currency(label):
    if label.endswith("(RUB)"):
        return 1 # RUSSIA
    elif label.endswith("(USD)") or label.endswith("(EUR)"):
        return 2 # WORLD


def db_choose_subGroup_for_currency(currencyCode):
    if currencyCode == "CASHRUB":
        return 44
    else:
        return 0


def db_choose_rateSource_for_currency(currencyCode):
    if currencyCode == "CASHRUB":
        return "grinex"
    else:
        return "0"


def db_add_e_rus_cashrub_currencies():
    db = get_db()
    currencies = get_currencies(search="CASHRUB")
    ban_list = ["GAR (PRIORITY)", "Ростов на Дону (RUB) del", "Таганрог (RUB) del"]
    for item in currencies:
        # отсюда исключаем PRIORITY
        if item["mainFields"]["label"]["value"] in ban_list:
            continue
        town = Town(
            erp_id=item["mainFields"]["id"]["value"],
            label=item["mainFields"]["label"]["value"][:-6],
            group=db_choose_group_for_currency(item["mainFields"]["label"]["value"]),
            subGroup=db_choose_subGroup_for_currency(item["mainFields"]["currencyCode"]["value"]),
            rateSource=db_choose_rateSource_for_currency(item["mainFields"]["currencyCode"]["value"]),
        )
        db.add(town)
    db.commit()


if __name__ == "__main__":
    init_db()  # Создать таблицы, если их ещё нет

    db_add_e_rus_cashrub_currencies()
    db = get_db()
    towns = db.query(Town).order_by(Town.label).all()
    for town in towns:
        # print(town.group, town.subGroup, town.label, town.erp_id, town.rateSource)
        print(town.label)
    print(f"Добавлено {len(towns)} городов")
    db.close()

    db_add_sites()
    db_get_sites()

# __________________________2________________________________________

# def update_all_currencies():
#     response = request_get_currencies(search="CASHRUB")
#     counter = 0
#     for item in response:
#         print(item["mainFields"]["label"]["value"], item["mainFields"]["id"]["value"])
#         counter += 1
#     print(f"Найдено {counter} валют")
#     return None

# if __name__ == "__main__":
#     init_db()  # Создать таблицы, если их ещё нет
#     update_all_currencies()








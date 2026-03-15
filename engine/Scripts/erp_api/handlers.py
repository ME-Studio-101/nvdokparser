import requests
import pyotp
import json
from pprint import pprint

from engine.Data.database.db import get_db
from engine.Data.database.models import Town
from engine.Scripts.erp_api.base_api import post_install_rate


# install_rate / BankRUB покупки
def correct_bankrub_buy(rate):
    data = {
        "site":[1,2,6],
        "group":[1],
        "subGroup":[15],
        "rateSource":"rapira",
        "course":"78.235",
        "modes":["buy_only"],
        "currentSourceRate":str(rate)
    }
    return post_install_rate(data)


# install_rate / BankRUB продажи
def correct_bankrub_sell(rate):
    data = {
        "site":[1,2,6],
        "group":[1],
        "subGroup":[15],
        "rateSource":"rapira",
        "course":"78.235",
        "modes":["sell_only"],
        "currentSourceRate":str(rate)
    }
    return post_install_rate(data)


# install_rate / CashRUB
def correct_cashrub(town, mode, site, rate):
    db = get_db()
    town = db.query(Town).filter(Town.label == town).first()
    data = {
        "site":[site],
        "group":town.group,
        "subGroup":town.subGroup,
        "modes": [mode],
        "currencyTo": [town.erp_id],
        "currentSourceRate":str(rate),
        "rateSource":town.rateSource,
        "course":"78.235",
    }
    return post_install_rate(data)


def update_turky():
    
    pokstambul = {
        "site": [
            1,
            2
        ],
        "group": [
            2
        ],
        "subGroup": [
            48
        ],
        "currencyTo": [
            340
        ],
        "rateSource": "xe",
        "modes": [
            "buy_only"
        ],
        "course": "1",
        "currentSourceRate": "0.6"
    }
    print(post_install_rate(pokstambul))

    pokantalya = {
        "site": [
            1,
            2
        ],
        "group": [
            2
        ],
        "subGroup": [
            48
        ],
        "currencyTo": [
            416
        ],
        "rateSource": "xe",
        "modes": [
            "buy_only"
        ],
        "course": "1",
        "currentSourceRate": "0.75"
    }
    print(post_install_rate(pokantalya))

    pokalanya = {
        "site": [
            1,
            2
        ],
        "group": [
            2
        ],
        "subGroup": [
            48
        ],
        "currencyTo": [
            308
        ],
        "rateSource": "xe",
        "modes": [
            "buy_only"
        ],
        "course": "1",
        "currentSourceRate": "0.85"
    }
    print(post_install_rate(pokalanya))
    
    prstambul = {
        "site": [
            1,
            2
        ],
        "group": [
            2
        ],
        "subGroup": [
            48
        ],
        "currencyTo": [
            340
        ],
        "rateSource": "xe",
        "modes": [
            "sell_only"
        ],
        "course": "1",
        "currentSourceRate": "0.4"
    }
    print(post_install_rate(prstambul))

    prantalya = {
        "site": [
            1,
            2
        ],
        "group": [
            2
        ],
        "subGroup": [
            48
        ],
        "currencyTo": [
            416
        ],
        "rateSource": "xe",
        "modes": [
            "sell_only"
        ],
        "course": "1",
        "currentSourceRate": "0.55"
    }
    print(post_install_rate(prantalya))
    pralanya = {
        "site": [
            1,
            2
        ],
        "group": [
            2
        ],
        "subGroup": [
            48
        ],
        "currencyTo": [
            308
        ],
        "rateSource": "xe",
        "modes": [
            "sell_only"
        ],
        "course": "1",
        "currentSourceRate": "0.65"
    }
    print(post_install_rate(pralanya))


if __name__ == "__main__":
    ERP_TOKEN = login_and_verify()


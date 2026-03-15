import logging
import requests
import pyotp
import json
from pprint import pprint

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)


ERP_LOGIN = "" # логин
ERP_PASSWORD = "" # пароль
ERP_USER_ID = # id пользователя (число) (надо глянуть в Network, любой запрос к ERP)
ERP_GA_SECRET = "" # ключ GA
ERP_TOKEN = None


## ______________AUTH________________________

## GA
def get_ga_code():
    totp = pyotp.TOTP(ERP_GA_SECRET)
    return totp.now()


## ВХОД В ERP
def login_and_verify():
    base_url = "https://erp.technology-connect.com/api/v1/auth"
    headers = {
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "ru,en;q=0.9",
        "Connection": "keep-alive",
        "Content-Type": "application/json",
        "Origin": "https://erp.technology-connect.com",
        "Referer": "https://erp.technology-connect.com/login",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
        "User-Agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Mobile Safari/537.36",
        "sec-ch-ua": '"Not/A)Brand";v="8", "Chromium";v="126", "YaBrowser";v="24.7", "Yowser";v="2.5"',
        "sec-ch-ua-mobile": "?1",
        "sec-ch-ua-platform": '"Android"',
    }

    # Шаг 1: Вход по логину и паролю
    login_url = f"{base_url}/login"
    login_data = {"username": ERP_LOGIN, "password": ERP_PASSWORD}
    try:
        response = requests.post(login_url, headers=headers, json=login_data)
        response.raise_for_status()
        log.info("Успешный вход")
    except requests.exceptions.RequestException as e:
        log.error(f"Ошибка при входе по логину и паролю: {e}")
        return "Error 1: Login and Password"

    # Шаг 2: Двухфакторная аутентификация
    verify_url = f"{base_url}/two-factor/verify"
    try:
        code = get_ga_code()
    except Exception as e:
        log.error(f"Ошибка при получении кода двухфакторной аутентификации: {e}")
        return "Error 2: GA Code"

    verify_data = {"username": ERP_LOGIN, "code": code, "user_id": ERP_USER_ID}
    try:
        verify_response = requests.post(verify_url, json=verify_data)
        verify_response.raise_for_status()
        verify_response_json = verify_response.json()
        token = verify_response_json["token"]
        log.info(f"Успешная верификация")
        return token
    except requests.exceptions.RequestException as e:
        log.error(f"Ошибка при верификации: {e}")
        return "Error 3: Verify"


## Декоратор аутентификации
def erp_token(func):
    """
    Декоратор для запросов в ERP:
    - гарантирует наличие токена;
    - при 401 (Unauthorized) получает новый токен и повторяет запрос один раз.
    """
    def wrapper(*args, **kwargs):
        global ERP_TOKEN
        if ERP_TOKEN is None:
            ERP_TOKEN = login_and_verify()
        try:
            return func(*args, **kwargs)
        except requests.exceptions.HTTPError as e:
            # Если токен устарел / невалиден — пробуем обновить и повторить запрос
            if e.response is not None and e.response.status_code == 401:
                ERP_TOKEN = login_and_verify()
                return func(*args, **kwargs)
            raise
    return wrapper



## ___________________ЗАПРОСЫ____________________________


# GET / Currencies
@erp_token
def get_currencies(search=None):
    url = (
        "https://erp.technology-connect.com/api/v1/currency?limit=100000&offset=0&isExchangePage=true"
        + (f"&search={search}" if search else "")
    )
    headers = {
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "ru,en;q=0.9",
        "Authorization": f"Bearer {ERP_TOKEN}",
        "Connection": "keep-alive",
        "Cookie": f"user-token={ERP_TOKEN}",
        "Referer": "https://erp.technology-connect.com/currency",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
    }
    response = requests.get(url, headers=headers)
    print("STATUS:", response.status_code)
    response.raise_for_status()

    data = response.json()["data"]
    return data


# GET / Directions
@erp_token
def get_directions(site=0, group=0, subgroup=0, give=0, get=0):
    """
    Принимает параметры в виде erp_id для формирования запроса
    site: int - erp_id сайта
    group: int - erp_id группы
    subgroup: int - erp_id подгруппы
    give: int - erp_id валюты, которую даём
    get: int - erp_id валюты, которую получаем
    Возвращает направления в JSON
    """
    url = (
        "https://erp.technology-connect.com/api/v1/direction?limit=100000&offset=0&isExchangePage=true"
        + (f"&site[ids][0]={site}" if site else "")
        + (f"&group[ids][0]={group}" if group else "")
        + (f"&subGroup[ids][0]={subgroup}" if subgroup else "")
        + (f"&currencyGive[ids][0]={give}" if give else "")
        + (f"&currencyGet[ids][0]={get}" if get else "")
        # + (f"&currencyGive[ids][0]={give}" if give else "&currencyGive[ids][0]=550")
        # + (f"&currencyGet[ids][0]={get}" if get else "&currencyGet[ids][0]=550")
    )
    print(f"GET: {url}")
    headers = {
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "ru,en;q=0.9",
        "Authorization": f"Bearer {ERP_TOKEN}",
        "Connection": "keep-alive",
        "Cookie": f"user-token={ERP_TOKEN}",
        "Referer": "https://erp.technology-connect.com/directions",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
    }

    response = requests.get(url, headers=headers)
    print("STATUS:", response.status_code)
    response.raise_for_status()

    return response.json()["data"]


# GET / Direction
def get_direction(**kwargs):
    return get_directions(**kwargs)[0]


# POST / install-rate
@erp_token
def post_install_rate(data):
    url = "https://erp.technology-connect.com/api/v1/direction/install-rate"
    headers = {
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "ru,en;q=0.9",
        "Authorization": f"Bearer {ERP_TOKEN}",
        "Connection": "keep-alive",
        "Cookie": f"user-token={ERP_TOKEN}",
        "Referer": "https://erp.technology-connect.com/direction/view-directions",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
    }

    response = requests.post(url, headers=headers, json=data)
    print("STATUS:", response.status_code)
    response.raise_for_status()

    data = response.json()
    updated = data["data"]["updated"]
    skipped = data["data"]["skipped"]
    skippedList = data["data"]["skippedList"]
    errors = data["data"]["errors"]
    return f"Обновлено: {updated} направлений"


## __________________ПАРСЕРЫ______________________________


def parse_total(data):
    id = data["mainFields"]["id"]["value"] #12908
    status = data["mainFields"]["status"]["value"] #Вкл
    site = data["mainFields"]["site"]["value"] #E-change
    group = data["mainFields"]["group"]["value"] #RUSSIA
    subGroup = data["mainFields"]["subGroup"]["value"] #BANK RUB
    rateSource = data["mainFields"]["rateSource"]["value"] #rapira
    feePercent = str(data["mainFields"]["feePercent"]["value"])+"%" #1.20%
    isBestchangeSniperEnabled = "Снайпер" + str(data["mainFields"]["isBestchangeSniperEnabled"]["value"]) #Снайпер Вкл
    currencyFrom = data["mainFields"]["currencyFrom"]["value"] #TRC-20 (USDT)
    amountGive = round(float(data["mainFields"]["amountGive"]["value"]), 4) #1.0000
    currencyTo = data["mainFields"]["currencyTo"]["value"] #Сбербанк (RUB)
    amountGet = round(float(data["mainFields"]["amountGet"]["value"]), 4) #77.3604
    bhCourse = round(float(data["mainFields"]["bhCourse"]["value"]), 4) #77.3314
    placeOnBestchange = int(data["expandedFields"]["placeOnBestchange"]["value"]) if data["expandedFields"]["placeOnBestchange"]["value"] is not None else "-" #173
    holdPlace = int(data["expandedFields"]["holdPlace"]["value"]) if data["expandedFields"]["holdPlace"]["value"] is not None else "-"  #0
    decimalPlaces = int(data["expandedFields"]["decimalPlaces"]["value"]) #8
    kvvp = round(float(data["expandedFields"]["kvvp"]["value"]), 2) if data["expandedFields"]["kvvp"]["value"] is not None else "-" #0.01
    listed = data["expandedFields"]["listed"]["value"] #Вкл
    # position = data["expandedFields"]["position"]["value"] #?
    reserve = round(float(data["expandedFields"]["reserve"]["value"]), 0) #100000000
    minAmount = round(float(data["expandedFields"]["minAmount"]["value"]), 2) #581.69
    minAmountFiat = round(float(data["expandedFields"]["minAmountFiat"]["value"]), 0) #45000
    maxAmount = round(float(data["expandedFields"]["maxAmount"]["value"]), 2) #16804.46
    maxAmountFiat = round(float(data["expandedFields"]["maxAmountFiat"]["value"]), 0) #1300000
    extraLabels = data["expandedFields"]["extraLabels"]["value"] #manual, otherout
    floating = data["expandedFields"]["floating"]["value"] #0.3
    # criticalPlace = int(data["expandedFields"]["criticalPlace"]["value"]) #0
    # lastNotificationAt = data["expandedFields"]["lastNotificationAt"]["value"] #-
    # chuvm = data["expandedFields"]["chuvm"]["value"] #null
    # changeReason = data["expandedFields"]["changeReason"]["value"] #null
    return


## Parser / install-rate
def parse_direction4install_rate(data):
    """
    Под выдачу: E-change TRC-20 (USDT) Ростов на Дону (RUB) grinex 0.60%
    """
    site = data["mainFields"]["site"]["value"] #E-change
    rateSource = data["mainFields"]["rateSource"]["value"] #rapira
    feePercent = str(data["mainFields"]["feePercent"]["value"])+"%" #1.20%
    currencyFrom = data["mainFields"]["currencyFrom"]["value"] #TRC-20 (USDT)
    currencyTo = data["mainFields"]["currencyTo"]["value"] #Сбербанк (RUB)
    parsed_data = {
        "site": site,
        "currencyFrom": currencyFrom,
        "currencyTo": currencyTo,
        "rateSource": rateSource,
        "feePercent": feePercent,
    }
    return parsed_data


## Parser / install-rate
def parse_direction4br(data):
    """
    Под выдачу: E-change TRC-20 (USDT) Сбербанк (RUB) grinex 0.60%
    """
    site = data["mainFields"]["site"]["value"] #E-change
    currencyFrom = data["mainFields"]["currencyFrom"]["value"] #TRC-20 (USDT)
    currencyTo = data["mainFields"]["currencyTo"]["value"] #Сбербанк (RUB)
    feePercent = str(data["mainFields"]["feePercent"]["value"])+"%" #1.20%
    rateSource = data["mainFields"]["rateSource"]["value"] #rapira
    parsed_data = {
        "site": site,
        "currencyFrom": currencyFrom,
        "currencyTo": currencyTo,
        "feePercent": feePercent,
        "rateSource": rateSource,
    }
    return parsed_data



## __________________ЗАПУСК______________________________


if __name__ == "__main__":
    parse_direction4install_rate(get_directions(site=1, group=1, subgroup=44, give=550, get=0)[0])

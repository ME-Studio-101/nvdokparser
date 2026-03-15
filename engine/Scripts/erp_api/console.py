from engine.Data.database.db_parser import save_data_to_file
from .base_api import post_install_rate, get_directions, get_direction, get_currencies


def get_setup(site=0, group=0, subgroup=0, give=0, get=0):
    data = get_direction(site=site, group=group, subgroup=subgroup, give=give, get=get)
    
    site = data["mainFields"]["site"]["value"] #E-change
    group = data["mainFields"]["group"]["value"] #RUSSIA
    subGroup = data["mainFields"]["subGroup"]["value"] #BANK RUB
    rateSource = data["mainFields"]["rateSource"]["value"] #rapira
    feePercent = str(data["mainFields"]["feePercent"]["value"])+"%" #1.20%
    currencyFrom = data["mainFields"]["currencyFrom"]["value"] #TRC-20 (USDT)
    currencyTo = data["mainFields"]["currencyTo"]["value"] #Сбербанк (RUB)
    holdPlace = int(data["expandedFields"]["holdPlace"]["value"]) if data["expandedFields"]["holdPlace"]["value"] is not None else "-"  #0
    decimalPlaces = int(data["expandedFields"]["decimalPlaces"]["value"]) #8
    kvvp = round(float(data["expandedFields"]["kvvp"]["value"]), 2) if data["expandedFields"]["kvvp"]["value"] is not None else "-" #0.01
    listed = data["expandedFields"]["listed"]["value"] #Вкл
    reserve = round(float(data["expandedFields"]["reserve"]["value"]), 0) #100000000
    minAmountFiat = round(float(data["expandedFields"]["minAmountFiat"]["value"]), 0) #45000
    maxAmountFiat = round(float(data["expandedFields"]["maxAmountFiat"]["value"]), 0) #1300000
    extraLabels = data["expandedFields"]["extraLabels"]["value"] #manual, otherout
    floating = data["expandedFields"]["floating"]["value"] #0.3
    
    _ = {
        "сайт": site,
        "группа": group,
        "подгруппа": subGroup,
        "источник курса": rateSource,
        "ставка (%)": feePercent,
        "отдает клиент": currencyFrom,
        "получает клиент": currencyTo,
        "удержание места": holdPlace,
        "знаки после запятой": decimalPlaces,
        "кввп": kvvp,
        "листинг": listed,
        "резерв": reserve,
        "минимальная сумма": minAmountFiat,
        "максимальная сумма": maxAmountFiat,
        "метки": extraLabels,
        "floating": floating,
    }

    save_data_to_file(_, f"{currencyFrom} {currencyTo} {site}")

    return _


def get_alts_list(site=0, group=0, subgroup=0, give=0, get=0):
    _ = []
    __ = []
    for data in get_directions(site=site, group=group, subgroup=subgroup, give=give, get=get):
        currencyFrom = data["mainFields"]["currencyFrom"]["value"] #TRC-20 (USDT)
        currencyTo = data["mainFields"]["currencyTo"]["value"] #Сбербанк (RUB)
        _.append(f"{currencyTo}")
        __.append(f"{currencyFrom}")
    return _, __


def set_setup(datajson):

    return post_install_rate(data1), post_install_rate(data2)


if __name__ == "__main__":
    # ТОМСК
    # save_data_to_file(get_direction(site=1, group=1, subgroup=44, give=550, get=643), "пок_Томск1")
    # save_data_to_file(get_direction(site=1, group=1, subgroup=44, give=550, get=371), "покЕ_Томск371")
    # save_data_to_file(get_direction(site=3, group=1, subgroup=44, give=550, get=371), "покЙО_Томск371")
    # save_data_to_file(get_direction(site=6, group=1, subgroup=44, give=550, get=371), "покСВЦ_Томск371")
    # ТОМСК ВСЕ - 371 валюта
    
    # КРАСНОДАР - 637 пок(СВЦ, ЙО, 1отс) пр(Е) 178 пок(Е)
    # get_setup(site=1, group=1, subgroup=44, give=550, get=178)
    # get_setup(site=1, group=1, subgroup=44, give=9, get=178)
    # get_setup(site=1, group=1, subgroup=44, give=111, get=178)
    # KRASN
    # _, g = get_alts_list(site=1, group=1, subgroup=44, give=0, get=637)
    # d = []
    # x = []
    # for data in get_directions(site=1, group=1, subgroup=44, give=0, get=178):
    #     currencyFrom = data["mainFields"]["currencyFrom"]["value"] #TRC-20 (USDT)
    #     d.append(f"{currencyFrom}")
    # for alt in g:
    #     if alt not in d:
    #         x.append(f"{alt}")
    # print(len(g))
    # print(g)
    # print(len(d))
    # print(d)
    # print(x)

    # data1 = {
    #     "site": [
    #         1,
    #     ],
    #     "group": [
    #         1
    #     ],
    #     "subGroup": [
    #         44
    #     ],
    #     "currencyTo": [
    #         637
    #     ],
    #     "rateSource": "grinex",
    #     "course": "80.27",
    #     "modes": [
    #         "buy_only"
    #     ],

    #     "currentSourceRate": "0.8",
    #     "decimalPlaces": "8",
    #     "reserve": "100000000",
    #     "minAmount": "505000",
    #     "maxAmount": "9245900",
    #     "floating": "0.3"
    # }
    # data2 = {
    #     "site": [
    #         1
    #     ],
    #     "group": [
    #         1
    #     ],
    #     "subGroup": [
    #         44
    #     ],
    #     "currencyTo": [
    #         637
    #     ],
    #     "rateSource": "grinex",
    #     "course": "80.29",
    #     "modes": [
    #         "buy_only"
    #     ],
        
    #     "extraLabels": [
    #         3
    #     ],
    #     "listing": 1,
    #     "isBestchangeSniperEnabled": 1,
    #     "status": 1
    # }

    # print(post_install_rate(data1))
    # print(post_install_rate(data2))

    # Ростов - del 639 пок(Е ЙО 1отс) 202 пок(СВЦ) пр (Е)
    # get_setup(site=1, group=1, subgroup=44, give=550, get=639)
    # RSTV
    # _, g = get_alts_list(site=1, group=1, subgroup=44, give=0, get=202)
    # d = []
    # x = []
    # for data in get_directions(site=1, group=1, subgroup=44, give=0, get=639):
    #     currencyFrom = data["mainFields"]["currencyFrom"]["value"]
    #     d.append(f"{currencyFrom}")
    # for alt in g:
    #     if alt not in d:
    #         x.append(f"{alt}")
    # print(len(g))
    # print(g)
    # print(len(d))
    # print(d)
    # print(x)
    save_data_to_file(get_currencies(), "currencies1403")

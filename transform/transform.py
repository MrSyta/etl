import json
import datetime

with open("../extract/data.json") as file:
    data = json.load(file)
    for currency in data:
        currency["exchange"] = float(currency["exchange"].replace(",", "."))
        currency["transition"] = float(currency["transition"].rstrip("%"))
        currency["transition_pln"] = float(currency["transition_pln"].rstrip("zł"))
        currency["date"] = datetime.datetime.strptime(currency["date"], "%Y-%m-%d")

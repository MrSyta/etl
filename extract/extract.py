import requests
import json
from bs4 import BeautifulSoup


def scrape():
    URL = "https://kursy-walut.mybank.pl/"
    PAGE_NAME = "mybank"

    page = requests.get(URL)
    soup = BeautifulSoup(page.content, 'html.parser')

    currencies = soup.find("table", class_="tab_kursy").find_all("tr", class_="")
    for currency in currencies[1:]:
        data = currency.find_all("td")
        yield {
            "currency_name": data[0].get_text(),
            "symbol": data[1].get_text(),
            "exchange": data[2].get_text(),
            "transition": data[3].get_text(),
            "transition_pln": data[4].get_text(),
            "source": PAGE_NAME,
            "source_url": URL,
            "date": soup.find("br", class_="rwd-break").find_next_sibling("b").get_text()
            }


def save_data():
    data = list(scrape())
    with open("data.json", "w") as file:
        json.dump(data, file)

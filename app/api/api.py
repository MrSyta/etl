import os
import json
import requests
import pymongo

from bs4 import BeautifulSoup
from flask import Flask
from flask_restful import Api, Resource
from flask_cors import CORS


app = Flask(__name__)
CORS(app)
api = Api(app)


class Extract(Resource):
    def extract(self):
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
            try:
                data = list(scrape())
                with open("data.json", "w") as file:
                    json.dump(data, file)
                success = True
            except Exception:
                data = []
                success = False
            finally:
                return data, success

        return save_data()

    def get(self):
        data, success = self.extract()
        info = f"Pobrano {len(data)} rekordów"
        if success:
            msg = f"Pobieranie danych zakończone sukcesem. {info}."
        else:
            msg = f"Wystąpił błąd podczas pobierania danych. {info}."
        return {"msg": msg, "success": success}


api.add_resource(Extract, '/extract/')


class Transform(Resource):
    def transform(self):
        with open("data.json") as file:
            data = json.load(file)

        for currency in data:
            currency["currency_name"] = currency["currency_name"].strip()
            currency["exchange"] = float(currency["exchange"].replace(",", "."))
            currency["transition"] = float(currency["transition"].rstrip("%"))
            currency["transition_pln"] = float(currency["transition_pln"].rstrip("zł"))

        with open("transformed_data.json", "w") as file:
            json.dump(data, file)

    def get(self):
        try:
            self.transform()
            success = True
            msg = "Dane zostały pomyślnie przygotowane do zapisu."
        except Exception:
            success = False
            msg = "Wystąpił błąd podczas transformacji danych."
        finally:
            return {"msg": msg, "success": success}


api.add_resource(Transform, '/transform/')


class Load(Resource):
    def load(self):
        client, collection = Currencies.connect()

        with open('transformed_data.json') as file:
            data = json.load(file)

        loaded_data = []
        for currency in data:
            try:
                collection.insert_one(currency)
                loaded_data.append(currency)
            except pymongo.errors.DuplicateKeyError:
                continue

        client.close()

        new_rows = len(loaded_data)
        duplicate_rows = len(data) - new_rows

        return loaded_data, new_rows, duplicate_rows

    @staticmethod
    def remove_files():
        os.remove("data.json")
        os.remove("transformed_data.json")

    def get(self):
        try:
            loaded_data, new_rows, duplicate_rows = self.load()
            success = True
            msg = f"Dane zostały pomyślnie zapisane w bazie danych. Zapisano {new_rows} rekordów, " \
                  f"odrzucono {duplicate_rows} duplikatów."
            Load.remove_files()
        except Exception:
            success = False
            msg = "Wystąpił błąd podczas zapisywania danych do bazy danych."
        finally:
            return {"data": loaded_data, "msg": msg, "success": success}


api.add_resource(Load, '/load/')


class Currencies(Resource):
    @staticmethod
    def connect():
        client = pymongo.MongoClient()
        db = client["etl"]
        collection = db["currencies"]
        return client, collection

    def get(self):
        client, collection = Currencies.connect()
        data = Currencies.remove_id_fields(list(collection.find()))
        client.close()

        return {"data": data}

    def delete(self):
        client, collection = Currencies.connect()
        collection.delete_many({})
        client.close()

        return None, 204

    @staticmethod
    def remove_id_fields(currencies):
        for curr in currencies:
            del curr["_id"]
        return currencies


api.add_resource(Currencies, '/currencies/')

if __name__ == "__main__":
    app.run(debug=True)

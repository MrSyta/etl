from scrapy import Spider, Request

from ..items import CurrencyItem
from ..itemloaders import CurrencyItemLoader


class MybankKursyWalutSpider(Spider):
    name = "mybank"
    url = "https://kursy-walut.mybank.pl/"

    def start_requests(self):
        yield Request(self.url, self.parse)

    def parse(self, response):
        table_rows = response.css(".tab_kursy tr:not([class])")[1:]
        for row in table_rows:
            loader = CurrencyItemLoader(item=CurrencyItem(), response=response)
            loader.add_value('currency_name', row.css("td")[0].css("a::text").get())
            loader.add_value("symbol", row.css("td")[1].css("::text").get())
            loader.add_value("exchange", row.css("td")[2].css("::text").get())
            loader.add_value("transition", row.css("td")[3].css("::text").get())
            loader.add_value("transition_pln", row.css("td")[4].css("::text").get())
            loader.add_value("source", self.name)
            loader.add_value("source_url", response.url)
            loader.add_css("date", ".rwd-break+ b::text")

            yield loader.load_item()

from scrapy import Item, Field


class CurrencyItem(Item):
    currency_name = Field()
    symbol = Field()
    exchange = Field()
    transition = Field()
    transition_pln = Field()
    source = Field()
    source_url = Field()
    date = Field()

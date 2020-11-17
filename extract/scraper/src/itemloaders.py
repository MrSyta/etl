from scrapy.loader import ItemLoader
from itemloaders.processors import TakeFirst

from .items import CurrencyItem


class CurrencyItemLoader(ItemLoader):
    default_item_class = CurrencyItem
    default_output_processor = TakeFirst()

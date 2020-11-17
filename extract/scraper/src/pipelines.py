import dateparser

from itemadapter import ItemAdapter
from datetime import datetime
from scrapy.exceptions import DropItem


class DefaultValuesPipeline:
    def process_item(self, item, spider):
        for field in item.fields:
            item.setdefault(field, None)
        return item


class DatePipeline:
    today = datetime.now().date()

    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        if dateparser.parse(adapter.get("date")).date() == self.today:
            return item
        raise DropItem(f"Data not from today({self.today.strftime('%d/%m/%Y')})")

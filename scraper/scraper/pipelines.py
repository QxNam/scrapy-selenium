# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html

# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
import pymongo

# class ScraperPipeline:
#     def process_item(self, item, spider):
#         return item

class ScraperPipeline:

    def __init__(self, mongo_uri, mongo_db, mongo_collection):
        self.mongo_uri = mongo_uri
        self.mongo_db = mongo_db
        self.mongo_collection = mongo_collection

    @classmethod
    def from_crawler(cls, crawler):
        # Get MongoDB settings from Scrapy settings
        return cls(
            mongo_uri=crawler.settings.get('MONGO_URI'),
            mongo_db=crawler.settings.get('MONGO_DATABASE', 'scrapy_db'),
            mongo_collection=crawler.settings.get('MONGO_COLLECTION', 'vnexpress')
        )

    def open_spider(self, spider):
        # Initialize MongoDB connection
        self.client = pymongo.MongoClient(self.mongo_uri)
        self.db = self.client[self.mongo_db]
        self.collection = self.db[self.mongo_collection]
        print("Connected to MongoDB")

    def close_spider(self, spider):
        # Close MongoDB connection when the spider closes
        self.client.close()
        print("Closed MongoDB connection")

    def process_item(self, item, spider):
        # Insert item into the MongoDB collection
        self.collection.insert_one(ItemAdapter(item).asdict())
        print("Inserted:", ItemAdapter(item).asdict())
        return item
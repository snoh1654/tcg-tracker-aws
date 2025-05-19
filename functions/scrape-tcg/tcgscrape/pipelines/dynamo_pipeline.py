from collections import deque
from itemadapter import ItemAdapter
import boto3

from .utils.item_utils import sanitize_value, generate_pk, generate_historical_sk, filter_static_data
from .utils.dynamodb_utils import batch_write, update_latest

class DynamoDBPipeline:
    DB_NAME = "tcg"
    BUCKET_NAME = "tcg-imgs"

    BUFF_LEN = 25

    PK = "pk"
    SK = "sk"
    KEY_ATTRS = [PK, SK]
    DYNAMIC_ATTRS = ["price", "currency", "source", "timestamp"]

    def __init__(self):
        self.buffer = deque([])

    def open_spider(self, spider):
        """
        Called when process begins.
        """

        print("BEGIN PIPELINE")
        # access DynamoDB
        self.dynamodb = boto3.resource("dynamodb")
        # access the tcg table
        self.table = self.dynamodb.Table(self.DB_NAME)
        # access s3
        self.s3 = boto3.resource("s3")
        # access tcg bucket
        self.bucket = self.s3.Bucket(self.BUCKET_NAME)
        # Adds all TCG Set information to DB prior to processing TCG scrape data
        self._process_sets(spider.URL_MAPPINGS)
    
    def close_spider(self, spider):
        """
        Called when process ends.
        """

        if self.buffer:
            batch_write(self.buffer)
            self.buffer.clear()

        print("Close DynamoDB Pipeline!")

    def process_item(self, item, spider):
        """
        Called for every item that goes through the pipeline.
        """

        adapter = ItemAdapter(item)
        data_item = adapter.asdict()
        
        # Sanitize card_id and name
        data_item["card_id"] = sanitize_value(data_item["card_id"])
        data_item["name"] = sanitize_value(data_item["name"])

        # Write to Latest row individually
        print("Updating Latest Rows")
        update_latest(data_item)

        # Add SK for historical row 
        self._append_to_buffer(data_item)

        # if buffer hits 25, batch write the buffer to DynamoDB
        if len(self.buffer) == self.BUFF_LEN:
            batch_write(self.buffer)
            self.buffer.clear()
        
        return item

    def _process_sets(self, url_mappings):
        """
        Process sets from the spider's URL_MAPPINGS.

        This ensures that there is a valid set row in the tcg table for every stored tcg set.
        """

        buffer = []
        for tcg_name, set_name in url_mappings.get_tcg_sets():
            set_row = {
                self.PK: f"TCG#{tcg_name}",
                self.SK: f"SET#{set_name}",
                "tcg_name": tcg_name,
                "set_name": set_name
            }
            buffer.append(set_row)

            if len(buffer) == self.BUFF_LEN:
                batch_write(buffer)
                buffer.clear()
        
        # batch write remaining rows in buffer
        if len(buffer):
            batch_write(buffer)

    def _append_to_buffer(self, data_item):
        """
        Generates a historical PK and SK and filters static data from data_item.
        Then, adds the item to buffer
        """

        data_item[self.PK] = generate_pk(data_item)
        data_item[self.SK] = generate_historical_sk(data_item)
        
        data_item = filter_static_data(data_item)

        self.buffer.append(data_item)
import os
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from tcgscrape.spiders.tcg_republic_spider import TCGRepublicSpider


def lambda_handler(event, context):
    # Requires cold start to run due to issue with scrapy dependency not restarting in same process
    # Not a problem since this function is ran once every 12 hours

    print("AWS Lambda function started!")

    os.environ.setdefault("SCRAPY_SETTINGS_MODULE", "tcgscrape.settings")
    settings = get_project_settings()
    process = CrawlerProcess(settings=settings)

    process.crawl(TCGRepublicSpider)
    process.start()
    
    print("Scraping completed!")
    return {"status": "SUCCESS"}

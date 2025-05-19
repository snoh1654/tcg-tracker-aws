from datetime import datetime, timezone
import scrapy
from tcgscrape.items import CardItems
from tcgscrape.utils.url_mapping import URL_Mapping

class TCGRepublicSpider(scrapy.Spider):
    """
    Spider to scrape TCG card prices from TCG Republic.
    """
    name = "tcg_republic"
    DOMAIN_NAME = "tcgrepublic.com"
    CURRENCY = "USD"
    allowed_domains = ["tcgrepublic.com"]
    URL_MAPPINGS = URL_Mapping([(URL_Mapping.ONE_PIECE, "Pillars of Strength", "https://tcgrepublic.com/category/subcategory_page_8014.html"),
                                (URL_Mapping.WEISS_SCHWARZ, "Oshi no Ko", "https://tcgrepublic.com/category/subcategory_page_8932.html"), 
                                (URL_Mapping.WEISS_SCHWARZ, "Oshi no Ko Vol. 2", "https://tcgrepublic.com/category/subcategory_page_10066.html")
                                (URL_Mapping.WEISS_SCHWARZ, "Frieren: Beyond Journey's End", "https://tcgrepublic.com/category/subcategory_page_8972.html")
                                (URL_Mapping.WEISS_SCHWARZ, "Chainsaw Man", "https://tcgrepublic.com/category/subcategory_page_8397.html")
                                (URL_Mapping.WEISS_SCHWARZ, "Kaguya-sama: Love Is War", "https://tcgrepublic.com/category/subcategory_page_3456.html")
                                (URL_Mapping.WEISS_SCHWARZ, "Kaguya-sama: Love is War Season 2", "https://tcgrepublic.com/category/subcategory_page_7286.html")
                                ]) 


    def start_requests(self):
        for tcg_name, set_name in self.URL_MAPPINGS.get_tcg_sets():
            yield scrapy.Request(
                url=self.URL_MAPPINGS.get_url(tcg_name, set_name),
                callback=self.parse,
                meta={"tcg_name": tcg_name, "set_name": set_name}
            )

    def parse(self, response):
        """
        Parses the product listing page for TCG cards. 
        Extracts card info and yields items, then follows to next pagination if present.
        """
        tcg_name = response.meta["tcg_name"]
        set_name = response.meta["set_name"]

        # Iterate over card containers
        for card_selector in response.css("#main_container > *"):
            yield self.parse_card(card_selector, tcg_name, set_name)

        # Handles pagination
        next_page = response.css('li.go_next a::attr("href")').get()
        if next_page:
            yield response.follow(
                next_page,
                callback=self.parse,
                meta=response.meta
            )

    def parse_card(self, card_selector, tcg_name, set_name):
        """
        Parses a single card entry from the listing page.
        """
        card_item = CardItems()

        card_item["card_id"] = card_selector.css(".product_thumbnail_caption span::text").get()
        card_item["name"] = card_selector.css(".product_thumbnail_caption span::text").get()
        card_item["timestamp"] = datetime.now(timezone.utc).isoformat()
        card_item["company"] = "TCG Republic"

        card_item["price"] = self.extract_price(card_selector)
        card_item["currency"] = self.CURRENCY

        card_item["tcg_name"] = tcg_name
        card_item["set_name"] = set_name

        card_item["image_src"] = self.extract_image_src(card_selector)

        return card_item

    def extract_price(self, selector):
        """
        Extracts price from the card selector. 
        """
        try:
            price_integer = selector.css(".price_with_unit_integer::text").get()
            price_fractional = selector.css(".price_with_unit_fractional::text").get()
            # Build the price like "12.99" from "12" + "99"
            if price_integer and price_fractional:
                return f"{price_integer}.{price_fractional}"
        except Exception:
            pass
        return "Not Available"

    def extract_image_src(self, selector):
        """
        Extracts image source, prefixing with the domain if needed.
        """
        try:
            src_relative = selector.css(".product_thumbnail_image img::attr(src)").get()
            if src_relative:
                return f"{self.DOMAIN_NAME}{src_relative}"
        except Exception:
            pass
        return "Not Available"

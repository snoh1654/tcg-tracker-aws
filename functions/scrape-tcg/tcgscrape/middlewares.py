# Define here the models for your spider middleware

import random

class RandomHeaderMiddleware:
    USER_AGENT_LIST = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Firefox/111.0",
    ]
    
    REFERER_LIST = [
        "https://google.com/",
        "https://bing.com/",
        "https://duckduckgo.com/",
    ]

    def __init__(self, user_agent=None, referer=None):
        self.session_user_agent = random.choice(self.USER_AGENT_LIST)

    def process_request(self, request, spider):
        request.headers['User-Agent'] = self.session_user_agent
        request.headers['Referer'] = random.choice(self.REFERER_LIST)
        request.headers['Accept-Language'] = "en-US,en;q=0.5"
    
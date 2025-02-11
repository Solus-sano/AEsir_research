from firecrawl.firecrawl import FirecrawlApp
import asyncio
import json
from Agent.config import GLOBAL_CONFIG

Crawl_app = FirecrawlApp(GLOBAL_CONFIG.FIRE_CRAWL_API_KEY)
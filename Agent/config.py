import argparse


class Config:
    def __init__(self):
        #llm setting
        self.LLM_MODULE = None
        self.LLM_BASE_URL = None
        self.LLM_API_KEY = None
        self.LLM_TEMPERATURE = 0.7
        
        #firecrawl setting
        self.FIRE_CRAWL_URL = None
        self.FIRE_CRAWL_API_KEY = None
        
        #dfs research setting
        self.ConcurrencyLimit = 8
        self.MAX_DEPTH = 3
        self.MAX_BREADTH = 3
        self.MAX_LEARNINGS = 3

GLOBAL_CONFIG = Config()

def set_config(args: argparse.Namespace):
    GLOBAL_CONFIG.LLM_MODULE = args.llm_module
    GLOBAL_CONFIG.LLM_BASE_URL = args.llm_base_url
    GLOBAL_CONFIG.LLM_API_KEY = args.llm_api_key
    
    GLOBAL_CONFIG.FIRE_CRAWL_URL = args.firecrawl_base_url
    GLOBAL_CONFIG.FIRE_CRAWL_API_KEY = args.firecrawl_api_key

    GLOBAL_CONFIG.MAX_BREADTH = args.max_breadth
    GLOBAL_CONFIG.MAX_DEPTH = args.max_depth

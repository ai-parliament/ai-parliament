# ai/src/agents/cached_wikipedia.py
from langchain_community.tools import WikipediaQueryRun
from langchain_community.utilities import WikipediaAPIWrapper
from langchain_core.tools import Tool
from .cache_manager import CacheManager

class CachedWikipediaTool:
    """Wikipedia tool with built-in caching"""
    
    def __init__(self, cache_manager: CacheManager, lang: str = "pl"):
        self.cache_manager = cache_manager
        self.wiki_wrapper = WikipediaAPIWrapper(lang=lang)
        self.base_tool = WikipediaQueryRun(api_wrapper=self.wiki_wrapper)
    
    def search(self, query: str) -> str:
        """Search Wikipedia with caching"""
        # Check cache first
        cached_result = self.cache_manager.get_wikipedia(query)
        if cached_result:
            print(f"📚 Wikipedia cache hit: {query[:50]}...")
            return cached_result
        
        # If not cached, fetch from Wikipedia
        print(f"🔍 Wikipedia API call: {query[:50]}...")
        result = self.base_tool.run(query)
        
        # Save to cache
        self.cache_manager.save_wikipedia(query, result)
        
        return result
    
    def as_tool(self) -> Tool:
        """Return as LangChain tool"""
        return Tool(
            name="Wikipedia",
            func=self.search,
            description="Search Wikipedia. Input should be a search query."
        )
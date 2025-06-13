# ai/src/agents/cache_manager.py
import os
import json
import pickle
import hashlib
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from pathlib import Path

class CacheManager:
    """Unified cache manager for all agents"""
    
    def __init__(self, cache_dir: str = "cache"):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
        
        # Create subdirectories
        self.politicians_dir = self.cache_dir / "politicians"
        self.parties_dir = self.cache_dir / "parties"
        self.wikipedia_dir = self.cache_dir / "wikipedia"
        
        for dir in [self.politicians_dir, self.parties_dir, self.wikipedia_dir]:
            dir.mkdir(exist_ok=True)
    
    def _get_file_age_days(self, file_path: Path) -> float:
        """Get age of file in days"""
        if not file_path.exists():
            return float('inf')
        
        file_time = datetime.fromtimestamp(file_path.stat().st_mtime)
        return (datetime.now() - file_time).days
    
    # ========== POLITICIAN CACHING ==========
    
    def get_politician_cache_path(self, first_name: str, last_name: str, party: str) -> Path:
        """Get cache file path for politician"""
        key = f"{first_name}_{last_name}_{party}".lower().replace(" ", "_")
        return self.politicians_dir / f"{key}.json"
    
    def get_politician(self, first_name: str, last_name: str, party: str, max_age_days: int = 30) -> Optional[Dict]:
        """Get cached politician data"""
        cache_path = self.get_politician_cache_path(first_name, last_name, party)
        
        if cache_path.exists() and self._get_file_age_days(cache_path) < max_age_days:
            with open(cache_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return None
    
    def save_politician(self, first_name: str, last_name: str, party: str, data: Dict):
        """Save politician data to cache"""
        cache_path = self.get_politician_cache_path(first_name, last_name, party)
        
        data['cached_at'] = datetime.now().isoformat()
        data['cache_version'] = '1.0'
        
        with open(cache_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    # ========== PARTY CACHING ==========
    
    def get_party_cache_path(self, party_name: str, acronym: str) -> Path:
        """Get cache file path for party"""
        key = f"{party_name}_{acronym}".lower().replace(" ", "_")
        return self.parties_dir / f"{key}.json"
    
    def get_party(self, party_name: str, acronym: str, max_age_days: int = 30) -> Optional[Dict]:
        """Get cached party data"""
        cache_path = self.get_party_cache_path(party_name, acronym)
        
        if cache_path.exists() and self._get_file_age_days(cache_path) < max_age_days:
            with open(cache_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return None
    
    def save_party(self, party_name: str, acronym: str, data: Dict):
        """Save party data to cache"""
        cache_path = self.get_party_cache_path(party_name, acronym)
        
        data['cached_at'] = datetime.now().isoformat()
        data['cache_version'] = '1.0'
        
        with open(cache_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    # ========== WIKIPEDIA CACHING ==========
    
    def get_wikipedia_cache_path(self, query: str) -> Path:
        """Get cache file path for Wikipedia query"""
        # Create a hash of the query for filename
        query_hash = hashlib.md5(query.encode()).hexdigest()[:12]
        safe_query = "".join(c for c in query if c.isalnum() or c in (' ', '-'))[:50]
        return self.wikipedia_dir / f"{safe_query}_{query_hash}.json"
    
    def get_wikipedia(self, query: str, max_age_days: int = 7) -> Optional[str]:
        """Get cached Wikipedia result"""
        cache_path = self.get_wikipedia_cache_path(query)
        
        if cache_path.exists() and self._get_file_age_days(cache_path) < max_age_days:
            with open(cache_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data['content']
        return None
    
    def save_wikipedia(self, query: str, content: str):
        """Save Wikipedia result to cache"""
        cache_path = self.get_wikipedia_cache_path(query)
        
        data = {
            'query': query,
            'content': content,
            'cached_at': datetime.now().isoformat()
        }
        
        with open(cache_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    # ========== CACHE MANAGEMENT ==========
    
    def clear_old_cache(self, max_age_days: int = 30):
        """Clear cache files older than specified days"""
        cleared = 0
        for dir in [self.politicians_dir, self.parties_dir, self.wikipedia_dir]:
            for file in dir.glob("*.json"):
                if self._get_file_age_days(file) > max_age_days:
                    file.unlink()
                    cleared += 1
        
        print(f"🧹 Cleared {cleared} old cache files")
        return cleared
    
    def get_cache_stats(self) -> Dict:
        """Get cache statistics"""
        stats = {
            'politicians': len(list(self.politicians_dir.glob("*.json"))),
            'parties': len(list(self.parties_dir.glob("*.json"))),
            'wikipedia': len(list(self.wikipedia_dir.glob("*.json"))),
            'total_size_mb': sum(
                f.stat().st_size for f in self.cache_dir.rglob("*.json")
            ) / 1024 / 1024
        }
        return stats

# Create global cache instance
cache_manager = CacheManager()
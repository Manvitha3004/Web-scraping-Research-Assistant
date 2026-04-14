import os
import json
import hashlib
from typing import Any, Optional
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class SimpleCache:
    """Simple file-based cache system with TTL support"""

    def __init__(self, cache_dir: str = "./cache", ttl_hours: int = 24):
        self.cache_dir = cache_dir
        self.ttl = timedelta(hours=ttl_hours)
        
        # Create cache directory if it doesn't exist
        os.makedirs(cache_dir, exist_ok=True)

    def _get_cache_key(self, key: str) -> str:
        """Generate MD5 hash of the cache key"""
        return hashlib.md5(key.encode()).hexdigest()

    def _get_cache_file_path(self, key: str) -> str:
        """Get the full path for a cache file"""
        cache_key = self._get_cache_key(key)
        return os.path.join(self.cache_dir, f"{cache_key}.json")

    def get(self, key: str) -> Optional[Any]:
        """Get value from cache if it exists and hasn't expired"""
        try:
            cache_file = self._get_cache_file_path(key)
            
            if not os.path.exists(cache_file):
                return None
            
            with open(cache_file, 'r', encoding='utf-8') as f:
                cache_data = json.load(f)
            
            # Check if cache has expired
            created_at = datetime.fromisoformat(cache_data['created_at'])
            if datetime.now() - created_at > self.ttl:
                # Delete expired cache
                os.remove(cache_file)
                return None
            
            return cache_data['data']
        
        except Exception as e:
            logger.warning(f"Error reading cache for key {key}: {e}")
            return None

    def set(self, key: str, value: Any) -> bool:
        """Store value in cache"""
        try:
            cache_file = self._get_cache_file_path(key)
            cache_data = {
                'created_at': datetime.now().isoformat(),
                'data': value
            }
            
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, ensure_ascii=False, indent=2)
            
            return True
        
        except Exception as e:
            logger.error(f"Error writing cache for key {key}: {e}")
            return False

    def clear(self) -> None:
        """Clear all cache files"""
        try:
            for file in os.listdir(self.cache_dir):
                if file.endswith('.json'):
                    os.remove(os.path.join(self.cache_dir, file))
            logger.info("Cache cleared successfully")
        except Exception as e:
            logger.error(f"Error clearing cache: {e}")

    def delete(self, key: str) -> bool:
        """Delete a specific cache entry"""
        try:
            cache_file = self._get_cache_file_path(key)
            if os.path.exists(cache_file):
                os.remove(cache_file)
                return True
            return False
        except Exception as e:
            logger.error(f"Error deleting cache for key {key}: {e}")
            return False

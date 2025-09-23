"""
Intelligent Caching System
Unified caching with predictive pre-loading and performance auto-tuning.
"""

import asyncio
import hashlib
import json
import logging
import pickle
import sqlite3
import threading
import time
import weakref
from collections import defaultdict, OrderedDict
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple, Union, Callable
import diskcache as dc
from concurrent.futures import ThreadPoolExecutor
import psutil


@dataclass
class CacheEntry:
    """Cache entry with metadata."""
    key: str
    value: Any
    created_at: float
    last_accessed: float
    access_count: int
    size_bytes: int
    ttl: Optional[float] = None
    tags: Optional[Set[str]] = None
    
    def is_expired(self) -> bool:
        """Check if entry is expired."""
        if self.ttl is None:
            return False
        return time.time() > (self.created_at + self.ttl)
    
    def age_seconds(self) -> float:
        """Get age in seconds."""
        return time.time() - self.created_at
    
    def time_since_access(self) -> float:
        """Get time since last access in seconds."""
        return time.time() - self.last_accessed


@dataclass
class AccessPattern:
    """Access pattern for predictive caching."""
    key: str
    access_times: List[float]
    access_intervals: List[float]
    frequency: float
    last_prediction: Optional[float] = None
    
    def predict_next_access(self) -> Optional[float]:
        """Predict next access time based on patterns."""
        if len(self.access_intervals) < 2:
            return None
        
        # Simple prediction based on average interval
        avg_interval = sum(self.access_intervals) / len(self.access_intervals)
        predicted_time = self.access_times[-1] + avg_interval
        
        # Weight recent intervals more heavily
        if len(self.access_intervals) >= 3:
            recent_weight = 0.6
            older_weight = 0.4
            recent_avg = sum(self.access_intervals[-3:]) / min(3, len(self.access_intervals))
            older_avg = sum(self.access_intervals[:-3]) / max(1, len(self.access_intervals) - 3)
            weighted_interval = recent_avg * recent_weight + older_avg * older_weight
            predicted_time = self.access_times[-1] + weighted_interval
        
        self.last_prediction = predicted_time
        return predicted_time


class CacheStats:
    """Cache statistics tracker."""
    
    def __init__(self):
        self.hits = 0
        self.misses = 0
        self.evictions = 0
        self.preloads = 0
        self.preload_hits = 0
        self.total_size = 0
        self.start_time = time.time()
        self._lock = threading.Lock()
    
    def record_hit(self):
        with self._lock:
            self.hits += 1
    
    def record_miss(self):
        with self._lock:
            self.misses += 1
    
    def record_eviction(self):
        with self._lock:
            self.evictions += 1
    
    def record_preload(self):
        with self._lock:
            self.preloads += 1
    
    def record_preload_hit(self):
        with self._lock:
            self.preload_hits += 1
    
    def get_hit_rate(self) -> float:
        total = self.hits + self.misses
        return (self.hits / total * 100) if total > 0 else 0
    
    def get_preload_effectiveness(self) -> float:
        return (self.preload_hits / self.preloads * 100) if self.preloads > 0 else 0
    
    def get_stats(self) -> Dict[str, Any]:
        with self._lock:
            total_requests = self.hits + self.misses
            uptime = time.time() - self.start_time
            
            return {
                'hits': self.hits,
                'misses': self.misses,
                'hit_rate': self.get_hit_rate(),
                'evictions': self.evictions,
                'preloads': self.preloads,
                'preload_hits': self.preload_hits,
                'preload_effectiveness': self.get_preload_effectiveness(),
                'total_requests': total_requests,
                'requests_per_second': total_requests / uptime if uptime > 0 else 0,
                'uptime_seconds': uptime,
                'total_size': self.total_size
            }


class LRUCache:
    """Enhanced LRU cache with size limits and TTL support."""
    
    def __init__(self, max_size: int = 1000, max_memory_mb: int = 100):
        self.max_size = max_size
        self.max_memory_bytes = max_memory_mb * 1024 * 1024
        self.cache: OrderedDict[str, CacheEntry] = OrderedDict()
        self.current_memory = 0
        self._lock = threading.RLock()
        self.stats = CacheStats()
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        with self._lock:
            if key not in self.cache:
                self.stats.record_miss()
                return None
            
            entry = self.cache[key]
            
            # Check expiration
            if entry.is_expired():
                del self.cache[key]
                self.current_memory -= entry.size_bytes
                self.stats.record_miss()
                return None
            
            # Update access info
            entry.last_accessed = time.time()
            entry.access_count += 1
            
            # Move to end (most recently used)
            self.cache.move_to_end(key)
            
            self.stats.record_hit()
            return entry.value
    
    def put(self, key: str, value: Any, ttl: Optional[float] = None, 
            tags: Optional[Set[str]] = None) -> bool:
        """Put value in cache."""
        with self._lock:
            # Calculate size
            try:
                size_bytes = len(pickle.dumps(value))
            except:
                size_bytes = 1024  # Default size estimate
            
            # Check if value is too large
            if size_bytes > self.max_memory_bytes:
                return False
            
            current_time = time.time()
            
            # Remove existing entry if present
            if key in self.cache:
                old_entry = self.cache[key]
                self.current_memory -= old_entry.size_bytes
                del self.cache[key]
            
            # Evict entries if necessary
            while (len(self.cache) >= self.max_size or 
                   self.current_memory + size_bytes > self.max_memory_bytes):
                if not self.cache:
                    break
                self._evict_lru()
            
            # Create new entry
            entry = CacheEntry(
                key=key,
                value=value,
                created_at=current_time,
                last_accessed=current_time,
                access_count=1,
                size_bytes=size_bytes,
                ttl=ttl,
                tags=tags
            )
            
            self.cache[key] = entry
            self.current_memory += size_bytes
            self.stats.total_size = len(self.cache)
            
            return True
    
    def _evict_lru(self):
        """Evict least recently used entry."""
        if not self.cache:
            return
        
        key, entry = self.cache.popitem(last=False)
        self.current_memory -= entry.size_bytes
        self.stats.record_eviction()
    
    def remove(self, key: str) -> bool:
        """Remove entry from cache."""
        with self._lock:
            if key in self.cache:
                entry = self.cache[key]
                self.current_memory -= entry.size_bytes
                del self.cache[key]
                self.stats.total_size = len(self.cache)
                return True
            return False
    
    def clear(self):
        """Clear all entries."""
        with self._lock:
            self.cache.clear()
            self.current_memory = 0
            self.stats.total_size = 0
    
    def get_entries_by_tag(self, tag: str) -> List[CacheEntry]:
        """Get all entries with specific tag."""
        with self._lock:
            return [entry for entry in self.cache.values() 
                   if entry.tags and tag in entry.tags]
    
    def remove_by_tag(self, tag: str) -> int:
        """Remove all entries with specific tag."""
        with self._lock:
            to_remove = [key for key, entry in self.cache.items() 
                        if entry.tags and tag in entry.tags]
            
            for key in to_remove:
                self.remove(key)
            
            return len(to_remove)
    
    def cleanup_expired(self) -> int:
        """Remove expired entries."""
        with self._lock:
            expired_keys = [key for key, entry in self.cache.items() 
                           if entry.is_expired()]
            
            for key in expired_keys:
                self.remove(key)
            
            return len(expired_keys)


class PredictiveEngine:
    """Predictive engine for cache warming."""
    
    def __init__(self, db_path: str = ":memory:"):
        self.db_path = db_path
        self.patterns: Dict[str, AccessPattern] = {}
        self.prediction_threshold = 0.7  # Confidence threshold for predictions
        self._lock = threading.Lock()
        self.logger = logging.getLogger(__name__)
        
        # Initialize database
        self._init_db()
    
    def _init_db(self):
        """Initialize SQLite database for pattern storage."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS access_patterns (
                    key TEXT PRIMARY KEY,
                    access_times TEXT,
                    access_intervals TEXT,
                    frequency REAL,
                    last_prediction REAL
                )
            """)
    
    def record_access(self, key: str):
        """Record access for pattern learning."""
        with self._lock:
            current_time = time.time()
            
            if key not in self.patterns:
                self.patterns[key] = AccessPattern(
                    key=key,
                    access_times=[current_time],
                    access_intervals=[],
                    frequency=1.0
                )
            else:
                pattern = self.patterns[key]
                
                # Calculate interval from last access
                if pattern.access_times:
                    interval = current_time - pattern.access_times[-1]
                    pattern.access_intervals.append(interval)
                    
                    # Keep only recent intervals (last 20)
                    if len(pattern.access_intervals) > 20:
                        pattern.access_intervals = pattern.access_intervals[-20:]
                
                pattern.access_times.append(current_time)
                
                # Keep only recent access times (last 50)
                if len(pattern.access_times) > 50:
                    pattern.access_times = pattern.access_times[-50:]
                
                # Update frequency (accesses per hour)
                if len(pattern.access_times) >= 2:
                    time_span = pattern.access_times[-1] - pattern.access_times[0]
                    pattern.frequency = len(pattern.access_times) / (time_span / 3600) if time_span > 0 else 1.0
    
    def get_predictions(self, lookahead_seconds: float = 3600) -> List[Tuple[str, float, float]]:
        """Get predictions for keys likely to be accessed soon."""
        predictions = []
        current_time = time.time()
        
        with self._lock:
            for key, pattern in self.patterns.items():
                if len(pattern.access_intervals) < 2:
                    continue
                
                predicted_time = pattern.predict_next_access()
                if predicted_time is None:
                    continue
                
                # Check if prediction is within lookahead window
                if predicted_time <= current_time + lookahead_seconds:
                    # Calculate confidence based on pattern consistency
                    if len(pattern.access_intervals) >= 3:
                        # Coefficient of variation (lower = more consistent)
                        mean_interval = sum(pattern.access_intervals) / len(pattern.access_intervals)
                        variance = sum((x - mean_interval) ** 2 for x in pattern.access_intervals) / len(pattern.access_intervals)
                        std_dev = variance ** 0.5
                        cv = std_dev / mean_interval if mean_interval > 0 else 1.0
                        confidence = max(0.1, 1.0 - cv)
                    else:
                        confidence = 0.5
                    
                    if confidence >= self.prediction_threshold:
                        predictions.append((key, predicted_time, confidence))
        
        # Sort by predicted time
        predictions.sort(key=lambda x: x[1])
        return predictions
    
    def save_patterns(self):
        """Save patterns to database."""
        with sqlite3.connect(self.db_path) as conn:
            with self._lock:
                for pattern in self.patterns.values():
                    conn.execute("""
                        INSERT OR REPLACE INTO access_patterns 
                        (key, access_times, access_intervals, frequency, last_prediction)
                        VALUES (?, ?, ?, ?, ?)
                    """, (
                        pattern.key,
                        json.dumps(pattern.access_times),
                        json.dumps(pattern.access_intervals),
                        pattern.frequency,
                        pattern.last_prediction
                    ))
    
    def load_patterns(self):
        """Load patterns from database."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("SELECT * FROM access_patterns")
                
                with self._lock:
                    for row in cursor:
                        key, access_times_json, intervals_json, frequency, last_pred = row
                        
                        self.patterns[key] = AccessPattern(
                            key=key,
                            access_times=json.loads(access_times_json),
                            access_intervals=json.loads(intervals_json),
                            frequency=frequency,
                            last_prediction=last_pred
                        )
        except Exception as e:
            self.logger.error(f"Error loading patterns: {e}")


class IntelligentCache:
    """Main intelligent cache with predictive warming and auto-tuning."""
    
    def __init__(self, 
                 max_size: int = 1000,
                 max_memory_mb: int = 100,
                 disk_cache_dir: Optional[str] = None,
                 enable_prediction: bool = True,
                 auto_tune: bool = True):
        
        # Initialize components
        self.memory_cache = LRUCache(max_size, max_memory_mb)
        self.disk_cache = dc.Cache(disk_cache_dir or "./intelligent_cache") if disk_cache_dir != ":memory:" else None
        self.predictive_engine = PredictiveEngine() if enable_prediction else None
        
        # Configuration
        self.enable_prediction = enable_prediction
        self.auto_tune = auto_tune
        self.warming_enabled = True
        
        # Auto-tuning parameters
        self.target_hit_rate = 80.0  # Target hit rate percentage
        self.tune_interval = 300  # Auto-tune every 5 minutes
        self.last_tune_time = time.time()
        
        # Background tasks
        self.executor = ThreadPoolExecutor(max_workers=2, thread_name_prefix="cache")
        self.warming_task = None
        self.cleanup_task = None
        
        # Monitoring
        self.logger = logging.getLogger(__name__)
        self.preload_callbacks: Dict[str, Callable[[], Any]] = {}
        
        # Start background tasks
        self._start_background_tasks()
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get value from cache with predictive learning."""
        # Try memory cache first
        value = self.memory_cache.get(key)
        
        if value is not None:
            # Record access for prediction
            if self.predictive_engine:
                self.predictive_engine.record_access(key)
            return value
        
        # Try disk cache
        if self.disk_cache:
            try:
                value = self.disk_cache.get(key, default=None)
                if value is not None:
                    # Promote to memory cache
                    self.memory_cache.put(key, value)
                    if self.predictive_engine:
                        self.predictive_engine.record_access(key)
                    return value
            except Exception as e:
                self.logger.error(f"Error reading from disk cache: {e}")
        
        return default
    
    def put(self, key: str, value: Any, ttl: Optional[float] = None, 
            tags: Optional[Set[str]] = None, disk_persist: bool = False) -> bool:
        """Put value in cache."""
        # Store in memory cache
        success = self.memory_cache.put(key, value, ttl, tags)
        
        # Store in disk cache if requested
        if disk_persist and self.disk_cache:
            try:
                expire_time = int(ttl) if ttl else None
                self.disk_cache.set(key, value, expire=expire_time)
            except Exception as e:
                self.logger.error(f"Error writing to disk cache: {e}")
        
        return success
    
    def remove(self, key: str) -> bool:
        """Remove key from all cache levels."""
        memory_removed = self.memory_cache.remove(key)
        disk_removed = False
        
        if self.disk_cache:
            try:
                disk_removed = self.disk_cache.delete(key)
            except Exception as e:
                self.logger.error(f"Error removing from disk cache: {e}")
        
        return memory_removed or disk_removed
    
    def register_preload_callback(self, key: str, callback: Callable[[], Any]):
        """Register callback for predictive preloading."""
        self.preload_callbacks[key] = callback
    
    def warm_cache(self, keys: List[str]):
        """Manually warm cache with specific keys."""
        if not self.warming_enabled:
            return
        
        def _warm():
            for key in keys:
                if key in self.preload_callbacks:
                    try:
                        value = self.preload_callbacks[key]()
                        self.put(key, value)
                        self.memory_cache.stats.record_preload()
                        self.logger.debug(f"Preloaded key: {key}")
                    except Exception as e:
                        self.logger.error(f"Error preloading {key}: {e}")
        
        self.executor.submit(_warm)
    
    def _start_background_tasks(self):
        """Start background maintenance tasks."""
        if self.enable_prediction:
            self.warming_task = self.executor.submit(self._predictive_warming_loop)
        
        self.cleanup_task = self.executor.submit(self._cleanup_loop)
    
    def _predictive_warming_loop(self):
        """Background task for predictive cache warming."""
        while True:
            try:
                if not self.warming_enabled or not self.predictive_engine:
                    time.sleep(60)
                    continue
                
                # Get predictions
                predictions = self.predictive_engine.get_predictions(lookahead_seconds=1800)  # 30 minutes
                
                # Warm cache for predicted keys
                for key, predicted_time, confidence in predictions[:10]:  # Top 10 predictions
                    if key in self.preload_callbacks:
                        # Check if key is already in cache
                        if self.memory_cache.get(key) is None:
                            try:
                                value = self.preload_callbacks[key]()
                                self.put(key, value)
                                self.memory_cache.stats.record_preload()
                                self.logger.debug(f"Predictively loaded {key} (confidence: {confidence:.2f})")
                            except Exception as e:
                                self.logger.error(f"Error predictively loading {key}: {e}")
                
                # Auto-tune if enabled
                if self.auto_tune and time.time() - self.last_tune_time > self.tune_interval:
                    self._auto_tune()
                    self.last_tune_time = time.time()
                
                # Save patterns periodically
                if self.predictive_engine:
                    self.predictive_engine.save_patterns()
                
                time.sleep(60)  # Check every minute
                
            except Exception as e:
                self.logger.error(f"Error in predictive warming loop: {e}")
                time.sleep(60)
    
    def _cleanup_loop(self):
        """Background task for cache cleanup."""
        while True:
            try:
                # Clean expired entries
                expired_count = self.memory_cache.cleanup_expired()
                if expired_count > 0:
                    self.logger.debug(f"Cleaned up {expired_count} expired entries")
                
                # Clean disk cache if available
                if self.disk_cache:
                    try:
                        self.disk_cache.expire()
                    except Exception as e:
                        self.logger.error(f"Error expiring disk cache: {e}")
                
                time.sleep(300)  # Clean every 5 minutes
                
            except Exception as e:
                self.logger.error(f"Error in cleanup loop: {e}")
                time.sleep(300)
    
    def _auto_tune(self):
        """Auto-tune cache parameters based on performance."""
        stats = self.memory_cache.stats.get_stats()
        current_hit_rate = stats['hit_rate']
        
        self.logger.info(f"Auto-tuning: current hit rate {current_hit_rate:.1f}%, target {self.target_hit_rate}%")
        
        # Adjust cache size based on hit rate
        if current_hit_rate < self.target_hit_rate * 0.9:  # Below 90% of target
            # Increase cache size if memory allows
            system_memory = psutil.virtual_memory()
            if system_memory.percent < 80:  # Less than 80% memory usage
                new_size = min(self.memory_cache.max_size * 1.2, self.memory_cache.max_size + 200)
                new_memory = min(self.memory_cache.max_memory_bytes * 1.1, 
                               self.memory_cache.max_memory_bytes + 50 * 1024 * 1024)
                
                self.memory_cache.max_size = int(new_size)
                self.memory_cache.max_memory_bytes = int(new_memory)
                
                self.logger.info(f"Increased cache limits: size={self.memory_cache.max_size}, "
                               f"memory={self.memory_cache.max_memory_bytes // (1024*1024)}MB")
        
        elif current_hit_rate > self.target_hit_rate * 1.1:  # Above 110% of target
            # Decrease cache size to free resources
            new_size = max(self.memory_cache.max_size * 0.9, 100)
            new_memory = max(self.memory_cache.max_memory_bytes * 0.9, 10 * 1024 * 1024)
            
            self.memory_cache.max_size = int(new_size)
            self.memory_cache.max_memory_bytes = int(new_memory)
            
            self.logger.info(f"Decreased cache limits: size={self.memory_cache.max_size}, "
                           f"memory={self.memory_cache.max_memory_bytes // (1024*1024)}MB")
        
        # Adjust prediction threshold based on preload effectiveness
        preload_effectiveness = stats['preload_effectiveness']
        if self.predictive_engine and preload_effectiveness < 50:  # Less than 50% effective
            self.predictive_engine.prediction_threshold = min(0.9, 
                                                            self.predictive_engine.prediction_threshold + 0.1)
            self.logger.info(f"Increased prediction threshold to {self.predictive_engine.prediction_threshold}")
        elif self.predictive_engine and preload_effectiveness > 80:  # More than 80% effective
            self.predictive_engine.prediction_threshold = max(0.3, 
                                                            self.predictive_engine.prediction_threshold - 0.1)
            self.logger.info(f"Decreased prediction threshold to {self.predictive_engine.prediction_threshold}")
    
    def get_comprehensive_stats(self) -> Dict[str, Any]:
        """Get comprehensive cache statistics."""
        stats = self.memory_cache.stats.get_stats()
        
        # Add disk cache stats if available
        if self.disk_cache:
            try:
                disk_stats = {
                    'disk_size': len(self.disk_cache),
                    'disk_volume_path': str(self.disk_cache.directory)
                }
                stats.update(disk_stats)
            except Exception as e:
                stats['disk_error'] = str(e)
        
        # Add predictive engine stats
        if self.predictive_engine:
            with self.predictive_engine._lock:
                pattern_count = len(self.predictive_engine.patterns)
                active_patterns = sum(1 for p in self.predictive_engine.patterns.values() 
                                    if len(p.access_intervals) >= 2)
                
                stats.update({
                    'total_patterns': pattern_count,
                    'active_patterns': active_patterns,
                    'prediction_threshold': self.predictive_engine.prediction_threshold
                })
        
        # Add system info
        stats.update({
            'system_memory_percent': psutil.virtual_memory().percent,
            'cache_memory_mb': self.memory_cache.current_memory // (1024 * 1024),
            'max_cache_memory_mb': self.memory_cache.max_memory_bytes // (1024 * 1024),
            'auto_tune_enabled': self.auto_tune,
            'warming_enabled': self.warming_enabled
        })
        
        return stats
    
    def shutdown(self):
        """Shutdown cache and cleanup resources."""
        self.warming_enabled = False
        
        # Save patterns before shutdown
        if self.predictive_engine:
            self.predictive_engine.save_patterns()
        
        # Shutdown executor
        self.executor.shutdown(wait=True)
        
        # Close disk cache
        if self.disk_cache:
            self.disk_cache.close()
        
        self.logger.info("Intelligent cache shutdown complete")


# Example usage and testing
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    # Initialize cache
    cache = IntelligentCache(
        max_size=1000,
        max_memory_mb=50,
        enable_prediction=True,
        auto_tune=True
    )
    
    # Example preload callback
    def load_expensive_data(key: str):
        """Simulate expensive data loading."""
        time.sleep(0.1)  # Simulate delay
        return f"expensive_data_for_{key}"
    
    # Register preload callbacks
    for i in range(10):
        key = f"data_{i}"
        cache.register_preload_callback(key, lambda k=key: load_expensive_data(k))
    
    # Example usage
    cache.put("test_key", "test_value", ttl=3600)
    value = cache.get("test_key")
    print(f"Retrieved: {value}")
    
    # Print stats
    stats = cache.get_comprehensive_stats()
    print(f"Cache stats: {json.dumps(stats, indent=2)}")
    
    print("Intelligent Cache initialized successfully!")

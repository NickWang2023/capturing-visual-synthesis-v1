'''
  @ Date: 2026-07-03
  @ Author: 明哥升级版
  @ Description: 性能优化模块单元测试（简化版）
'''
import pytest
import time
import numpy as np
from unittest.mock import Mock, patch

# 检查torch是否可用
try:
    import torch
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False

from easymocap.performance.optimizer import (
    CacheManager,
    timer,
)


class TestCacheManager:
    """测试缓存管理器"""
    
    def test_init(self):
        """测试初始化"""
        cache = CacheManager(max_size=100)
        assert cache.max_size == 100
        assert len(cache.cache) == 0
    
    def test_get_set(self):
        """测试获取和设置"""
        cache = CacheManager()
        cache.set("key1", "value1")
        assert cache.get("key1") == "value1"
        assert cache.hits == 1
    
    def test_get_miss(self):
        """测试缓存未命中"""
        cache = CacheManager()
        assert cache.get("nonexistent") is None
        assert cache.misses == 1
    
    def test_max_size(self):
        """测试最大容量"""
        cache = CacheManager(max_size=2)
        cache.set("key1", "value1")
        cache.set("key2", "value2")
        cache.set("key3", "value3")
        assert len(cache.cache) == 2
        assert cache.get("key1") is None
    
    def test_clear(self):
        """测试清除缓存"""
        cache = CacheManager()
        cache.set("key1", "value1")
        cache.clear()
        assert len(cache.cache) == 0
    
    def test_get_stats(self):
        """测试获取统计信息"""
        cache = CacheManager(max_size=10)
        cache.set("key1", "value1")
        cache.get("key1")
        cache.get("nonexistent")
        stats = cache.get_stats()
        assert stats['size'] == 1
        assert stats['hits'] == 1
        assert stats['misses'] == 1


class TestTimerDecorator:
    """测试计时器装饰器"""
    
    def test_timer(self):
        """测试计时器"""
        @timer
        def fast_function():
            return "done"
        assert fast_function() == "done"
    
    def test_preserves_name(self):
        """测试保留函数名"""
        @timer
        def my_function():
            pass
        assert my_function.__name__ == "my_function"


@pytest.mark.skipif(not TORCH_AVAILABLE, reason="torch未安装")
class TestGPUManager:
    """测试GPU管理器"""
    
    def test_import(self):
        from easymocap.performance.optimizer import GPUManager
        assert GPUManager is not None


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])

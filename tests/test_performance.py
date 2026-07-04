'''
  @ Date: 2026-07-03
  @ Author: 明哥升级版
  @ Description: 性能优化模块单元测试
'''
import pytest
import time
import numpy as np
from unittest.mock import Mock, patch

# 可选导入torch
torch = pytest.importorskip("torch", reason="torch未安装，跳过性能测试")

# 导入被测试的模块
from easymocap.performance.optimizer import (
    PerformanceOptimizer,
    CacheManager,
    timer,
    memory_efficient,
    GPUManager
)


class TestPerformanceOptimizer:
    """测试性能优化器"""
    
    def test_init_with_amp(self):
        """测试启用AMP初始化"""
        with patch('torch.cuda.is_available', return_value=True):
            optimizer = PerformanceOptimizer(use_amp=True, accumulation_steps=4)
            
            assert optimizer.use_amp is True
            assert optimizer.accumulation_steps == 4
            assert optimizer.scaler is not None
    
    def test_init_without_amp(self):
        """测试禁用AMP初始化"""
        optimizer = PerformanceOptimizer(use_amp=False, accumulation_steps=1)
        
        assert optimizer.use_amp is False
        assert optimizer.accumulation_steps == 1
        assert optimizer.scaler is None
    
    def test_autocast_with_amp(self):
        """测试启用AMP的autocast"""
        with patch('torch.cuda.is_available', return_value=True):
            optimizer = PerformanceOptimizer(use_amp=True)
            
            with optimizer.autocast():
                # 这里应该在autocast上下文中
                pass
    
    def test_autocast_without_amp(self):
        """测试禁用AMP的autocast"""
        optimizer = PerformanceOptimizer(use_amp=False)
        
        with optimizer.autocast():
            # 这里应该不在autocast上下文中
            pass


class TestCacheManager:
    """测试缓存管理器"""
    
    def test_init(self):
        """测试初始化"""
        cache = CacheManager(max_size=100)
        
        assert cache.max_size == 100
        assert len(cache.cache) == 0
        assert cache.hits == 0
        assert cache.misses == 0
    
    def test_get_set(self):
        """测试获取和设置"""
        cache = CacheManager()
        
        # 设置缓存
        cache.set("key1", "value1")
        
        # 获取缓存
        result = cache.get("key1")
        assert result == "value1"
        assert cache.hits == 1
        assert cache.misses == 0
    
    def test_get_miss(self):
        """测试缓存未命中"""
        cache = CacheManager()
        
        result = cache.get("nonexistent")
        
        assert result is None
        assert cache.hits == 0
        assert cache.misses == 1
    
    def test_max_size(self):
        """测试最大容量"""
        cache = CacheManager(max_size=2)
        
        cache.set("key1", "value1")
        cache.set("key2", "value2")
        cache.set("key3", "value3")  # 应该删除key1
        
        assert len(cache.cache) == 2
        assert cache.get("key1") is None
        assert cache.get("key2") == "value2"
        assert cache.get("key3") == "value3"
    
    def test_clear(self):
        """测试清除缓存"""
        cache = CacheManager()
        
        cache.set("key1", "value1")
        cache.set("key2", "value2")
        cache.get("key1")  # 命中
        cache.get("nonexistent")  # 未命中
        
        cache.clear()
        
        assert len(cache.cache) == 0
        assert cache.hits == 0
        assert cache.misses == 0
    
    def test_get_stats(self):
        """测试获取统计信息"""
        cache = CacheManager(max_size=10)
        
        cache.set("key1", "value1")
        cache.set("key2", "value2")
        cache.get("key1")  # 命中
        cache.get("key1")  # 命中
        cache.get("nonexistent")  # 未命中
        
        stats = cache.get_stats()
        
        assert stats['size'] == 2
        assert stats['max_size'] == 10
        assert stats['hits'] == 2
        assert stats['misses'] == 1
        assert abs(stats['hit_rate'] - 2/3) < 0.001


class TestTimerDecorator:
    """测试计时器装饰器"""
    
    def test_timer(self):
        """测试计时器"""
        @timer
        def slow_function():
            time.sleep(0.1)
            return "done"
        
        result = slow_function()
        
        assert result == "done"
    
    def test_timer_preserves_name(self):
        """测试计时器保留函数名"""
        @timer
        def my_function():
            pass
        
        assert my_function.__name__ == "my_function"


class TestMemoryEfficientDecorator:
    """测试内存高效装饰器"""
    
    def test_memory_efficient(self):
        """测试内存高效装饰器"""
        @memory_efficient(batch_size=32)
        def my_function():
            return "done"
        
        result = my_function()
        
        assert result == "done"
    
    def test_memory_efficient_preserves_name(self):
        """测试内存高效装饰器保留函数名"""
        @memory_efficient()
        def my_function():
            pass
        
        assert my_function.__name__ == "my_function"


class TestGPUManager:
    """测试GPU管理器"""
    
    @patch('torch.cuda.is_available', return_value=False)
    def test_get_gpu_info_no_gpu(self, mock_is_available):
        """测试没有GPU时获取信息"""
        info = GPUManager.get_gpu_info()
        
        assert info['available'] is False
    
    @patch('torch.cuda.is_available', return_value=True)
    @patch('torch.cuda.device_count', return_value=1)
    @patch('torch.cuda.current_device', return_value=0)
    @patch('torch.cuda.get_device_name', return_value="NVIDIA A100")
    @patch('torch.cuda.get_device_properties')
    @patch('torch.cuda.memory_allocated', return_value=1024*1024*100)
    @patch('torch.cuda.memory_reserved', return_value=1024*1024*200)
    def test_get_gpu_info_with_gpu(
        self,
        mock_memory_reserved,
        mock_memory_allocated,
        mock_get_device_properties,
        mock_get_device_name,
        mock_current_device,
        mock_device_count,
        mock_is_available
    ):
        """测试有GPU时获取信息"""
        mock_properties = Mock()
        mock_properties.total_mem = 1024*1024*1024*80  # 80GB
        mock_get_device_properties.return_value = mock_properties
        
        info = GPUManager.get_gpu_info()
        
        assert info['available'] is True
        assert info['device_count'] == 1
        assert info['devices'][0]['name'] == "NVIDIA A100"
    
    @patch('torch.cuda.is_available', return_value=True)
    @patch('torch.cuda.empty_cache')
    def test_clear_cache(self, mock_empty_cache, mock_is_available):
        """测试清除缓存"""
        GPUManager.clear_cache()
        
        mock_empty_cache.assert_called_once()
    
    @patch('torch.cuda.is_available', return_value=False)
    def test_get_optimal_batch_size_no_gpu(self, mock_is_available):
        """测试没有GPU时获取最优批次大小"""
        model = Mock()
        input_shape = (3, 224, 224)
        
        batch_size = GPUManager.get_optimal_batch_size(model, input_shape)
        
        assert batch_size == 32
    
    @patch('torch.cuda.is_available', return_value=True)
    @patch('torch.cuda.get_device_properties')
    def test_get_optimal_batch_size_a100(self, mock_get_device_properties, mock_is_available):
        """测试A100 GPU的最优批次大小"""
        mock_properties = Mock()
        mock_properties.total_mem = 1024*1024*1024*80  # 80GB
        mock_get_device_properties.return_value = mock_properties
        
        model = Mock()
        input_shape = (3, 224, 224)
        
        batch_size = GPUManager.get_optimal_batch_size(model, input_shape)
        
        assert batch_size == 64


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])

'''
  @ Date: 2026-07-03
  @ Author: 明哥升级版
  @ Description: 性能优化模块 - Issue #10
'''
import logging
import time
from typing import Optional, Dict, Any, Callable
from functools import wraps
from contextlib import contextmanager

import torch
import numpy as np

logger = logging.getLogger(__name__)


class PerformanceOptimizer:
    """
    性能优化器
    
    提供混合精度训练、梯度累积、内存优化等功能
    """
    
    def __init__(self, use_amp: bool = True, accumulation_steps: int = 1):
        """
        初始化性能优化器
        
        Args:
            use_amp: 是否使用混合精度训练
            accumulation_steps: 梯度累积步数
        """
        self.use_amp = use_amp and torch.cuda.is_available()
        self.accumulation_steps = accumulation_steps
        self.scaler = torch.cuda.amp.GradScaler() if self.use_amp else None
        
        if self.use_amp:
            logger.info("启用混合精度训练 (AMP)")
        logger.info(f"梯度累积步数: {accumulation_steps}")
    
    @contextmanager
    def autocast(self):
        """
        自动混合精度上下文管理器
        
        使用方法:
            with optimizer.autocast():
                output = model(input)
                loss = criterion(output, target)
        """
        if self.use_amp:
            with torch.cuda.amp.autocast():
                yield
        else:
            yield
    
    def backward(self, loss: torch.Tensor):
        """
        反向传播
        
        Args:
            loss: 损失值
        """
        if self.scaler is not None:
            self.scaler.scale(loss).backward()
        else:
            loss.backward()
    
    def step(self, optimizer: torch.optim.Optimizer):
        """
        优化器步骤
        
        Args:
            optimizer: 优化器
        """
        if self.scaler is not None:
            self.scaler.step(optimizer)
            self.scaler.update()
        else:
            optimizer.step()
    
    def zero_grad(self, optimizer: torch.optim.Optimizer):
        """
        清除梯度
        
        Args:
            optimizer: 优化器
        """
        optimizer.zero_grad()


class CacheManager:
    """
    缓存管理器
    
    提供结果缓存功能，避免重复计算
    """
    
    def __init__(self, max_size: int = 1000):
        """
        初始化缓存管理器
        
        Args:
            max_size: 缓存最大容量
        """
        self.cache: Dict[str, Any] = {}
        self.max_size = max_size
        self.hits = 0
        self.misses = 0
    
    def get(self, key: str) -> Optional[Any]:
        """
        获取缓存
        
        Args:
            key: 缓存键
        
        Returns:
            缓存值，如果不存在返回None
        """
        if key in self.cache:
            self.hits += 1
            return self.cache[key]
        self.misses += 1
        return None
    
    def set(self, key: str, value: Any):
        """
        设置缓存
        
        Args:
            key: 缓存键
            value: 缓存值
        """
        # 如果缓存已满，删除最早的条目
        if len(self.cache) >= self.max_size:
            oldest_key = next(iter(self.cache))
            del self.cache[oldest_key]
        
        self.cache[key] = value
    
    def clear(self):
        """清除所有缓存"""
        self.cache.clear()
        self.hits = 0
        self.misses = 0
    
    def get_stats(self) -> Dict[str, Any]:
        """
        获取缓存统计信息
        
        Returns:
            统计信息字典
        """
        total = self.hits + self.misses
        hit_rate = self.hits / total if total > 0 else 0
        
        return {
            'size': len(self.cache),
            'max_size': self.max_size,
            'hits': self.hits,
            'misses': self.misses,
            'hit_rate': hit_rate
        }


def timer(func: Callable) -> Callable:
    """
    计时器装饰器
    
    使用方法:
        @timer
        def my_function():
            pass
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        elapsed = end_time - start_time
        logger.info(f"{func.__name__} 执行时间: {elapsed:.3f}秒")
        return result
    return wrapper


def memory_efficient(batch_size: int = 32):
    """
    内存高效装饰器
    
    Args:
        batch_size: 批次大小
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # 清理GPU缓存
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
            
            result = func(*args, **kwargs)
            
            # 再次清理
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
            
            return result
        return wrapper
    return decorator


class GPUManager:
    """
    GPU管理器
    
    提供GPU资源管理功能
    """
    
    @staticmethod
    def get_gpu_info() -> Dict[str, Any]:
        """
        获取GPU信息
        
        Returns:
            GPU信息字典
        """
        if not torch.cuda.is_available():
            return {'available': False}
        
        gpu_info = {
            'available': True,
            'device_count': torch.cuda.device_count(),
            'current_device': torch.cuda.current_device(),
            'devices': []
        }
        
        for i in range(torch.cuda.device_count()):
            device_info = {
                'index': i,
                'name': torch.cuda.get_device_name(i),
                'memory_total': torch.cuda.get_device_properties(i).total_mem,
                'memory_allocated': torch.cuda.memory_allocated(i),
                'memory_cached': torch.cuda.memory_reserved(i)
            }
            gpu_info['devices'].append(device_info)
        
        return gpu_info
    
    @staticmethod
    def clear_cache():
        """清除GPU缓存"""
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
            logger.info("GPU缓存已清除")
    
    @staticmethod
    def get_optimal_batch_size(model: torch.nn.Module, input_shape: tuple) -> int:
        """
        获取最优批次大小
        
        Args:
            model: 模型
            input_shape: 输入形状
        
        Returns:
            最优批次大小
        """
        if not torch.cuda.is_available():
            return 32
        
        # 简单启发式方法
        gpu_memory = torch.cuda.get_device_properties(0).total_mem
        memory_gb = gpu_memory / (1024 ** 3)
        
        if memory_gb >= 80:  # A100 80GB
            return 64
        elif memory_gb >= 40:  # A100 40GB
            return 32
        elif memory_gb >= 24:  # A10
            return 16
        elif memory_gb >= 16:  # V100
            return 8
        else:
            return 4

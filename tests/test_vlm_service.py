'''
  @ Date: 2026-07-03
  @ Author: 明哥升级版
  @ Description: VLM服务模块单元测试（简化版）
'''
import pytest
import numpy as np
from unittest.mock import Mock, patch, MagicMock
from typing import List

# 检查torch是否可用
try:
    import torch
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False

from easymocap.vlm.service import VLMConfig, Detection


class TestVLMConfig:
    """测试VLM配置"""
    
    def test_default_config(self):
        """测试默认配置"""
        config = VLMConfig()
        assert config.sam_model_type == "vit_h"
    
    def test_custom_config(self):
        """测试自定义配置"""
        config = VLMConfig(
            sam_model_path="/mock/path/sam.pth",
            device="cpu"
        )
        assert config.sam_model_path == "/mock/path/sam.pth"
        assert config.device == "cpu"


class TestDetection:
    """测试检测结果"""
    
    def test_creation(self):
        """测试创建检测结果"""
        d = Detection(
            bbox=[10, 20, 100, 200],
            confidence=0.95,
            label="person"
        )
        assert d.bbox == [10, 20, 100, 200]
        assert d.confidence == 0.95
        assert d.mask is None


@pytest.mark.skipif(not TORCH_AVAILABLE, reason="torch未安装")
class TestVLMServiceWithTorch:
    """测试VLM服务（需要torch）"""
    
    def test_service_import(self):
        from easymocap.vlm.service import VLMService
        assert VLMService is not None


class TestVLMServiceWithoutTorch:
    """测试VLM服务（无torch）"""
    
    @pytest.mark.skipif(TORCH_AVAILABLE, reason="torch已安装")
    def test_config_still_works(self):
        config = VLMConfig(device="cpu")
        assert config.device == "cpu"


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])

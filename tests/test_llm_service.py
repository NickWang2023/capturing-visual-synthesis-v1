'''
  @ Date: 2026-07-03
  @ Author: 明哥升级版
  @ Description: LLM服务模块单元测试（简化版）
'''
import pytest
import json
from unittest.mock import Mock, patch, MagicMock
from typing import Dict, Any

# 检查openai是否可用
try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

from easymocap.llm.service import (
    LLMConfig,
    TaskComplexity,
    TaskComplexityLevel,
    OPENAI_AVAILABLE as MODULE_OPENAI_AVAILABLE
)


class TestLLMConfig:
    """测试LLM配置"""
    
    def test_default_config(self):
        """测试默认配置"""
        config = LLMConfig(api_key="test_key")
        assert config.api_key == "test_key"
        assert config.model == "gpt-4"
        assert config.temperature == 0.7


class TestTaskComplexity:
    """测试任务复杂度"""
    
    def test_creation(self):
        """测试创建任务复杂度"""
        c = TaskComplexity(
            level=TaskComplexityLevel.MEDIUM,
            estimated_time=300,
            recommended_gpu="A100",
            priority=5
        )
        assert c.level == TaskComplexityLevel.MEDIUM
        assert c.estimated_time == 300
    
    def test_to_dict(self):
        """测试转换为字典"""
        c = TaskComplexity(
            level=TaskComplexityLevel.SIMPLE,
            estimated_time=60,
            recommended_gpu="A10",
            priority=3
        )
        d = c.to_dict()
        assert d['level'] == 'simple'
        assert d['estimated_time'] == 60


@pytest.mark.skipif(not MODULE_OPENAI_AVAILABLE, reason="openai未安装")
class TestLLMServiceWithOpenAI:
    """测试LLM服务（需要openai）"""
    
    @pytest.fixture
    def service(self):
        from easymocap.llm.service import LLMService
        config = LLMConfig(api_key="test_key")
        with patch('easymocap.llm.service.OpenAI') as mock_openai:
            mock_client = Mock()
            mock_openai.return_value = mock_client
            svc = LLMService(config)
            svc.client = mock_client
            return svc
    
    def test_initialization(self, service):
        assert service.client is not None


class TestLLMServiceWithoutOpenAI:
    """测试LLM服务（无openai）"""
    
    @pytest.mark.skipif(MODULE_OPENAI_AVAILABLE, reason="openai已安装")
    def test_import_error(self):
        from easymocap.llm.service import LLMService
        config = LLMConfig(api_key="test_key")
        with pytest.raises(ImportError):
            LLMService(config)


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])

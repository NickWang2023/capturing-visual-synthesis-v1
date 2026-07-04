'''
  @ Date: 2026-07-03
  @ Author: 明哥升级版
  @ Description: LLM服务模块单元测试
'''
import pytest
import json
from unittest.mock import Mock, patch, MagicMock
from typing import Dict, Any

# 导入被测试的模块
from easymocap.llm.service import (
    LLMService,
    LLMConfig,
    TaskComplexity,
    TaskComplexityLevel
)


class TestLLMConfig:
    """测试LLM配置"""
    
    def test_default_config(self):
        """测试默认配置"""
        config = LLMConfig(api_key="test_key")
        
        assert config.api_key == "test_key"
        assert config.base_url == "https://api.openai.com/v1"
        assert config.model == "gpt-4"
        assert config.temperature == 0.7
        assert config.max_tokens == 2000
        assert config.timeout == 60
    
    def test_custom_config(self):
        """测试自定义配置"""
        config = LLMConfig(
            api_key="custom_key",
            base_url="https://custom.api.com/v1",
            model="gpt-3.5-turbo",
            temperature=0.5,
            max_tokens=1000,
            timeout=30
        )
        
        assert config.api_key == "custom_key"
        assert config.base_url == "https://custom.api.com/v1"
        assert config.model == "gpt-3.5-turbo"
        assert config.temperature == 0.5
        assert config.max_tokens == 1000
        assert config.timeout == 30
    
    @patch.dict('os.environ', {
        'OPENAI_API_KEY': 'env_key',
        'OPENAI_BASE_URL': 'https://env.api.com/v1',
        'LLM_MODEL': 'gpt-4-turbo',
        'LLM_TEMPERATURE': '0.8',
        'LLM_MAX_TOKENS': '3000',
        'LLM_TIMEOUT': '90'
    })
    def test_from_env(self):
        """测试从环境变量加载配置"""
        config = LLMConfig.from_env()
        
        assert config.api_key == "env_key"
        assert config.base_url == "https://env.api.com/v1"
        assert config.model == "gpt-4-turbo"
        assert config.temperature == 0.8
        assert config.max_tokens == 3000
        assert config.timeout == 90


class TestTaskComplexity:
    """测试任务复杂度"""
    
    def test_task_complexity_creation(self):
        """测试创建任务复杂度"""
        complexity = TaskComplexity(
            level=TaskComplexityLevel.MEDIUM,
            estimated_time=300,
            recommended_gpu="A100",
            priority=5
        )
        
        assert complexity.level == TaskComplexityLevel.MEDIUM
        assert complexity.estimated_time == 300
        assert complexity.recommended_gpu == "A100"
        assert complexity.priority == 5
    
    def test_task_complexity_to_dict(self):
        """测试转换为字典"""
        complexity = TaskComplexity(
            level=TaskComplexityLevel.SIMPLE,
            estimated_time=60,
            recommended_gpu="A10",
            priority=3
        )
        
        result = complexity.to_dict()
        
        assert result['level'] == 'simple'
        assert result['estimated_time'] == 60
        assert result['recommended_gpu'] == 'A10'
        assert result['priority'] == 3


class TestLLMService:
    """测试LLM服务"""
    
    @pytest.fixture
    def mock_config(self):
        """创建模拟配置"""
        return LLMConfig(api_key="test_key")
    
    @pytest.fixture
    def service(self, mock_config):
        """创建LLM服务实例"""
        with patch('easymocap.llm.service.OpenAI') as mock_openai:
            mock_client = Mock()
            mock_openai.return_value = mock_client
            service = LLMService(mock_config)
            service.client = mock_client
            return service
    
    def test_service_initialization(self, service, mock_config):
        """测试服务初始化"""
        assert service.config == mock_config
        assert service.client is not None
    
    def test_analyze_task_complexity(self, service):
        """测试任务复杂度分析"""
        # 模拟API响应
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = json.dumps({
            "level": "medium",
            "estimated_time": 300,
            "recommended_gpu": "A100",
            "priority": 5
        })
        
        service.client.chat.completions.create.return_value = mock_response
        
        video_info = {
            "duration": 60,
            "resolution": "1920x1080",
            "fps": 30,
            "person_count": 1,
            "scene_type": "indoor"
        }
        
        result = service.analyze_task_complexity(video_info)
        
        assert result.level == TaskComplexityLevel.MEDIUM
        assert result.estimated_time == 300
        assert result.recommended_gpu == "A100"
        assert result.priority == 5
    
    def test_generate_parameters(self, service):
        """测试参数生成"""
        # 模拟API响应
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = json.dumps({
            "detection": {"confidence_threshold": 0.5},
            "optimization": {"learning_rate": 0.001}
        })
        
        service.client.chat.completions.create.return_value = mock_response
        
        result = service.generate_parameters("mv1p", {"duration": 60})
        
        assert "detection" in result
        assert "optimization" in result
    
    def test_diagnose_error(self, service):
        """测试错误诊断"""
        # 模拟API响应
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = json.dumps({
            "error_type": "CUDA Out of Memory",
            "root_cause": "Batch size too large",
            "solution": "Reduce batch size",
            "prevention": "Use gradient accumulation"
        })
        
        service.client.chat.completions.create.return_value = mock_response
        
        result = service.diagnose_error("CUDA out of memory")
        
        assert result['error_type'] == 'CUDA Out of Memory'
        assert result['solution'] == 'Reduce batch size'
    
    def test_chat(self, service):
        """测试对话功能"""
        # 模拟API响应
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "你好！我是AI助手。"
        
        service.client.chat.completions.create.return_value = mock_response
        
        result = service.chat("你好")
        
        assert result == "你好！我是AI助手。"
    
    def test_analyze_task_complexity_error(self, service):
        """测试任务复杂度分析错误处理"""
        service.client.chat.completions.create.side_effect = Exception("API Error")
        
        video_info = {"duration": 60}
        
        with pytest.raises(RuntimeError) as exc_info:
            service.analyze_task_complexity(video_info)
        
        assert "无法分析任务复杂度" in str(exc_info.value)


class TestLLMServiceGlobal:
    """测试全局LLM服务"""
    
    def test_get_llm_service(self):
        """测试获取全局服务"""
        from easymocap.llm.service import get_llm_service, _llm_service
        
        # 重置全局实例
        import easymocap.llm.service as module
        module._llm_service = None
        
        with patch('easymocap.llm.service.LLMService') as mock_class:
            mock_instance = Mock()
            mock_class.return_value = mock_instance
            
            service = get_llm_service()
            
            assert service == mock_instance
            mock_class.assert_called_once()
    
    def test_init_llm_service(self):
        """测试初始化全局服务"""
        from easymocap.llm.service import init_llm_service
        
        config = LLMConfig(api_key="test_key")
        
        with patch('easymocap.llm.service.LLMService') as mock_class:
            mock_instance = Mock()
            mock_class.return_value = mock_instance
            
            service = init_llm_service(config)
            
            assert service == mock_instance
            mock_class.assert_called_once_with(config)


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])

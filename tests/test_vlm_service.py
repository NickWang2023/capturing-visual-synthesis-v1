'''
  @ Date: 2026-07-03
  @ Author: 明哥升级版
  @ Description: VLM服务模块单元测试
'''
import pytest
import numpy as np
from unittest.mock import Mock, patch, MagicMock
from typing import List

# 可选导入torch
torch = pytest.importorskip("torch", reason="torch未安装，跳过VLM测试")

# 导入被测试的模块
from easymocap.vlm.service import (
    VLMService,
    VLMConfig,
    Detection
)


class TestVLMConfig:
    """测试VLM配置"""
    
    def test_default_config(self):
        """测试默认配置"""
        config = VLMConfig()
        
        assert config.sam_model_path == "/opt/mocap-system/models/sam_vit_h.pth"
        assert config.sam_model_type == "vit_h"
        assert config.device == "cuda" if config.device == "cuda" else "cpu"
    
    def test_custom_config(self):
        """测试自定义配置"""
        config = VLMConfig(
            sam_model_path="/custom/path/sam.pth",
            sam_model_type="vit_l",
            device="cpu"
        )
        
        assert config.sam_model_path == "/custom/path/sam.pth"
        assert config.sam_model_type == "vit_l"
        assert config.device == "cpu"
    
    @patch.dict('os.environ', {
        'SAM_MODEL_PATH': '/env/path/sam.pth',
        'SAM_MODEL_TYPE': 'vit_b',
        'VLM_DEVICE': 'cpu'
    })
    def test_from_env(self):
        """测试从环境变量加载配置"""
        config = VLMConfig.from_env()
        
        assert config.sam_model_path == "/env/path/sam.pth"
        assert config.sam_model_type == "vit_b"
        assert config.device == "cpu"


class TestDetection:
    """测试检测结果"""
    
    def test_detection_creation(self):
        """测试创建检测结果"""
        detection = Detection(
            bbox=[10, 20, 100, 200],
            confidence=0.95,
            label="person"
        )
        
        assert detection.bbox == [10, 20, 100, 200]
        assert detection.confidence == 0.95
        assert detection.label == "person"
        assert detection.mask is None
    
    def test_detection_with_mask(self):
        """测试带mask的检测结果"""
        mask = np.zeros((100, 100), dtype=bool)
        mask[10:50, 20:60] = True
        
        detection = Detection(
            bbox=[10, 20, 100, 200],
            confidence=0.95,
            label="person",
            mask=mask
        )
        
        assert detection.mask is not None
        assert detection.mask.shape == (100, 100)


class TestVLMService:
    """测试VLM服务"""
    
    @pytest.fixture
    def mock_config(self):
        """创建模拟配置"""
        return VLMConfig(
            sam_model_path="/mock/path/sam.pth",
            device="cpu"
        )
    
    @pytest.fixture
    def service(self, mock_config):
        """创建VLM服务实例"""
        with patch('easymocap.vlm.service.VLMService._init_models'):
            service = VLMService(mock_config)
            return service
    
    def test_service_initialization(self, service, mock_config):
        """测试服务初始化"""
        assert service.config == mock_config
        assert service.sam_predictor is None
        assert service.grounding_dino is None
    
    def test_segment_person_no_model(self, service):
        """测试没有模型时的分割"""
        image = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)
        bbox = [10, 20, 50, 80]
        
        result = service.segment_person(image, bbox)
        
        assert result is None
    
    def test_segment_person_with_model(self, service):
        """测试有模型时的分割"""
        # 模拟SAM预测器
        mock_predictor = Mock()
        mock_predictor.predict.return_value = (
            np.array([[[True, False], [False, True]]]),  # masks
            np.array([0.9]),  # scores
            None  # logits
        )
        service.sam_predictor = mock_predictor
        
        image = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)
        bbox = [10, 20, 50, 80]
        
        result = service.segment_person(image, bbox)
        
        assert result is not None
        mock_predictor.set_image.assert_called_once()
        mock_predictor.predict.assert_called_once()
    
    def test_detect_with_grounding_no_model(self, service):
        """测试没有模型时的检测"""
        image = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)
        
        result = service.detect_with_grounding(image, "person")
        
        assert result == []
    
    def test_enhance_keypoints_high_confidence(self, service):
        """测试高置信度关键点增强"""
        image = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)
        keypoints = np.array([[10, 20], [30, 40], [50, 60]])
        confidence = np.array([0.9, 0.8, 0.95])
        
        result_keypoints, result_confidence = service.enhance_keypoints(
            image, keypoints, confidence
        )
        
        # 高置信度关键点应该保持不变
        np.testing.assert_array_equal(result_keypoints, keypoints)
        np.testing.assert_array_equal(result_confidence, confidence)
    
    def test_enhance_keypoints_low_confidence(self, service):
        """测试低置信度关键点增强"""
        image = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)
        keypoints = np.array([[10, 20], [30, 40], [50, 60]])
        confidence = np.array([0.1, 0.8, 0.2])  # 低置信度
        
        result_keypoints, result_confidence = service.enhance_keypoints(
            image, keypoints, confidence
        )
        
        # 当前实现应该返回原始值（待实现）
        np.testing.assert_array_equal(result_keypoints, keypoints)
        np.testing.assert_array_equal(result_confidence, confidence)
    
    def test_segment_multiple_persons(self, service):
        """测试多个人物分割"""
        # 模拟segment_person方法
        service.segment_person = Mock(return_value=np.ones((100, 100), dtype=bool))
        
        image = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)
        bboxes = [[10, 20, 50, 80], [60, 70, 100, 110]]
        
        result = service.segment_multiple_persons(image, bboxes)
        
        assert len(result) == 2
        assert service.segment_person.call_count == 2
    
    def test_batch_segment(self, service):
        """测试批量分割"""
        # 模拟segment_multiple_persons方法
        service.segment_multiple_persons = Mock(return_value=[
            np.ones((100, 100), dtype=bool),
            np.ones((100, 100), dtype=bool)
        ])
        
        images = [
            np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8),
            np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)
        ]
        bboxes_list = [
            [[10, 20, 50, 80]],
            [[60, 70, 100, 110]]
        ]
        
        result = service.batch_segment(images, bboxes_list)
        
        assert len(result) == 2
        assert service.segment_multiple_persons.call_count == 2


class TestVLMServiceGlobal:
    """测试全局VLM服务"""
    
    def test_get_vlm_service(self):
        """测试获取全局服务"""
        from easymocap.vlm.service import get_vlm_service
        
        # 重置全局实例
        import easymocap.vlm.service as module
        module._vlm_service = None
        
        with patch('easymocap.vlm.service.VLMService') as mock_class:
            mock_instance = Mock()
            mock_class.return_value = mock_instance
            
            service = get_vlm_service()
            
            assert service == mock_instance
            mock_class.assert_called_once()
    
    def test_init_vlm_service(self):
        """测试初始化全局服务"""
        from easymocap.vlm.service import init_vlm_service
        
        config = VLMConfig(device="cpu")
        
        with patch('easymocap.vlm.service.VLMService') as mock_class:
            mock_instance = Mock()
            mock_class.return_value = mock_instance
            
            service = init_vlm_service(config)
            
            assert service == mock_instance
            mock_class.assert_called_once_with(config)


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])

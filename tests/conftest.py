'''
  @ Date: 2026-07-03
  @ Author: 明哥升级版
  @ Description: pytest配置文件
'''
import pytest
import numpy as np
from typing import Dict, Any


def pytest_configure(config):
    """pytest配置"""
    config.addinivalue_line(
        "markers", "unit: 单元测试"
    )
    config.addinivalue_line(
        "markers", "integration: 集成测试"
    )
    config.addinivalue_line(
        "markers", "performance: 性能测试"
    )
    config.addinivalue_line(
        "markers", "slow: 慢速测试"
    )


@pytest.fixture
def sample_image():
    """创建示例图像"""
    return np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)


@pytest.fixture
def sample_keypoints():
    """创建示例关键点"""
    return np.random.rand(25, 2) * 100


@pytest.fixture
def sample_keypoints3d():
    """创建示例3D关键点"""
    return np.random.rand(25, 4)  # x, y, z, confidence


@pytest.fixture
def sample_bbox():
    """创建示例边界框"""
    return [10, 20, 100, 200]


@pytest.fixture
def sample_bboxes():
    """创建示例边界框列表"""
    return [
        [10, 20, 100, 200],
        [50, 60, 150, 250],
        [100, 100, 200, 300]
    ]


@pytest.fixture
def sample_video_info():
    """创建示例视频信息"""
    return {
        "duration": 60,
        "resolution": "1920x1080",
        "fps": 30,
        "person_count": 1,
        "scene_type": "indoor"
    }


@pytest.fixture
def mock_body_model():
    """创建模拟的body_model"""
    from unittest.mock import Mock
    
    model = Mock()
    model.model_type = 'smplx'
    model.device = 'cpu'
    model.init_params.return_value = {
        'Rh': np.zeros((1, 3)),
        'Th': np.zeros((1, 3)),
        'poses': np.zeros((1, 165)),
        'shapes': np.zeros((1, 10)),
        'expression': np.zeros((1, 10))
    }
    model.faces = np.zeros((1000, 3), dtype=np.int32)
    
    return model


@pytest.fixture
def mock_config():
    """创建模拟配置"""
    from unittest.mock import Mock
    
    config = Mock()
    config.model = 'smplx'
    config.device = 'cpu'
    config.OPT_R = False
    config.OPT_T = False
    config.OPT_POSE = False
    config.OPT_HAND = False
    config.OPT_EXPR = False
    config.ROBUST_3D = False
    
    return config


@pytest.fixture
def sample_params():
    """创建示例参数"""
    return {
        'Rh': np.zeros((1, 3)),
        'Th': np.zeros((1, 3)),
        'poses': np.zeros((1, 165)),
        'shapes': np.zeros((1, 10)),
        'expression': np.zeros((1, 10))
    }


@pytest.fixture
def sample_weight():
    """创建示例权重"""
    return {
        'smooth_body': 0.01,
        'smooth_poses': 0.001,
        'robust_3d': 1.0,
        'robust_2d': 0.5
    }

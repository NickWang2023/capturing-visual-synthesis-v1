'''
  VLM视觉大模型服务模块
  Issue #6: 实现VLM服务模块
'''
from .service import VLMService, get_vlm_service, init_vlm_service, VLMConfig, Detection

__all__ = ['VLMService', 'get_vlm_service', 'init_vlm_service', 'VLMConfig', 'Detection']

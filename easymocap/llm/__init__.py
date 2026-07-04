'''
  LLM大语言模型服务模块
  Issue #5: 实现LLM服务模块
'''
from .service import LLMService, get_llm_service, init_llm_service, LLMConfig, TaskComplexity

__all__ = ['LLMService', 'get_llm_service', 'init_llm_service', 'LLMConfig', 'TaskComplexity']

'''
  安全模块
  提供密钥管理、加密等功能
'''
from .secrets import SecretManager, get_secret_manager

__all__ = ['SecretManager', 'get_secret_manager']

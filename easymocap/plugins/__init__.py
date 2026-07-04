'''
  插件系统模块
  提供可扩展的插件机制
'''
from .manager import PluginManager, Plugin, PluginInfo

__all__ = ['PluginManager', 'Plugin', 'PluginInfo']

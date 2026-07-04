'''
  @ Date: 2026-07-03
  @ Author: 明哥升级版
  @ Description: 插件管理器
'''
import os
import sys
import importlib
import logging
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass
from pathlib import Path
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)


@dataclass
class PluginInfo:
    """插件信息"""
    name: str
    version: str
    description: str
    author: str
    enabled: bool = True


class Plugin(ABC):
    """插件基类"""
    
    @abstractmethod
    def get_info(self) -> PluginInfo:
        """获取插件信息"""
        pass
    
    @abstractmethod
    def initialize(self) -> bool:
        """初始化插件"""
        pass
    
    @abstractmethod
    def cleanup(self):
        """清理插件资源"""
        pass
    
    def on_event(self, event_name: str, data: Any):
        """处理事件"""
        pass


class PluginManager:
    """
    插件管理器
    
    管理插件的加载、初始化和事件分发
    """
    
    def __init__(self, plugin_dir: str = None):
        """
        初始化插件管理器
        
        Args:
            plugin_dir: 插件目录路径
        """
        self.plugin_dir = plugin_dir or os.path.join(os.path.dirname(__file__), 'builtin')
        self.plugins: Dict[str, Plugin] = {}
        self.plugin_info: Dict[str, PluginInfo] = {}
        self.event_handlers: Dict[str, List[Callable]] = {}
        
        logger.info(f"插件管理器初始化，插件目录: {self.plugin_dir}")
    
    def discover_plugins(self) -> List[str]:
        """
        发现插件
        
        Returns:
            发现的插件名称列表
        """
        discovered = []
        
        if not os.path.exists(self.plugin_dir):
            logger.warning(f"插件目录不存在: {self.plugin_dir}")
            return discovered
        
        for item in os.listdir(self.plugin_dir):
            plugin_path = os.path.join(self.plugin_dir, item)
            
            # 检查是否是Python包
            if os.path.isdir(plugin_path) and os.path.exists(os.path.join(plugin_path, '__init__.py')):
                discovered.append(item)
            # 检查是否是Python文件
            elif item.endswith('.py') and not item.startswith('_'):
                discovered.append(item[:-3])
        
        logger.info(f"发现 {len(discovered)} 个插件: {discovered}")
        return discovered
    
    def load_plugin(self, plugin_name: str) -> bool:
        """
        加载插件
        
        Args:
            plugin_name: 插件名称
        
        Returns:
            是否加载成功
        """
        try:
            # 动态导入插件模块
            module_path = f"easymocap.plugins.builtin.{plugin_name}"
            module = importlib.import_module(module_path)
            
            # 查找插件类
            plugin_class = None
            for attr_name in dir(module):
                attr = getattr(module, attr_name)
                if (isinstance(attr, type) and 
                    issubclass(attr, Plugin) and 
                    attr is not Plugin):
                    plugin_class = attr
                    break
            
            if plugin_class is None:
                logger.error(f"插件 {plugin_name} 中未找到Plugin子类")
                return False
            
            # 实例化插件
            plugin = plugin_class()
            info = plugin.get_info()
            
            # 初始化插件
            if plugin.initialize():
                self.plugins[plugin_name] = plugin
                self.plugin_info[plugin_name] = info
                logger.info(f"插件 {plugin_name} 加载成功")
                return True
            else:
                logger.error(f"插件 {plugin_name} 初始化失败")
                return False
                
        except Exception as e:
            logger.error(f"加载插件 {plugin_name} 失败: {e}")
            return False
    
    def load_all_plugins(self):
        """加载所有插件"""
        discovered = self.discover_plugins()
        
        for plugin_name in discovered:
            self.load_plugin(plugin_name)
        
        logger.info(f"已加载 {len(self.plugins)} 个插件")
    
    def get_plugin(self, plugin_name: str) -> Optional[Plugin]:
        """
        获取插件实例
        
        Args:
            plugin_name: 插件名称
        
        Returns:
            插件实例，如果不存在返回None
        """
        return self.plugins.get(plugin_name)
    
    def get_all_plugins(self) -> Dict[str, Plugin]:
        """获取所有已加载的插件"""
        return self.plugins.copy()
    
    def get_plugin_info(self, plugin_name: str) -> Optional[PluginInfo]:
        """获取插件信息"""
        return self.plugin_info.get(plugin_name)
    
    def register_event_handler(self, event_name: str, handler: Callable):
        """
        注册事件处理器
        
        Args:
            event_name: 事件名称
            handler: 处理函数
        """
        if event_name not in self.event_handlers:
            self.event_handlers[event_name] = []
        self.event_handlers[event_name].append(handler)
    
    def dispatch_event(self, event_name: str, data: Any = None):
        """
        分发事件
        
        Args:
            event_name: 事件名称
            data: 事件数据
        """
        if event_name in self.event_handlers:
            for handler in self.event_handlers[event_name]:
                try:
                    handler(data)
                except Exception as e:
                    logger.error(f"事件处理器执行失败: {e}")
        
        # 通知所有插件
        for plugin in self.plugins.values():
            try:
                plugin.on_event(event_name, data)
            except Exception as e:
                logger.error(f"插件事件处理失败: {e}")
    
    def unload_plugin(self, plugin_name: str):
        """
        卸载插件
        
        Args:
            plugin_name: 插件名称
        """
        if plugin_name in self.plugins:
            try:
                self.plugins[plugin_name].cleanup()
                del self.plugins[plugin_name]
                del self.plugin_info[plugin_name]
                logger.info(f"插件 {plugin_name} 已卸载")
            except Exception as e:
                logger.error(f"卸载插件 {plugin_name} 失败: {e}")
    
    def unload_all_plugins(self):
        """卸载所有插件"""
        for plugin_name in list(self.plugins.keys()):
            self.unload_plugin(plugin_name)


# 全局插件管理器实例
_plugin_manager: Optional[PluginManager] = None


def get_plugin_manager() -> PluginManager:
    """获取全局插件管理器"""
    global _plugin_manager
    if _plugin_manager is None:
        _plugin_manager = PluginManager()
    return _plugin_manager


def init_plugin_manager(plugin_dir: str = None) -> PluginManager:
    """初始化全局插件管理器"""
    global _plugin_manager
    _plugin_manager = PluginManager(plugin_dir)
    return _plugin_manager

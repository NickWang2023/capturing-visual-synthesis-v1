'''
  @ Date: 2026-07-03
  @ Author: 明哥升级版
  @ Description: 密钥管理器
'''
import os
import json
import logging
from typing import Optional, Dict, Any
from pathlib import Path
from cryptography.fernet import Fernet
import base64

logger = logging.getLogger(__name__)


class SecretManager:
    """
    密钥管理器
    
    支持多种密钥存储方式：
    - 环境变量
    - 加密文件
    - 外部密钥管理服务（如AWS Secrets Manager, HashiCorp Vault）
    """
    
    def __init__(self, secret_key: str = None):
        """
        初始化密钥管理器
        
        Args:
            secret_key: 加密密钥，用于加密/解密本地存储的密钥
        """
        self.secret_key = secret_key or os.getenv('SECRET_KEY', '')
        self._cipher = None
        
        if self.secret_key:
            # 生成Fernet密钥
            key = base64.urlsafe_b64encode(
                self.secret_key.encode()[:32].ljust(32, b'0')
            )
            self._cipher = Fernet(key)
        
        # 缓存
        self._cache: Dict[str, str] = {}
        
        logger.info("密钥管理器初始化完成")
    
    def get_secret(self, key: str, default: str = None) -> Optional[str]:
        """
        获取密钥
        
        优先级：
        1. 缓存
        2. 环境变量
        3. 加密文件
        4. 默认值
        
        Args:
            key: 密钥名称
            default: 默认值
        
        Returns:
            密钥值
        """
        # 1. 检查缓存
        if key in self._cache:
            return self._cache[key]
        
        # 2. 检查环境变量
        value = os.getenv(key)
        if value:
            self._cache[key] = value
            return value
        
        # 3. 检查加密文件
        value = self._read_from_encrypted_file(key)
        if value:
            self._cache[key] = value
            return value
        
        # 4. 返回默认值
        return default
    
    def set_secret(self, key: str, value: str, persist: bool = False):
        """
        设置密钥
        
        Args:
            key: 密钥名称
            value: 密钥值
            persist: 是否持久化到加密文件
        """
        # 更新缓存
        self._cache[key] = value
        
        # 更新环境变量
        os.environ[key] = value
        
        # 持久化到文件
        if persist:
            self._write_to_encrypted_file(key, value)
        
        logger.info(f"密钥 {key} 已更新")
    
    def delete_secret(self, key: str):
        """
        删除密钥
        
        Args:
            key: 密钥名称
        """
        # 从缓存删除
        self._cache.pop(key, None)
        
        # 从环境变量删除
        os.environ.pop(key, None)
        
        # 从加密文件删除
        self._delete_from_encrypted_file(key)
        
        logger.info(f"密钥 {key} 已删除")
    
    def _get_encrypted_file_path(self) -> Path:
        """获取加密文件路径"""
        return Path.home() / '.mocap' / 'secrets.enc'
    
    def _read_from_encrypted_file(self, key: str) -> Optional[str]:
        """从加密文件读取密钥"""
        if not self._cipher:
            return None
        
        file_path = self._get_encrypted_file_path()
        if not file_path.exists():
            return None
        
        try:
            # 读取加密数据
            encrypted_data = file_path.read_bytes()
            
            # 解密
            decrypted_data = self._cipher.decrypt(encrypted_data)
            
            # 解析JSON
            secrets = json.loads(decrypted_data.decode())
            
            return secrets.get(key)
        except Exception as e:
            logger.error(f"读取加密文件失败: {e}")
            return None
    
    def _write_to_encrypted_file(self, key: str, value: str):
        """写入密钥到加密文件"""
        if not self._cipher:
            logger.warning("未配置加密密钥，无法写入加密文件")
            return
        
        file_path = self._get_encrypted_file_path()
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            # 读取现有密钥
            secrets = {}
            if file_path.exists():
                encrypted_data = file_path.read_bytes()
                decrypted_data = self._cipher.decrypt(encrypted_data)
                secrets = json.loads(decrypted_data.decode())
            
            # 更新密钥
            secrets[key] = value
            
            # 加密并写入
            encrypted_data = self._cipher.encrypt(
                json.dumps(secrets).encode()
            )
            file_path.write_bytes(encrypted_data)
            
            # 设置文件权限
            file_path.chmod(0o600)
            
            logger.info(f"密钥 {key} 已写入加密文件")
        except Exception as e:
            logger.error(f"写入加密文件失败: {e}")
    
    def _delete_from_encrypted_file(self, key: str):
        """从加密文件删除密钥"""
        if not self._cipher:
            return
        
        file_path = self._get_encrypted_file_path()
        if not file_path.exists():
            return
        
        try:
            # 读取现有密钥
            encrypted_data = file_path.read_bytes()
            decrypted_data = self._cipher.decrypt(encrypted_data)
            secrets = json.loads(decrypted_data.decode())
            
            # 删除密钥
            secrets.pop(key, None)
            
            # 加密并写入
            encrypted_data = self._cipher.encrypt(
                json.dumps(secrets).encode()
            )
            file_path.write_bytes(encrypted_data)
            
            logger.info(f"密钥 {key} 已从加密文件删除")
        except Exception as e:
            logger.error(f"从加密文件删除密钥失败: {e}")
    
    def list_secrets(self) -> Dict[str, str]:
        """列出所有密钥（值被遮蔽）"""
        result = {}
        
        # 列出缓存中的密钥
        for key in self._cache:
            result[key] = "***"
        
        # 列出环境变量中的密钥
        for key in os.environ:
            if key not in result:
                result[key] = "***"
        
        return result


# 全局密钥管理器实例
_secret_manager: Optional[SecretManager] = None


def get_secret_manager() -> SecretManager:
    """获取全局密钥管理器"""
    global _secret_manager
    if _secret_manager is None:
        _secret_manager = SecretManager()
    return _secret_manager


def init_secret_manager(secret_key: str = None) -> SecretManager:
    """初始化全局密钥管理器"""
    global _secret_manager
    _secret_manager = SecretManager(secret_key)
    return _secret_manager

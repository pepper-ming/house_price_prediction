"""
配置管理模組

這個模組負責載入和管理所有的配置檔案，提供統一的配置存取介面。
使用單例模式確保配置在整個應用程式中保持一致。
"""

import yaml
import os
from pathlib import Path
from typing import Dict, Any, Optional
import logging

class ConfigManager:
    """
    配置管理器類別
    
    使用單例模式確保整個應用程式使用同一個配置實例。
    支援從 YAML 檔案載入配置，並提供方便的存取方法。
    """
    
    _instance = None
    _config = {}
    
    def __new__(cls):
        """實現單例模式"""
        if cls._instance is None:
            cls._instance = super(ConfigManager, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        """初始化配置管理器"""
        if not hasattr(self, 'initialized'):
            self.initialized = True
            self.config_dir = Path(__file__).parent.parent.parent / "configs"
            self.logger = logging.getLogger(__name__)
            self._load_all_configs()
    
    def _load_all_configs(self) -> None:
        """載入所有配置檔案"""
        config_files = {
            'data': 'data_config.yaml',
            'model': 'model_config.yaml',
            'train': 'train_config.yaml'
        }
        
        for config_name, filename in config_files.items():
            filepath = self.config_dir / filename
            if filepath.exists():
                try:
                    self._config[config_name] = self._load_yaml(filepath)
                    self.logger.info(f"成功載入配置: {filename}")
                except Exception as e:
                    self.logger.error(f"載入配置失敗 {filename}: {str(e)}")
            else:
                self.logger.warning(f"配置檔案不存在: {filepath}")
    
    def _load_yaml(self, filepath: Path) -> Dict[str, Any]:
        """
        載入 YAML 檔案
        
        Args:
            filepath: YAML 檔案路徑
            
        Returns:
            解析後的字典
        """
        with open(filepath, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        獲取配置值
        
        支援使用點號分隔的路徑，例如 'data.paths.train_raw'
        
        Args:
            key: 配置鍵，支援點號分隔的路徑
            default: 預設值
            
        Returns:
            配置值或預設值
        """
        keys = key.split('.')
        value = self._config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def get_data_config(self) -> Dict[str, Any]:
        """獲取資料配置"""
        return self._config.get('data', {})
    
    def get_model_config(self) -> Dict[str, Any]:
        """獲取模型配置"""
        return self._config.get('model', {})
    
    def get_train_config(self) -> Dict[str, Any]:
        """獲取訓練配置"""
        return self._config.get('train', {})
    
    def update(self, key: str, value: Any) -> None:
        """
        更新配置值（運行時）
        
        注意：這只會更新記憶體中的配置，不會寫回檔案
        
        Args:
            key: 配置鍵
            value: 新值
        """
        keys = key.split('.')
        config = self._config
        
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        config[keys[-1]] = value
    
    def __repr__(self) -> str:
        """返回配置的字串表示"""
        return f"ConfigManager({list(self._config.keys())})"


# 建立全域配置實例
config = ConfigManager()

# 便利函數
def get_config(key: str, default: Any = None) -> Any:
    """獲取配置值的便利函數"""
    return config.get(key, default)
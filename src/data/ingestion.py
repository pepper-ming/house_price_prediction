"""
資料載入模組

負責從各種來源載入資料，包含本地檔案和 Kaggle API。
提供統一的資料載入介面，並進行初步的資料驗證。
"""

import pandas as pd
import numpy as np
from pathlib import Path
import os
from typing import Tuple, Optional, Dict, Any
import subprocess
import json

from ..utils.config import get_config
from ..utils.logger import get_logger

logger = get_logger(__name__)

class DataIngestion:
    """
    資料載入類別
    
    支援從本地檔案和 Kaggle API 載入資料，
    並進行基本的資料驗證和統計摘要。
    """
    
    def __init__(self):
        """初始化資料載入器"""
        self.data_config = get_config('data')
        self.train_path = Path(get_config('data.paths.train_raw'))
        self.test_path = Path(get_config('data.paths.test_raw'))
        self.target_column = get_config('data.target_column')
        self.id_column = get_config('data.id_column')
        
    def download_from_kaggle(self) -> bool:
        """
        從 Kaggle 下載資料集
        
        需要先設定 Kaggle API 認證（~/.kaggle/kaggle.json）
        
        Returns:
            是否成功下載
        """
        try:
            # 檢查 Kaggle API 認證
            kaggle_json = Path.home() / '.kaggle' / 'kaggle.json'
            if not kaggle_json.exists():
                logger.error("找不到 Kaggle API 認證檔案。請先設定 ~/.kaggle/kaggle.json")
                return False
            
            # 建立資料目錄
            download_path = Path(get_config('data.kaggle.download_path'))
            download_path.mkdir(parents=True, exist_ok=True)
            
            # 下載資料集
            competition = get_config('data.kaggle.competition')
            cmd = [
                'kaggle', 'competitions', 'download',
                '-c', competition,
                '-p', str(download_path)
            ]
            
            logger.info(f"開始從 Kaggle 下載資料集: {competition}")
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                logger.info("資料集下載成功")
                
                # 解壓縮檔案
                import zipfile
                zip_path = download_path / f"{competition}.zip"
                if zip_path.exists():
                    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                        zip_ref.extractall(download_path)
                    logger.info("資料集解壓縮完成")
                    zip_path.unlink()  # 刪除 zip 檔
                
                return True
            else:
                logger.error(f"下載失敗: {result.stderr}")
                return False
                
        except Exception as e:
            logger.exception(f"下載過程發生錯誤: {str(e)}")
            return False
    
    def load_data(self, force_download: bool = False) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        載入訓練和測試資料
        
        Args:
            force_download: 是否強制重新下載資料
            
        Returns:
            訓練資料和測試資料的元組
        """
        # 檢查資料檔案是否存在
        if force_download or not self.train_path.exists() or not self.test_path.exists():
            logger.info("資料檔案不存在，嘗試從 Kaggle 下載...")
            if not self.download_from_kaggle():
                raise FileNotFoundError("無法取得資料檔案")
        
        # 載入資料
        logger.info("開始載入資料...")
        train_df = pd.read_csv(self.train_path)
        test_df = pd.read_csv(self.test_path)
        
        logger.info(f"訓練資料載入完成: {train_df.shape[0]} 筆資料, {train_df.shape[1]} 個欄位")
        logger.info(f"測試資料載入完成: {test_df.shape[0]} 筆資料, {test_df.shape[1]} 個欄位")
        
        # 基本驗證
        self._validate_data(train_df, test_df)
        
        return train_df, test_df
    
    def _validate_data(self, train_df: pd.DataFrame, test_df: pd.DataFrame) -> None:
        """
        驗證資料的基本完整性
        
        Args:
            train_df: 訓練資料
            test_df: 測試資料
        """
        # 檢查目標變數
        if self.target_column not in train_df.columns:
            raise ValueError(f"訓練資料中找不到目標變數: {self.target_column}")
        
        # 檢查 ID 欄位
        if self.id_column not in train_df.columns or self.id_column not in test_df.columns:
            raise ValueError(f"資料中找不到 ID 欄位: {self.id_column}")
        
        # 檢查重複的 ID
        train_duplicates = train_df[self.id_column].duplicated().sum()
        test_duplicates = test_df[self.id_column].duplicated().sum()
        
        if train_duplicates > 0:
            logger.warning(f"訓練資料中有 {train_duplicates} 筆重複的 ID")
        if test_duplicates > 0:
            logger.warning(f"測試資料中有 {test_duplicates} 筆重複的 ID")
        
        # 檢查特徵欄位是否一致（除了目標變數）
        train_features = set(train_df.columns) - {self.target_column}
        test_features = set(test_df.columns)
        
        missing_in_test = train_features - test_features
        missing_in_train = test_features - train_features
        
        if missing_in_test:
            logger.warning(f"測試資料缺少的欄位: {missing_in_test}")
        if missing_in_train:
            logger.warning(f"訓練資料缺少的欄位: {missing_in_train}")
    
    def get_data_info(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        獲取資料的基本資訊
        
        Args:
            df: 資料框
            
        Returns:
            包含資料資訊的字典
        """
        info = {
            'shape': df.shape,
            'columns': list(df.columns),
            'dtypes': df.dtypes.to_dict(),
            'missing_counts': df.isnull().sum().to_dict(),
            'missing_percentage': (df.isnull().sum() / len(df) * 100).to_dict(),
            'numeric_columns': list(df.select_dtypes(include=[np.number]).columns),
            'categorical_columns': list(df.select_dtypes(include=['object']).columns),
            'memory_usage': df.memory_usage(deep=True).sum() / 1024**2  # MB
        }
        
        # 數值型欄位的統計資訊
        if info['numeric_columns']:
            info['numeric_stats'] = df[info['numeric_columns']].describe().to_dict()
        
        return info
    
    def save_data_info(self, train_df: pd.DataFrame, test_df: pd.DataFrame) -> None:
        """
        儲存資料資訊到報告目錄
        
        Args:
            train_df: 訓練資料
            test_df: 測試資料
        """
        reports_dir = Path('reports')
        reports_dir.mkdir(exist_ok=True)
        
        # 收集資訊
        train_info = self.get_data_info(train_df)
        test_info = self.get_data_info(test_df)
        
        # 儲存為 JSON
        info_dict = {
            'train': train_info,
            'test': test_info,
            'target_column': self.target_column,
            'id_column': self.id_column
        }
        
        with open(reports_dir / 'data_info.json', 'w', encoding='utf-8') as f:
            json.dump(info_dict, f, indent=2, default=str)
        
        logger.info("資料資訊已儲存到 reports/data_info.json")


# 便利函數
def load_house_price_data() -> Tuple[pd.DataFrame, pd.DataFrame]:
    """載入房價資料的便利函數"""
    ingestion = DataIngestion()
    return ingestion.load_data()
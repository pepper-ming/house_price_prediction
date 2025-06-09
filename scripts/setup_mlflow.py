"""
MLflow 設置腳本

初始化 MLflow 實驗追蹤系統，建立實驗並設定基本配置。
"""

import mlflow
import mlflow.sklearn
from pathlib import Path
import sys

# 將專案根目錄加入路徑
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.utils.config import get_config
from src.utils.logger import get_logger

logger = get_logger(__name__)

def setup_mlflow():
    """設置 MLflow 實驗追蹤"""
    
    # 從配置檔案讀取設定
    tracking_uri = get_config('mlflow.tracking_uri', 'mlruns')
    experiment_name = get_config('mlflow.experiment_name', 'house_price_prediction')
    
    # 設定追蹤 URI
    mlflow.set_tracking_uri(tracking_uri)
    logger.info(f"MLflow tracking URI 設定為: {tracking_uri}")
    
    # 建立或獲取實驗
    try:
        experiment_id = mlflow.create_experiment(
            experiment_name,
            artifact_location=f"{tracking_uri}/{experiment_name}"
        )
        logger.info(f"建立新實驗: {experiment_name} (ID: {experiment_id})")
    except Exception as e:
        # 實驗已存在
        experiment = mlflow.get_experiment_by_name(experiment_name)
        experiment_id = experiment.experiment_id
        logger.info(f"使用現有實驗: {experiment_name} (ID: {experiment_id})")
    
    # 設定為當前實驗
    mlflow.set_experiment(experiment_name)
    
    # 測試記錄一個範例執行
    with mlflow.start_run(run_name="test_setup"):
        # 記錄一些測試參數
        mlflow.log_param("test_param", "test_value")
        mlflow.log_metric("test_metric", 0.5)
        
        # 記錄配置檔案作為 artifact
        mlflow.log_artifact("configs/data_config.yaml")
        mlflow.log_artifact("configs/model_config.yaml")
        mlflow.log_artifact("configs/train_config.yaml")
        
        logger.info("測試執行記錄完成")
    
    # 顯示 MLflow UI 啟動指令
    print("\n" + "="*50)
    print("MLflow 設置完成！")
    print(f"實驗名稱: {experiment_name}")
    print(f"追蹤目錄: {tracking_uri}")
    print("\n要啟動 MLflow UI，請在終端執行：")
    print(f"mlflow ui --backend-store-uri {tracking_uri}")
    print("\n然後在瀏覽器開啟: http://localhost:5000")
    print("="*50 + "\n")

if __name__ == "__main__":
    setup_mlflow()
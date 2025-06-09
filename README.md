房價預測機器學習專案
這是一個完整的房價預測機器學習專案，使用 Kaggle 的 House Prices Advanced Regression Techniques 資料集。專案目標是建立一個準確的房價預測模型（R² > 0.85），同時學習完整的資料科學工作流程。

專案結構
house_price_prediction/
├── configs/               # 配置檔案
├── data/                  # 資料目錄
│   ├── raw/              # 原始資料
│   ├── processed/        # 處理後資料
│   └── external/         # 外部資料
├── notebooks/            # Jupyter notebooks
├── src/                  # 核心程式碼
│   ├── data/            # 資料處理模組
│   ├── features/        # 特徵工程模組
│   ├── models/          # 模型相關模組
│   └── utils/           # 工具模組
├── scripts/              # 執行腳本
├── models/               # 訓練好的模型
├── reports/              # 分析報告
└── mlruns/              # MLflow 實驗追蹤
快速開始
1. 環境設置
bash
# 建立虛擬環境
python -m venv venv

# 啟動虛擬環境
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# 安裝套件
pip install -r requirements.txt
2. Kaggle API 設定
在 Kaggle 網站獲取 API 憑證
將 kaggle.json 放到 ~/.kaggle/ 目錄
設定權限（Linux/macOS）：
bash
chmod 600 ~/.kaggle/kaggle.json
3. 初始化專案
bash
# 設置 MLflow
python scripts/setup_mlflow.py

# 啟動 MLflow UI（選擇性）
mlflow ui --backend-store-uri mlruns
4. 開始探索
在 Jupyter 中開啟 notebooks/01_initial_data_exploration.ipynb 開始資料探索。

第1週任務清單
 建立專案結構
 設置開發環境
 配置管理系統
 日誌系統
 MLflow 實驗追蹤
 下載 Kaggle 資料集
 初步資料探索
 資料品質評估
第2週預計任務
 深度 EDA 分析
 缺失值處理策略
 異常值檢測與處理
 建立基線模型
配置說明
專案使用 YAML 配置檔案管理所有設定：

configs/data_config.yaml: 資料相關配置
configs/model_config.yaml: 模型定義和超參數空間
configs/train_config.yaml: 訓練流程配置
注意事項
資料下載：首次執行會自動從 Kaggle 下載資料，需要先設定 Kaggle API
記憶體需求：完整訓練需要至少 8GB RAM
Python 版本：建議使用 Python 3.8+
聯絡資訊
如有問題，請開啟 GitHub Issue 或聯絡專案維護者。


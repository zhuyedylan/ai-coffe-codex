"""
存储引擎 - 历史记录持久化
"""
import json
import os
from datetime import datetime
from typing import Dict, List
import pandas as pd

HISTORY_DIR = 'data/history'

class StorageEngine:
    def __init__(self, history_dir: str = HISTORY_DIR):
        self.history_dir = history_dir
        self.history_records: List[Dict] = []
        os.makedirs(self.history_dir, exist_ok=True)
        self._load_history()

    def _load_history(self):
        history_file = os.path.join(self.history_dir, 'history.json')
        if os.path.exists(history_file):
            try:
                with open(history_file, 'r', encoding='utf-8') as f:
                    self.history_records = json.load(f)
            except:
                self.history_records = []

    def _save_history_file(self):
        history_file = os.path.join(self.history_dir, 'history.json')
        with open(history_file, 'w', encoding='utf-8') as f:
            json.dump(self.history_records, f, ensure_ascii=False, indent=2)

    def create_record(self, operation_type: str, details: Dict) -> Dict:
        record_id = f"hist_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        record = {
            'id': record_id,
            'timestamp': datetime.now().isoformat(),
            'operation_type': operation_type,
            'details': details
        }
        self.history_records.append(record)
        self._save_history_file()
        return record

    def save_model_training(self, metrics: Dict, config: Dict, importance: Dict):
        return self.create_record('model_training', {
            'metrics': metrics,
            'config': config,
            'importance': importance
        })

    def save_formula_screening(self, formulas: pd.DataFrame, n_samples: int):
        top_row = formulas.iloc[0] if len(formulas) > 0 else {}
        pred_col = 'predicted_score'
        # 找到预测列名
        for col in formulas.columns:
            if col.startswith('predicted_'):
                pred_col = col
                break
        top_score = float(top_row.get(pred_col, 0)) if isinstance(top_row, dict) else 0
        return self.create_record('formula_screening', {
            'n_samples': n_samples,
            'top_score': top_score,
            'top_formula': top_row.to_dict() if hasattr(top_row, 'to_dict') else {}
        })

    def get_history_list(self) -> List[Dict]:
        return self.history_records.copy()

    def clear_history(self):
        self.history_records = []
        self._save_history_file()


# 全局实例
storage_engine = StorageEngine()

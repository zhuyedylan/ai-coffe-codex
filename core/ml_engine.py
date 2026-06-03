"""
机器学习引擎 - 随机森林模型训练、预测和分析
"""
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, r2_score
import joblib
import os
from typing import Dict, List, Optional

def _get_material_config():
    from .material_config import material_config
    return material_config

DEFAULT_CONFIG = {
    'n_estimators': 50,
    'max_depth': None,
    'min_samples_leaf': 1,
    'random_state': 42
}

class MLEngine:
    def __init__(self, model_dir: str = 'data/models'):
        self.model_dir = model_dir
        self.model: Optional[RandomForestRegressor] = None
        self.config: Dict = DEFAULT_CONFIG.copy()
        self.metrics: Dict = {}
        self.feature_importance: Dict = {}
        self.is_trained: bool = False
        self.feature_cols: List[str] = []
        os.makedirs(self.model_dir, exist_ok=True)

    def get_feature_cols(self) -> List[str]:
        mc = _get_material_config()
        return mc.get_feature_names()

    def get_target_name(self) -> str:
        mc = _get_material_config()
        target = mc.get_active_target_variable()
        return target['name'] if target else 'score'

    def train(self, data: pd.DataFrame, config: Optional[Dict] = None) -> Dict:
        if config:
            self.config.update(config)

        self.feature_cols = self.get_feature_cols()
        target_name = self.get_target_name()

        missing_features = [f for f in self.feature_cols if f not in data.columns]
        if missing_features:
            raise ValueError(f"数据缺少特征列: {missing_features}")

        X = data[self.feature_cols].values
        y = data[target_name].values

        self.model = RandomForestRegressor(
            n_estimators=self.config['n_estimators'],
            max_depth=self.config['max_depth'],
            min_samples_leaf=self.config['min_samples_leaf'],
            random_state=self.config['random_state']
        )
        self.model.fit(X, y)

        y_pred = self.model.predict(X)
        self.metrics = {
            'mse': mean_squared_error(y, y_pred),
            'r2': r2_score(y, y_pred),
            'data_count': len(data),
            'feature_count': len(self.feature_cols),
            'features': self.feature_cols,
            'target': target_name
        }

        self.feature_importance = dict(zip(self.feature_cols, self.model.feature_importances_))
        self.is_trained = True
        return self.metrics

    def predict(self, formula: Dict) -> float:
        if not self.is_trained:
            raise ValueError("模型尚未训练")
        X = [[formula.get(feat, 0) for feat in self.feature_cols]]
        return self.model.predict(X)[0]

    def predict_batch(self, formulas: pd.DataFrame) -> np.ndarray:
        if not self.is_trained:
            raise ValueError("模型尚未训练")
        for feat in self.feature_cols:
            if feat not in formulas.columns:
                formulas[feat] = 0
        X = formulas[self.feature_cols].values
        return self.model.predict(X)

    def generate_virtual_formulas(self, config: Optional[Dict] = None) -> pd.DataFrame:
        if not self.is_trained:
            raise ValueError("模型尚未训练")

        n_samples = 5000
        if config:
            n_samples = config.get('n_samples', 5000)

        mc = _get_material_config()
        materials = mc.get_materials()
        ranges = mc.get_ranges()

        if config and 'ranges' in config:
            ranges.update(config['ranges'])

        formulas = []
        for _ in range(n_samples):
            formula = {}
            for mat in materials:
                mat_name = mat['name']
                min_val, max_val = ranges.get(mat_name, tuple(mat['range']))
                formula[mat_name] = np.random.uniform(min_val, max_val)
            formulas.append(formula)

        df = pd.DataFrame(formulas)
        predictions = self.predict_batch(df)
        target_name = self.get_target_name()
        df[f'predicted_{target_name}'] = predictions
        df = df.sort_values(f'predicted_{target_name}', ascending=False).reset_index(drop=True)

        return df

    def get_top_formulas(self, n: int = 20, config: Optional[Dict] = None) -> pd.DataFrame:
        all_formulas = self.generate_virtual_formulas(config)
        return all_formulas.head(n)

# 全局实例
ml_engine = MLEngine()

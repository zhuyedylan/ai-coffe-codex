"""
数据管理引擎 - 处理实验数据的导入、管理和验证
"""
import pandas as pd
import numpy as np
import os
from typing import List, Dict, Tuple, Optional

def _get_material_config():
    from .material_config import material_config
    return material_config

def get_data_columns():
    """获取数据列名映射"""
    mc = _get_material_config()
    columns = mc.get_columns()
    columns['id'] = '序号'
    return columns

def get_data_ranges():
    """获取所有数据范围"""
    mc = _get_material_config()
    ranges = mc.get_ranges()
    target = mc.get_active_target_variable()
    if target:
        ranges[target['name']] = tuple(target['range'])
    return ranges

def generate_sample_data():
    """生成15组示例实验数据"""
    mc = _get_material_config()
    target = mc.get_active_target_variable()
    target_name = target['name'] if target else 'score'

    base_configs = [
        # Optimal zone: PLA ~95%, best balance of strength + sustainability
        {'pla_percent': 95, 'coffee_percent': 2.5, 'eso_percent': 1.5, 'citric_percent': 0.8, 'score': 9.2},
        {'pla_percent': 94.5, 'coffee_percent': 3, 'eso_percent': 1.8, 'citric_percent': 1.0, 'score': 9.0},
        {'pla_percent': 95.5, 'coffee_percent': 2, 'eso_percent': 1.2, 'citric_percent': 0.6, 'score': 8.8},
        {'pla_percent': 94, 'coffee_percent': 3.5, 'eso_percent': 2.0, 'citric_percent': 1.2, 'score': 8.6},
        {'pla_percent': 96, 'coffee_percent': 1.8, 'eso_percent': 1.0, 'citric_percent': 0.5, 'score': 8.5},
        # Near-optimal: PLA 93-97%
        {'pla_percent': 93, 'coffee_percent': 4, 'eso_percent': 2.5, 'citric_percent': 1.5, 'score': 7.8},
        {'pla_percent': 96.5, 'coffee_percent': 1.5, 'eso_percent': 0.8, 'citric_percent': 0.4, 'score': 7.5},
        {'pla_percent': 93.5, 'coffee_percent': 3.5, 'eso_percent': 2.2, 'citric_percent': 1.3, 'score': 7.6},
        {'pla_percent': 97, 'coffee_percent': 1.2, 'eso_percent': 0.6, 'citric_percent': 0.3, 'score': 7.0},
        # Declining: PLA 90-93%
        {'pla_percent': 92, 'coffee_percent': 5, 'eso_percent': 2.0, 'citric_percent': 1.0, 'score': 6.2},
        {'pla_percent': 91, 'coffee_percent': 5.5, 'eso_percent': 2.8, 'citric_percent': 1.8, 'score': 5.8},
        {'pla_percent': 90, 'coffee_percent': 6, 'eso_percent': 2.5, 'citric_percent': 1.6, 'score': 5.2},
        {'pla_percent': 89, 'coffee_percent': 7, 'eso_percent': 2.2, 'citric_percent': 1.5, 'score': 4.8},
        # Low: PLA 88-89%
        {'pla_percent': 88.5, 'coffee_percent': 7.5, 'eso_percent': 2.0, 'citric_percent': 1.5, 'score': 4.2},
        {'pla_percent': 88, 'coffee_percent': 8, 'eso_percent': 1.5, 'citric_percent': 1.0, 'score': 3.5},
        # Declining: PLA 97-99% (too pure, less additive benefit)
        {'pla_percent': 97.5, 'coffee_percent': 1, 'eso_percent': 0.5, 'citric_percent': 0.2, 'score': 6.0},
        {'pla_percent': 98, 'coffee_percent': 0.8, 'eso_percent': 0.4, 'citric_percent': 0.2, 'score': 4.5},
        {'pla_percent': 98.5, 'coffee_percent': 0.6, 'eso_percent': 0.3, 'citric_percent': 0.1, 'score': 3.0},
        {'pla_percent': 99, 'coffee_percent': 0.5, 'eso_percent': 0.2, 'citric_percent': 0.1, 'score': 1.8},
        {'pla_percent': 99, 'coffee_percent': 0.5, 'eso_percent': 0.3, 'citric_percent': 0.2, 'score': 2.0},
    ]

    df = pd.DataFrame(base_configs)

    # 加一些小噪声使数据更真实
    for col in df.columns:
        if col != target_name:
            df[col] = df[col] + np.random.normal(0, 0.3, len(df))
            df[col] = df[col].clip(lower=0)

    df[target_name] = df[target_name] + np.random.normal(0, 0.2, len(df))
    df[target_name] = df[target_name].clip(lower=1, upper=10)

    return df.round(1)

SAMPLE_DATA = generate_sample_data()
DATA_RANGES = get_data_ranges()


class DataEngine:
    """数据管理引擎"""

    def __init__(self):
        self.current_data: pd.DataFrame = pd.DataFrame()
        self._load_default()

    def _load_default(self):
        """加载默认空DataFrame"""
        mc = _get_material_config()
        cols = ['id'] + mc.get_feature_names()
        target = mc.get_active_target_variable()
        if target:
            cols.append(target['name'])
        self.current_data = pd.DataFrame(columns=cols)

    def get_data(self) -> pd.DataFrame:
        """获取当前数据"""
        return self.current_data

    def get_data_count(self) -> int:
        """获取当前数据记录数"""
        return len(self.current_data)

    def set_data(self, df: pd.DataFrame):
        """设置当前数据"""
        self.current_data = df.copy()

    def get_sample_data(self) -> pd.DataFrame:
        """获取示例数据"""
        return generate_sample_data()

    def add_record(self, record: Dict) -> bool:
        """添加单条记录"""
        import pandas as pd
        new_row = pd.DataFrame([record])
        if self.current_data.empty:
            self.current_data = new_row
        else:
            self.current_data = pd.concat([self.current_data, new_row], ignore_index=True)
        return True

    def clear_data(self):
        """清空数据"""
        self._load_default()

    def load_csv(self, file_path: str) -> Tuple[bool, str]:
        """从CSV文件加载数据"""
        try:
            df = pd.read_csv(file_path)
            self.current_data = df
            return True, f"成功加载 {len(df)} 条数据"
        except Exception as e:
            return False, f"加载失败: {e}"


# 全局实例
data_engine = DataEngine()

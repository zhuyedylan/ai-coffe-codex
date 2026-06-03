"""
材料配置管理器 - 动态管理材料成分定义
"""
import json
import os
import uuid
from typing import Dict, List, Optional, Tuple
from datetime import datetime

class MaterialConfigManager:
    """材料配置管理类 - 支持增删改查"""

    DEFAULT_CONFIG_PATH = 'data/configs/materials.json'

    def __init__(self, config_path: str = None):
        self.config_path = config_path or self.DEFAULT_CONFIG_PATH
        self.materials: List[Dict] = []
        self.target_variables: List[Dict] = []
        self.active_target: str = 'score'
        self.role_types: List[Dict] = []
        self._load()

    def _load(self):
        """从JSON文件加载配置"""
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    content = json.load(f)
                    self.materials = content.get('materials', [])
                    self.target_variables = content.get('target_variables', [])
                    self.active_target = content.get('active_target', 'score')
                    self.role_types = content.get('role_types', [])
                    self.materials.sort(key=lambda x: x.get('order', 999))
            except Exception as e:
                print(f"加载材料配置失败: {e}")
                self._init_default()
        else:
            self._init_default()

    def _init_default(self):
        """初始化默认配置"""
        self.materials = [
            {
                'id': 'mat_pla', 'name': 'pla_percent', 'label': 'PLA含量',
                'display_name': 'PLA (聚乳酸)', 'unit': '%', 'range': [0, 100],
                'default_value': 70, 'role': '基体材料', 'role_type': 'matrix',
                'description': '主要塑料基体', 'is_required': True, 'order': 1,
                'print_rules': {'temp_adjust_per_unit': 0, 'speed_adjust_per_unit': 0}
            },
            {
                'id': 'mat_coffee', 'name': 'coffee_percent', 'label': '咖啡渣含量',
                'display_name': '咖啡渣', 'unit': '%', 'range': [0, 50],
                'default_value': 15, 'role': '填料', 'role_type': 'filler',
                'description': '增加质感降低成本', 'is_required': True, 'order': 2,
                'print_rules': {'temp_adjust_per_unit': 0.5, 'speed_adjust_per_unit': -0.3}
            },
            {
                'id': 'mat_eso', 'name': 'eso_percent', 'label': 'ESO含量',
                'display_name': 'ESO (环氧大豆油)', 'unit': '%', 'range': [0, 10],
                'default_value': 5, 'role': '扩链剂', 'role_type': 'chain_extender',
                'description': '修复断裂分子链', 'is_required': True, 'order': 3,
                'print_rules': {'temp_adjust_per_unit': -0.5, 'speed_adjust_per_unit': 0}
            },
            {
                'id': 'mat_citric', 'name': 'citric_percent', 'label': '柠檬酸含量',
                'display_name': '柠檬酸', 'unit': '%', 'range': [0, 5],
                'default_value': 2.5, 'role': '偶联剂', 'role_type': 'coupling_agent',
                'description': '改善界面结合', 'is_required': False, 'order': 4,
                'print_rules': {'temp_adjust_per_unit': 0, 'speed_adjust_per_unit': 0}
            }
        ]
        self.target_variables = [
            {'name': 'score', 'label': '韧性评分', 'range': [1, 10], 'description': '材料韧性综合评价'}
        ]
        self.active_target = 'score'
        self._save()

    def _save(self):
        """保存到JSON文件"""
        os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
        content = {
            'materials': self.materials,
            'target_variables': self.target_variables,
            'active_target': self.active_target,
            'role_types': self.role_types,
            'last_updated': datetime.now().isoformat()
        }
        with open(self.config_path, 'w', encoding='utf-8') as f:
            json.dump(content, f, ensure_ascii=False, indent=2)

    def get_materials(self) -> List[Dict]:
        return self.materials.copy()

    def get_material_by_name(self, name: str) -> Optional[Dict]:
        for mat in self.materials:
            if mat['name'] == name:
                return mat.copy()
        return None

    def get_feature_names(self) -> List[str]:
        return [mat['name'] for mat in self.materials]

    def get_feature_labels(self) -> Dict[str, str]:
        return {mat['name']: mat['label'] for mat in self.materials}

    def get_ranges(self) -> Dict[str, Tuple]:
        return {mat['name']: tuple(mat['range']) for mat in self.materials}

    def get_default_values(self) -> Dict[str, float]:
        return {mat['name']: mat['default_value'] for mat in self.materials}

    def get_active_target_variable(self) -> Optional[Dict]:
        for tv in self.target_variables:
            if tv['name'] == self.active_target:
                return tv.copy()
        return None

    def get_columns(self) -> Dict[str, str]:
        """获取列名映射 {字段名: 显示名}"""
        cols = {mat['name']: mat['label'] for mat in self.materials}
        target = self.get_active_target_variable()
        if target:
            cols[target['name']] = target['label']
        return cols

    def add_material(self, name: str, label: str, display_name: str = None,
                     unit: str = '%', range: list = None, default_value: float = 0,
                     role: str = '添加剂', role_type: str = 'additive',
                     description: str = '', is_required: bool = False,
                     print_rules: dict = None) -> tuple:
        """添加新材料，返回 (success: bool, message: str)"""
        if not name or not label:
            return False, "字段名和标签不能为空"
        if any(m['name'] == name for m in self.materials):
            return False, f"字段名 '{name}' 已存在"
        if range is None:
            range = [0, 100]

        new_id = f"mat_{uuid.uuid4().hex[:8]}"
        new_material = {
            'id': new_id,
            'name': name,
            'label': label,
            'display_name': display_name or label,
            'unit': unit or '%',
            'range': range,
            'default_value': default_value,
            'role': role,
            'role_type': role_type,
            'description': description,
            'is_required': is_required,
            'order': len(self.materials) + 1,
            'print_rules': print_rules or {'temp_adjust_per_unit': 0, 'speed_adjust_per_unit': 0}
        }
        self.materials.append(new_material)
        self._save()
        return True, new_id

# 全局实例
material_config = MaterialConfigManager()

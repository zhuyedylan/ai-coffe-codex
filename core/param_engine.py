"""
打印参数引擎 - 智能3D打印参数推荐
"""
import numpy as np
from typing import Dict, List, Optional

# 参数调整原因的文案
PARAM_REASONS = {
    'nozzle_temp': '挤出温度影响熔融流动性，基于填料含量和扩链剂协同调整',
    'bed_temp': '热床温度保证首层附着，高填料含量需更高热床温度',
    'print_speed': '打印速度影响成型质量，高填料含量需降低速度',
    'retraction_dist': '回抽距离防止拉丝，高填料含量需增大回抽',
    'retraction_speed': '回抽速度协同回抽距离防止堵头',
    'layer_height': '层高影响打印精度和强度',
    'fan_speed': '风扇速度影响冷却效率，高填料需降低风扇',
    'flow_rate': '流量补偿挤出量，高填料需增加补偿',
}

# 常见问题及解决方案
FAQ_SOLUTIONS = {
    '喷嘴堵塞': {
        'symptoms': ['挤出断断续续', '出丝变细', '打印件缺层'],
        'solutions': [
            '增加回抽距离至 6-8mm',
            '降低打印速度 10-20mm/s',
            '清理喷嘴或更换',
            '检查耗材是否受潮',
            '适当增加挤出温度 5-10°C'
        ]
    },
    '打印分层': {
        'symptoms': ['层间粘合不良', '模型易断裂', '表面有裂纹'],
        'solutions': [
            '降低冷却风扇强度至 30-50%',
            '提高挤出温度 5-10°C',
            '降低打印速度',
            '检查Z轴高度是否正确'
        ]
    },
    '拉丝严重': {
        'symptoms': ['移动时有细丝', '模型表面有毛刺', '支撑清理困难'],
        'solutions': [
            '增加回抽距离至 5-7mm',
            '提高回抽速度至 50-60mm/s',
            '降低打印温度 5°C',
            '开启回抽时Z抬升'
        ]
    },
    '翘边': {
        'symptoms': ['模型边缘翘起', '首层附着不良', '角落脱离热床'],
        'solutions': [
            '提高热床温度至 65-70°C',
            '使用 brim 或 raft',
            '降低首层打印速度',
            '关闭风扇或降至最低'
        ]
    },
    '挤出不足': {
        'symptoms': ['出丝太细', '层间有空隙', '表面不饱满'],
        'solutions': [
            '增加流量补偿至 105-110%',
            '提高挤出温度',
            '检查喷嘴是否部分堵塞',
            '减小打印速度'
        ]
    },
    '表面粗糙': {
        'symptoms': ['表面不光滑', '有明显层纹', '手感粗糙'],
        'solutions': [
            '降低层高至 0.12-0.16mm',
            '降低打印速度',
            '检查耗材是否受潮',
            '适当降低温度减少拉丝'
        ]
    }
}

# 成分角色类型规则
ROLE_TYPE_RULES = {
    'matrix': {'label': '基体材料', 'description': '主要塑料基体'},
    'filler': {'label': '填料', 'description': '增加质感降低成本'},
    'chain_extender': {'label': '扩链剂', 'description': '修复断裂分子链'},
    'coupling_agent': {'label': '偶联剂', 'description': '改善界面结合'},
    'additive': {'label': '添加剂', 'description': '功能助剂'},
}


class ParamEngine:
    """3D打印参数智能推荐引擎"""

    def __init__(self):
        self.base_params = {
            'nozzle_temp': 195,
            'bed_temp': 60,
            'print_speed': 50,
            'retraction_dist': 4.0,
            'retraction_speed': 40,
            'layer_height': 0.2,
            'fan_speed': 80,
            'flow_rate': 100,
        }
        self.recommended_params: Dict = {}
        self.current_formula: Dict = {}

    def recommend_params(self, formula: Dict) -> Dict:
        """
        基于配方智能推荐3D打印参数

        参数:
            formula: dict {成分字段名: 含量值}
        返回:
            dict: 推荐参数字典
        """
        from .material_config import material_config

        params = self.base_params.copy()
        materials = material_config.get_materials()

        for mat in materials:
            mat_name = mat['name']
            mat_value = formula.get(mat_name, mat['default_value'])
            rules = mat.get('print_rules', {})
            role_type = mat.get('role_type', 'additive')

            # 温度调整
            temp_adjust = rules.get('temp_adjust_per_unit', 0)
            if temp_adjust != 0:
                # 偏离默认值的温度调整
                default_val = mat['default_value']
                deviation = mat_value - default_val
                params['nozzle_temp'] += deviation * temp_adjust

            # 速度调整
            speed_adjust = rules.get('speed_adjust_per_unit', 0)
            if speed_adjust != 0:
                default_val = mat['default_value']
                deviation = mat_value - default_val
                params['print_speed'] += deviation * speed_adjust

        # 根据填料含量调整回抽距离
        filler_materials = [m for m in materials if m['role_type'] == 'filler']
        for fm in filler_materials:
            fm_value = formula.get(fm['name'], fm['default_value'])
            params['retraction_dist'] += fm_value * 0.05

        # 根据扩链剂调整热床温度
        chain_extenders = [m for m in materials if m['role_type'] == 'chain_extender']
        for ce in chain_extenders:
            ce_value = formula.get(ce['name'], ce['default_value'])
            params['bed_temp'] -= ce_value * 0.5

        # 根据填料含量调整风扇速度
        for fm in filler_materials:
            fm_value = formula.get(fm['name'], fm['default_value'])
            params['fan_speed'] -= fm_value * 1.0

        # 根据填料含量调整流量补偿
        total_filler = sum(formula.get(fm['name'], fm['default_value']) for fm in filler_materials)
        params['flow_rate'] += total_filler * 0.1

        # 钳制参数在合理范围
        params['nozzle_temp'] = np.clip(params['nozzle_temp'], 180, 220)
        params['bed_temp'] = np.clip(params['bed_temp'], 50, 80)
        params['print_speed'] = np.clip(params['print_speed'], 20, 80)
        params['retraction_dist'] = np.clip(params['retraction_dist'], 2.0, 10.0)
        params['retraction_speed'] = np.clip(params['retraction_speed'], 20, 80)
        params['layer_height'] = 0.2  # 固定层高
        params['fan_speed'] = np.clip(params['fan_speed'], 0, 100)
        params['flow_rate'] = np.clip(params['flow_rate'], 90, 120)

        # 保留两位小数
        for k in params:
            if isinstance(params[k], float):
                params[k] = round(params[k], 1)

        self.recommended_params = params
        self.current_formula = formula
        return params

    def get_faq_solution(self, problem: str) -> Dict:
        """获取常见问题的解决方案"""
        return FAQ_SOLUTIONS.get(problem, {
            'symptoms': [],
            'solutions': ['暂无针对性的解决方案，请参考参数建议']
        })

    def get_all_faqs(self) -> List[str]:
        """获取所有常见问题列表"""
        return list(FAQ_SOLUTIONS.keys())

    def get_param_reason(self, param_name: str) -> str:
        """获取参数调整原因说明"""
        return PARAM_REASONS.get(param_name, '综合配方优化')


# 全局实例
param_engine = ParamEngine()

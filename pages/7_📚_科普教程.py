"""科普教程页面"""
import streamlit as st
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

st.header("📚 科普教程")
st.markdown("了解AI如何帮助材料科学研究")

CODE_EXPLANATIONS = {
    "ml_engine": {
        "title": "🧠 ml_engine.py — 随机森林引擎（核心算法）",
        "sections": [
            {
                "title": "1. 模型初始化与配置",
                "explanation": "MLEngine 类是系统的核心。初始化时设置模型存储目录和默认超参数，包括决策树数量(n_estimators=50)、最大深度(max_depth=None，即不限制)等。",
                "code": '''    def __init__(self, model_dir: str = 'data/models'):
        self.model_dir = model_dir
        self.model: Optional[RandomForestRegressor] = None
        self.config: Dict = DEFAULT_CONFIG.copy()
        self.metrics: Dict = {}
        self.feature_importance: Dict = {}
        self.is_trained: bool = False
        self.feature_cols: List[str] = []
        os.makedirs(self.model_dir, exist_ok=True)'''
            },
            {
                "title": "2. 模型训练 - train()",
                "explanation": "最关键的方法。从 material_config 动态获取特征列（PLA、咖啡渣、ESO、柠檬酸）和目标变量（评分），训练随机森林回归模型，自动计算 R^2 和特征重要性。",
                "code": '''    def train(self, data: pd.DataFrame, config: Optional[Dict] = None) -> Dict:
        if config:
            self.config.update(config)

        self.feature_cols = self.get_feature_cols()
        target_name = self.get_target_name()

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
        }
        self.feature_importance = dict(
            zip(self.feature_cols, self.model.feature_importances_)
        )
        self.is_trained = True
        return self.metrics'''
            },
            {
                "title": "3. 虚拟配方生成 - generate_virtual_formulas()",
                "explanation": "配方的智能推荐引擎。在成分范围内随机生成数千种配方组合，用模型预测评分，按评分排序返回最优配方。",
                "code": '''    def generate_virtual_formulas(self, config=None) -> pd.DataFrame:
        n_samples = 5000
        mc = _get_material_config()
        materials = mc.get_materials()
        ranges = mc.get_ranges()

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
        df = df.sort_values(f'predicted_{target_name}', ascending=False)
        return df'''
            }
        ]
    },
    "data_engine": {
        "title": "📊 data_engine.py — 数据管理引擎",
        "sections": [
            {
                "title": "1. 示例数据生成",
                "explanation": "generate_sample_data() 生成20组虚拟实验数据，评分遵循最优区间评分高、极端成分评分低的规律。",
                "code": '''    base_configs = [
        # 最佳配方区 (PLA 88-90%)
        {'pla_percent': 88, 'coffee_percent': 7, 'eso_percent': 2.5, 'citric_percent': 1.8, 'score': 8.0},
        # 中等区间 (PLA 92-95%)
        {'pla_percent': 93, 'coffee_percent': 4, 'eso_percent': 1.5, 'citric_percent': 0.8, 'score': 5.5},
        # 极端区间 (PLA 99%)
        {'pla_percent': 99, 'coffee_percent': 0.5, 'eso_percent': 0.2, 'citric_percent': 0.1, 'score': 1.0},
    ]
    # 添加随机噪声模拟实验误差
    for col in df.columns:
        if col != target_name:
            df[col] = df[col] + np.random.normal(0, 0.3, len(df))'''
            },
            {
                "title": "2. 数据管理核心",
                "explanation": "DataEngine 维护当前数据的 DataFrame，支持加载示例、添加记录、清空数据，所有页面共享同一个全局实例。",
                "code": '''class DataEngine:
    def __init__(self):
        self.current_data: pd.DataFrame = pd.DataFrame()
        self._load_default()

    def get_data(self) -> pd.DataFrame:
        return self.current_data

    def get_data_count(self) -> int:
        return len(self.current_data)

    def set_data(self, df: pd.DataFrame):
        self.current_data = df.copy()

    def add_record(self, record: Dict) -> bool:
        new_row = pd.DataFrame([record])
        self.current_data = pd.concat(
            [self.current_data, new_row], ignore_index=True)
        return True'''
            }
        ]
    },
    "param_engine": {
        "title": "🖨️ param_engine.py — 3D打印参数推荐",
        "sections": [
            {
                "title": "1. 参数推荐算法",
                "explanation": "根据配方中各成分含量动态调整打印参数。每种材料有 print_rules 定义温度/速度的影响系数，偏离默认值越大调整幅度越大。",
                "code": '''    def recommend_params(self, formula: Dict) -> Dict:
        params = self.base_params.copy()
        materials = material_config.get_materials()

        for mat in materials:
            mat_value = formula.get(mat['name'], mat['default_value'])
            rules = mat.get('print_rules', {})

            temp_adjust = rules.get('temp_adjust_per_unit', 0)
            if temp_adjust != 0:
                deviation = mat_value - mat['default_value']
                params['nozzle_temp'] += deviation * temp_adjust

            speed_adjust = rules.get('speed_adjust_per_unit', 0)
            if speed_adjust != 0:
                deviation = mat_value - mat['default_value']
                params['print_speed'] += deviation * speed_adjust

        params['retraction_dist'] += formula.get('coffee_percent', 0) * 0.05
        params['nozzle_temp'] = np.clip(params['nozzle_temp'], 180, 220)
        params['print_speed'] = np.clip(params['print_speed'], 20, 80)
        return params'''
            },
            {
                "title": "2. 常见故障知识库",
                "explanation": "内置6种常见3D打印问题的诊断与解决方案：喷嘴堵塞、打印分层、拉丝严重、翘边、挤出不足、表面粗糙。",
                "code": '''FAQ_SOLUTIONS = {
    '喷嘴堵塞': {
        'symptoms': ['挤出断断续续', '出丝变细'],
        'solutions': [
            '增加回抽距离至 6-8mm',
            '降低打印速度 10-20mm/s',
            '清理喷嘴或更换',
        ]
    },
    '打印分层': {
        'solutions': [
            '降低风扇强度至 30-50%',
            '提高挤出温度 5-10°C',
        ]
    },
    # ... 共6种
}'''
            }
        ]
    },
    "material_config": {
        "title": "⚙️ material_config.py — 材料配置管理",
        "sections": [
            {
                "title": "1. 动态材料系统",
                "explanation": "材料定义存储在 data/configs/materials.json 中。MaterialConfigManager 支持运行时增删改材料，新增材料自动适配所有页面和模型。",
                "code": '''class MaterialConfigManager:
    def __init__(self, config_path: str = None):
        self.config_path = config_path or 'data/configs/materials.json'
        self.materials: List[Dict] = []
        self._load()

    def _load(self):
        if os.path.exists(self.config_path):
            with open(self.config_path, 'r', encoding='utf-8') as f:
                content = json.load(f)
                self.materials = content.get('materials', [])

    def get_feature_names(self) -> List[str]:
        return [mat['name'] for mat in self.materials]

    def get_ranges(self) -> Dict[str, Tuple]:
        return {mat['name']: tuple(mat['range']) for mat in self.materials}'''
            },
            {
                "title": "2. JSON 配置持久化",
                "explanation": "材料配置以JSON格式持久化到磁盘。增删改立即保存，重启不丢失。",
                "code": '''{
    "materials": [
        {
            "id": "mat_pla",
            "name": "pla_percent",
            "label": "PLA含量",
            "range": [88, 99],
            "default_value": 93,
            "role_type": "matrix",
            "print_rules": {"temp_adjust_per_unit": 0, "speed_adjust_per_unit": 0}
        },
        {
            "id": "mat_coffee",
            "name": "coffee_percent",
            "label": "咖啡渣含量",
            "range": [0.5, 8],
            "default_value": 4,
            "role_type": "filler",
            "print_rules": {"temp_adjust_per_unit": 0.5, "speed_adjust_per_unit": -0.3}
        }
    ]
}'''
            }
        ]
    }
}

tabs = st.tabs(["🤖 AI原理", "🧪 材料科学", "❓ 常见问题", "🛠️ 实操指南", "💻 代码详解"])

with tabs[0]:
    st.markdown("""
    ## 什么是随机森林？

    想象你要预测一个材料的性能，但影响因素很多（PLA含量、咖啡渣含量、ESO含量...）。你问一位专家的意见，但一个人的判断可能有偏差。

    随机森林的做法是：**问50个「专家」，然后取平均值**。每个「专家」就是一棵「决策树」。

    ### 为什么叫「随机」森林？

    - **随机样本**：每棵树只随机看到一部分训练数据
    - **随机特征**：每棵树只随机使用一部分影响因素
    - 这种随机性让每棵树学会不同的「知识」，综合起来更可靠

    ### 为什么用随机森林？

    | 特点 | 说明 |
    |------|------|
    | 小样本友好 | 15-20组数据就能用 |
    | 无需GPU | CPU即可快速训练 |
    | 可解释性强 | 能告诉你每个成分的重要性 |
    | 抗过拟合 | 多棵树投票，不容易死记硬背 |

    ### 工作流程

    ```
    实验数据 → 随机森林训练 → 预测模型
                                    ↓
    生成5000+虚拟配方 → 模型预测评分 → 排序筛选Top配方
    ```
    """)

    st.image("assets/random_forest.png",
             caption="随机森林示意图", width=600)

with tabs[1]:
    st.markdown("""
    ## 材料科学原理

    ### 为什么用咖啡渣做3D打印？

    全球每年产生约 **600万吨** 废弃咖啡渣。传统处理方式是填埋或焚烧，会产生大量温室气体。

    将咖啡渣混入PLA塑料制作3D打印线材，既环保又能创造独特质感。

    ### 各成分的作用

    | 成分 | 作用 | 典型含量 | 说明 |
    |------|------|---------|------|
    | **PLA** | 基体材料，提供力学强度 | 88-99% | 主体塑料，含量越高材料越接近纯PLA |
    | **咖啡渣** | 填料，增加环保质感 | 0.5-8% | 小比例添加即可改善可持续性 |
    | **ESO** | 扩链剂，修复分子链断裂 | 0.2-3% | 微量即可改善韧性 |
    | **柠檬酸** | 偶联剂，改善界面结合 | 0.1-2% | 极微量即有效 |

    ### 成分之间的协同关系

    这些成分并非独立作用，它们之间存在复杂的交互：

    | 关系 | 说明 |
    |------|------|
    | PLA ↔ 咖啡渣 | PLA提供基体强度，咖啡渣牺牲部分强度换取环保性 |
    | ESO ↔ 热降解 | ESO修复高温加工中断裂的PLA分子链 |
    | 柠檬酸 ↔ 界面 | 柠檬酸改善咖啡渣与PLA的界面结合力 |

    ### 为什么材料会变脆？

    在混合和挤出过程中，高温会导致PLA的分子链断裂（热降解）。

    **ESO（环氧大豆油）** 的作用就像「胶水」，可以把断裂的分子链重新连接起来，恢复材料的韧性。

    ### 评分规律

    韧性评分（1-10分）随成分变化的基本规律：

    - PLA 93-96% + 咖啡渣 2-4% → 评分 7.5-9.1（最佳平衡）
    - PLA 88-92% + 咖啡渣 5-8% → 评分 5-6（填料过多）
    - PLA 97-99% + 咖啡渣 <1% → 评分 1-4（基本是纯PLA）
    """)

with tabs[2]:
    st.markdown("""
    ## 常见问题

    **Q: 模型需要多少数据？**
    A: 最少15组。数据越多、分布越广，模型越准确。

    **Q: R²多少算好？**
    A: >0.85 优秀，0.70-0.85 可用，<0.70 建议补充数据或调整参数。

    **Q: 预测评分是什么意思？**
    A: 1-10分，综合反映材料韧性。7分以上通常认为可用。

    **Q: 为什么我的数据预测不准？**
    A: 可能原因：数据量不足、数据分布不均匀、成分范围太窄、实验测量误差大。

    **Q: 虚拟配方和真实实验有什么区别？**
    A: 虚拟配方是AI基于已有数据推测的「最优猜测」，最终仍需真实实验验证。

    **Q: 咖啡渣含量越高越好吗？**
    A: 本项目以PLA为主体（88-99%），咖啡渣为小比例填料（0.5-8%）。适量咖啡渣（5-7%）可兼顾环保与性能。
    """)

with tabs[3]:
    st.markdown("""
    ## 实操指南

    ### 推荐工作流程

    ```
    第1步: 收集实验数据（至少15组）
          ↓
    第2步: 在【数据管理】加载数据
          ↓
    第3步: 在【模型训练】训练随机森林
          ↓
    第4步: 在【配方筛选】生成虚拟配方
          ↓
    第5步: 查看Top3推荐配方
          ↓
    第6步: 用【打印参数】获取打印设置
          ↓
    第7步: 实际打印验证AI推荐的配方！
    ```

    ### 数据收集建议

    - 各成分含量尽量均匀分布在整个范围内
    - 覆盖成分范围的两端（低值和高值）
    - 每个配方重复测试2-3次取平均值
    - 记录所有实验条件（温度、湿度等）

    ### 结果验证

    AI推荐的配方是 **理论最优**，仍需实际打印验证：
    1. 按推荐配比制作小批量耗材
    2. 打印标准测试件（如拉伸样条）
    3. 测试力学性能
    4. 将新数据加入模型，迭代优化
    """)

with tabs[4]:
    st.markdown("## 💻 代码详解")
    st.markdown("浏览本项目关键代码模块，了解AI配方预测的实现原理。")

    selected = st.selectbox(
        "选择代码文件查看",
        options=list(CODE_EXPLANATIONS.keys()),
        format_func=lambda x: CODE_EXPLANATIONS[x]["title"],
        key="code_viewer"
    )

    info = CODE_EXPLANATIONS[selected]
    st.markdown(f"### {info['title']}")

    for section in info["sections"]:
        with st.expander(section["title"], expanded=True):
            st.markdown(section["explanation"])
            st.code(section["code"].strip(), language="python")

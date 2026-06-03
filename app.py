"""
AI-3D咖啡渣材料配方预测系统
主应用入口
"""
import streamlit as st
import os
import sys

# 设置页面配置 - 必须在最前面
st.set_page_config(
    page_title="AI-3D咖啡渣材料配方预测系统",
    page_icon="☕",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'About': "# AI-3D咖啡渣材料配方预测系统\n基于随机森林的智能配方预测",
    }
)

# 自定义CSS样式
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        padding: 1rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #666;
        text-align: center;
    }
    .metric-card {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem;
    }
    .stMetric {
        background-color: #f0f2f6;
        padding: 10px;
        border-radius: 5px;
    }
    div[data-testid="stMetricValue"] {
        font-size: 1.8rem;
    }
    .nav-card {
        background: #f8f9fa;
        padding: 1.2rem;
        border-radius: 8px;
        border-left: 4px solid #1f77b4;
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# 初始化session state
if 'data_loaded' not in st.session_state:
    st.session_state['data_loaded'] = False
if 'model_trained' not in st.session_state:
    st.session_state['model_trained'] = False

# 主标题
st.markdown("<h1 class='main-header'>☕ AI-3D咖啡渣材料配方预测系统</h1>", unsafe_allow_html=True)
st.markdown("<p class='sub-header'>基于随机森林的智能材料配方预测与3D打印参数推荐</p>", unsafe_allow_html=True)

# 简介
st.markdown("""
### 🎯 系统简介

本系统利用AI机器学习技术，帮助您：

- **智能预测** 最佳材料配方组合
- **虚拟筛选** 上万种配方可能性
- **自动推荐** 3D打印参数配置
- **科普教育** 理解AI材料研发原理

**核心算法：** 随机森林回归 (Random Forest Regression)

**应用场景：** 废弃咖啡渣 + PLA塑料 → 环保3D打印线材
""")

# 功能导航
st.markdown("---")
st.markdown("### 📋 功能导航")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown("""
    <div class="nav-card">
    <b>📊 数据管理</b><br>
    内置示例数据 · CSV导入<br>
    手动录入实验数据
    </div>
    """, unsafe_allow_html=True)
    if st.button("前往数据管理", key="nav_data", use_container_width=True):
        st.switch_page("pages/1_📊_数据管理.py")

with col2:
    st.markdown("""
    <div class="nav-card">
    <b>🧠 模型训练</b><br>
    随机森林算法 · R²评估<br>
    特征重要性分析
    </div>
    """, unsafe_allow_html=True)
    if st.button("前往模型训练", key="nav_model", use_container_width=True):
        st.switch_page("pages/2_🧠_模型训练.py")

with col3:
    st.markdown("""
    <div class="nav-card">
    <b>🔍 配方筛选</b><br>
    虚拟配方生成 · Top推荐<br>
    协同效应分析
    </div>
    """, unsafe_allow_html=True)
    if st.button("前往配方筛选", key="nav_formula", use_container_width=True):
        st.switch_page("pages/3_🔍_配方筛选.py")

with col4:
    st.markdown("""
    <div class="nav-card">
    <b>🖨️ 打印参数</b><br>
    智能温度推荐 · 速度计算<br>
    防堵头策略
    </div>
    """, unsafe_allow_html=True)
    if st.button("前往打印参数", key="nav_print", use_container_width=True):
        st.switch_page("pages/4_🖨️_打印参数.py")

# 快速开始指南
st.markdown("---")
st.markdown("### 🚀 快速开始指南")

st.markdown("""
**推荐使用流程：**

1. **数据准备** → 在【数据管理】加载示例数据（15组）
2. **模型训练** → 在【模型训练】点击「开始训练」
3. **配方筛选** → 在【配方筛选】生成推荐配方
4. **参数查看** → 在【打印参数】获取智能推荐
5. **结果分析** → 在【可视分析】查看图表解读
6. **实验配置** → 在【实验配置】设计验证实验

**新手提示：**
- 使用内置示例数据可快速体验全流程
- 点击各页面的「💡 使用帮助」了解更多
- 【科普教程】页面有完整的原理讲解
""")

# 系统状态显示
st.markdown("---")
st.markdown("### 📊 系统状态")

# 获取实际状态
try:
    from core import data_engine, ml_engine
    data_count = data_engine.get_data_count()
    model_status = "✅ 已训练" if ml_engine.is_trained else "⏳ 未训练"
except Exception:
    data_count = 0
    model_status = "⏳ 未训练"

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("数据量", f"{data_count} 组", delta=None if data_count >= 15 else f"还需{15-data_count}组",
              help="最少需要15组数据才能训练模型")

with col2:
    st.metric("模型状态", model_status, help="训练模型后才能进行配方筛选和预测")

with col3:
    model_r2 = f"{ml_engine.metrics.get('r2', 0):.3f}" if hasattr(ml_engine, 'is_trained') and ml_engine.is_trained else "-"
    st.metric("模型 R²", model_r2, help="决定系数，>0.85 优秀，0.70-0.85 可用")

# 页面快捷入口 - 第二行
st.markdown("---")
col1, col2, col3, col4 = st.columns(4)

with col1:
    if st.button("📈 可视分析", use_container_width=True):
        st.switch_page("pages/5_📈_可视分析.py")
with col2:
    if st.button("📜 历史记录", use_container_width=True):
        st.switch_page("pages/6_📜_历史记录.py")
with col3:
    if st.button("📚 科普教程", use_container_width=True):
        st.switch_page("pages/7_📚_科普教程.py")
with col4:
    if st.button("⚙️ 材料配置", use_container_width=True):
        st.switch_page("pages/9_⚙️_材料配置.py")

# 底部信息
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #888;'>
    <p>AI-3D咖啡渣材料配方预测系统 | 基于研究报告《基于AI算法辅助的废弃咖啡渣3D打印材料研制》</p>
    <p style='font-size: 0.8rem;'>技术栈：Streamlit + Scikit-learn + Plotly + Pandas</p>
</div>
""", unsafe_allow_html=True)

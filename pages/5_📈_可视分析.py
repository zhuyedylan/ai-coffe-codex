"""可视分析页面"""
import streamlit as st
import pandas as pd
import numpy as np
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core import ml_engine, data_engine, viz_engine, material_config

st.header("📈 可视分析")
st.markdown("多维可视化图表，深入理解配方数据与模型表现")

if not ml_engine.is_trained:
    st.warning("⚠️ 请先训练模型，本页面需要模型预测结果")
    st.info("💡 前往【模型训练】页面完成训练后返回")
    st.stop()

current_data = data_engine.get_data()
target_name = ml_engine.get_target_name()
materials = material_config.get_materials()
labels_map = material_config.get_feature_labels()

st.success("✅ 模型已就绪，以下展示各项分析图表")

# 1. 预测 vs 实际
st.markdown("---")
st.subheader("🎯 预测值 vs 实际值")
st.markdown("**解读：** 点越靠近对角线，预测越准确。R²值衡量模型整体表现。")

if target_name in current_data.columns and ml_engine.model is not None:
    X = current_data[ml_engine.feature_cols].values
    y = current_data[target_name].values
    y_pred = ml_engine.model.predict(X)

    fig = viz_engine.create_scatter_plot(pd.Series(y), pd.Series(y_pred), ml_engine.metrics['r2'])
    st.plotly_chart(fig, use_container_width=True)
else:
    st.warning("当前数据中缺少目标变量列")

# 2. 特征重要性
st.markdown("---")
st.subheader("🔬 特征重要性排名")
st.markdown("**解读：** 各成分对配方评分的贡献度百分比，数值越大越关键。")

fig = viz_engine.create_feature_importance_bar(ml_engine.feature_importance)
st.plotly_chart(fig, use_container_width=True)

# 3. 相关性热力图
st.markdown("---")
st.subheader("📊 成分相关性热力图")
st.markdown("**解读：** 红色表示正相关，蓝色表示负相关。数值为相关系数。")

if len(current_data) > 0:
    fig_heatmap = viz_engine.create_correlation_heatmap(current_data)
    st.plotly_chart(fig_heatmap, use_container_width=True)

# 4. 配方空间分布
if 'top_formulas' in st.session_state:
    st.markdown("---")
    st.subheader("🌐 配方空间3D分布")
    st.markdown("**解读：** 观察高分（亮色）配方的聚集区域，定位最佳配方区间。")

    fig_3d = viz_engine.create_3d_scatter(st.session_state['top_formulas'])
    st.plotly_chart(fig_3d, use_container_width=True)
else:
    st.info("💡 前往【配方筛选】页面生成虚拟配方后，可在此查看3D空间分布图")

# 5. 参数趋势
st.markdown("---")
st.subheader("📈 配方成分趋势分析")
st.markdown("**解读：** 查看不同成分取值与评分的关系趋势。")

if 'top_formulas' in st.session_state:
    formulas = st.session_state['top_formulas']
    target = material_config.get_active_target_variable()
    pred_col = f'predicted_{target["name"]}' if target else 'predicted_score'

    # 选择一个成分查看趋势
    selected_mat = st.selectbox(
        "选择成分查看趋势",
        options=[m['name'] for m in materials],
        format_func=lambda x: labels_map.get(x, x)
    )

    if selected_mat in formulas.columns:
        fig_trend = {
            'data': [
                {
                    'x': formulas[selected_mat].values,
                    'y': formulas[pred_col].values,
                    'mode': 'markers',
                    'type': 'scatter',
                    'marker': {'color': 'rgba(31, 119, 180, 0.6)', 'size': 6},
                    'name': '虚拟配方'
                }
            ],
            'layout': {
                'title': f'{labels_map.get(selected_mat)} 与 预测评分的关系',
                'xaxis': {'title': labels_map.get(selected_mat, selected_mat)},
                'yaxis': {'title': '预测评分'},
                'template': 'plotly_white',
                'height': 400
            }
        }
        st.plotly_chart(fig_trend, use_container_width=True)
else:
    st.info("💡 生成虚拟配方后可在本页查看更多分析图表")

"""模型训练页面"""
import streamlit as st
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core import ml_engine, data_engine, viz_engine, storage_engine

st.header("🧠 模型训练")
st.markdown("使用随机森林算法训练配方预测模型")

with st.expander("💡 使用帮助"):
    st.markdown("""
    - **决策树数量**：越多模型越稳定，但训练越慢
    - **最大深度**：控制树的复杂度，防止过拟合
    - **数据要求**：至少15组实验数据
    - **R² > 0.85** 说明模型表现优秀
    """)

st.subheader("⚙️ 模型参数设置")

col1, col2 = st.columns(2)
with col1:
    n_estimators = st.slider("决策树数量", 10, 200, 50, 10,
                             help="随机森林中决策树的数量，越多越稳定")
with col2:
    max_depth_val = st.slider("最大深度", 3, 20, 10, 1,
                              help="限制每棵树的最大深度，防止过拟合")
max_depth = max_depth_val if max_depth_val < 20 else None

st.markdown("---")
st.subheader("📊 数据状态")

data_count = data_engine.get_data_count()
st.metric("当前数据量", f"{data_count} 组", delta=None if data_count >= 15 else f"还需{15-data_count}组")

if data_count < 15:
    st.warning("⚠️ 数据量不足15组，请先在【数据管理】页面加载数据")
else:
    st.success("✅ 数据量满足训练要求")

if st.button("🚀 开始训练模型", disabled=data_count < 15, use_container_width=True):
    with st.spinner("🔄 正在训练随机森林模型..."):
        current_data = data_engine.get_data()
        config = {
            'n_estimators': n_estimators,
            'max_depth': max_depth
        }
        try:
            metrics = ml_engine.train(current_data, config)
            storage_engine.save_model_training(metrics, config, ml_engine.feature_importance)
            st.success("✅ 模型训练完成！")
            st.rerun()
        except Exception as e:
            st.error(f"训练失败: {e}")

if ml_engine.is_trained:
    st.markdown("---")
    st.subheader("📈 训练结果")

    col1, col2, col3 = st.columns(3)
    col1.metric("R² 决定系数", f"{ml_engine.metrics['r2']:.3f}",
                help=">0.85优秀，0.70-0.85可用")
    col2.metric("MSE 均方误差", f"{ml_engine.metrics['mse']:.3f}",
                help="值越小越好")
    col3.metric("训练数据量", f"{ml_engine.metrics['data_count']} 组")

    st.subheader("特征重要性")
    fig = viz_engine.create_feature_importance_bar(ml_engine.feature_importance)
    st.plotly_chart(fig, use_container_width=True)

    # 特征重要性表格
    st.subheader("特征贡献明细")
    importance_data = [{"成分": k, "贡献度": f"{v*100:.2f}%"}
                       for k, v in sorted(ml_engine.feature_importance.items(),
                                          key=lambda x: x[1], reverse=True)]
    st.dataframe(importance_data, use_container_width=True)
else:
    st.info("💡 加载数据后，点击上方按钮开始训练")

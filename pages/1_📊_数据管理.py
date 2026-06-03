"""数据管理页面"""
import streamlit as st
import pandas as pd
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core import data_engine, material_config

st.header("📊 数据管理")
st.markdown("管理用于模型训练的实验配方数据")

materials = material_config.get_materials()
target = material_config.get_active_target_variable()

with st.expander("💡 使用帮助"):
    st.markdown("""
    有三种数据来源可选：
    - **内置示例数据**：快速体验15组虚拟实验数据
    - **导入CSV文件**：上传包含实验数据的CSV文件
    - **手动添加**：逐条录入实验配方和评分
    
    **数据要求**：至少15组数据才能训练模型
    """)

st.subheader("数据来源选择")
tabs = st.tabs(["内置示例数据", "导入CSV文件", "手动添加"])

with tabs[0]:
    st.markdown("点击下方按钮加载内置的15组示例实验数据，快速体验全流程。")
    if st.button("📥 加载内置示例数据", use_container_width=True):
        sample_df = data_engine.get_sample_data()
        data_engine.set_data(sample_df)
        st.success(f"✅ 已加载 {len(sample_df)} 组示例数据！")
        st.rerun()

with tabs[1]:
    st.markdown("上传您自己的实验数据CSV文件。")
    uploaded_file = st.file_uploader("选择CSV文件（UTF-8编码）", type=['csv'])
    if uploaded_file is not None:
        try:
            df = pd.read_csv(uploaded_file)
            st.dataframe(df, use_container_width=True)
            if st.button("✅ 确认使用此数据", use_container_width=True):
                data_engine.set_data(df)
                st.success(f"✅ 已导入 {len(df)} 条数据！")
                st.rerun()
        except Exception as e:
            st.error(f"读取CSV文件失败: {e}")

with tabs[2]:
    st.markdown("手动录入一组实验配方数据。")
    with st.form("add_form"):
        cols = st.columns(2)
        input_values = {}
        for i, mat in enumerate(materials):
            col = cols[i % 2]
            with col:
                slider_min = float(mat['range'][0])
                slider_max = float(mat['range'][1])
                slider_default = float(mat['default_value'])
                input_values[mat['name']] = st.slider(
                    f"{mat['label']} ({mat['range'][0]}-{mat['range'][1]}%)",
                    slider_min, slider_max, slider_default,
                    help=mat.get('description', '')
                )

        if target:
            score = st.slider(
                f"{target['label']} ({target['range'][0]}-{target['range'][1]})",
                float(target['range'][0]), float(target['range'][1]), 7.0, 0.5
            )
            input_values[target['name']] = score

        submitted = st.form_submit_button("➕ 添加这条数据", use_container_width=True)
        if submitted:
            data_engine.add_record(input_values)
            st.success("✅ 数据已添加！")
            st.rerun()

st.markdown("---")
st.subheader("📋 当前数据")
current_data = data_engine.get_data()
col1, col2, col3 = st.columns(3)
col1.metric("数据量", f"{len(current_data)} 组")
col2.metric("特征数", len(materials))
col3.metric("目标变量", target['label'] if target else 'score')

if len(current_data) > 0:
    st.dataframe(current_data, use_container_width=True)
    if st.button("🗑️ 清空数据", use_container_width=True):
        data_engine.clear_data()
        st.rerun()
else:
    st.info("当前没有数据，请通过上述方式加载数据。")

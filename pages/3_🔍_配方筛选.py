"""配方筛选页面"""
import streamlit as st
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core import ml_engine, material_config, storage_engine, viz_engine

st.header("🔍 配方筛选")
st.markdown("虚拟生成大量配方组合，通过AI模型筛选最优推荐")

if not ml_engine.is_trained:
    st.warning("⚠️ 请先在【模型训练】页面完成训练")
    st.info("💡 训练完成后，本页面将自动可用")
    st.stop()

materials = material_config.get_materials()
target = material_config.get_active_target_variable()

with st.expander("💡 使用帮助"):
    st.markdown("""
    - **虚拟配方数量**：AI将随机生成成千上万种配方组合
    - **成分范围**：可限制各成分的取值范围
    - **Top配方**：根据模型预测评分自动排序
    - **3D空间图**：直观展示最佳配方的参数区间
    """)

st.subheader("🎯 筛选条件设置")

n_samples = st.slider("虚拟配方数量", 500, 10000, 5000, 500,
                       help="越多越可能找到最优解，但耗时更长")

st.markdown("**成分范围约束**（可选限制搜索范围）")
range_values = {}
cols = st.columns(2)
for i, mat in enumerate(materials):
    col = cols[i % 2]
    with col:
        default_min = max(mat['range'][0], mat['default_value'] - 20)
        default_max = min(mat['range'][1], mat['default_value'] + 20)
        range_values[mat['name']] = st.slider(
            f"{mat['label']} 范围 ({mat['range'][0]}-{mat['range'][1]}%)",
            float(mat['range'][0]), float(mat['range'][1]),
            (float(default_min), float(default_max)),
            help=mat.get('description', '')
        )

config = {
    'n_samples': n_samples,
    'ranges': {k: list(v) for k, v in range_values.items()}
}

st.markdown("---")
if st.button("🚀 开始配方筛选", use_container_width=True):
    with st.spinner(f"🔄 正在生成并评估 {n_samples:,} 组虚拟配方..."):
        top_formulas = ml_engine.get_top_formulas(n=20, config=config)
        st.session_state['top_formulas'] = top_formulas
        storage_engine.save_formula_screening(top_formulas, n_samples)
        st.success(f"✅ 完成！从 {n_samples:,} 组配方中找到20个高分配方！")
        st.rerun()

if 'top_formulas' in st.session_state:
    formulas = st.session_state['top_formulas']
    pred_col = f'predicted_{target["name"]}' if target else 'predicted_score'

    st.subheader("🏆 Top 3 最佳配方推荐")

    top3 = formulas.head(3)
    medal_colors = ['#FFD700', '#C0C0C0', '#CD7F32']
    medal_icons = ['🥇', '🥈', '🥉']

    for idx, (i, row) in enumerate(top3.iterrows()):
        with st.container():
            st.markdown(f"""
            <div style="background:{medal_colors[idx]}22; padding:15px; border-radius:10px; margin:10px 0;
                        border:2px solid {medal_colors[idx]}">
                <h3>{medal_icons[idx]} Top {idx+1} 配方</h3>
            </div>
            """, unsafe_allow_html=True)

            cols = st.columns(len(materials) + 1)
            for j, mat in enumerate(materials):
                with cols[j]:
                    if mat['name'] in row:
                        st.metric(mat['label'], f"{row[mat['name']]:.1f}%")
            with cols[-1]:
                st.metric("预测评分", f"{row[pred_col]:.2f}")

    st.markdown("---")
    st.subheader("📊 Top 20 配方列表")
    display_df = formulas.head(20).copy()
    display_cols = {mat['name']: mat['label'] for mat in materials}
    display_cols[pred_col] = '预测评分'
    display_df = display_df.rename(columns=display_cols)
    st.dataframe(display_df[list(display_cols.values())].round(2), use_container_width=True)

    st.subheader("🌐 配方空间分布")
    fig = viz_engine.create_3d_scatter(formulas)
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("📈 平行坐标图 - 高分配方的参数区间")
    fig_parallel = viz_engine.create_parallel_coordinates(formulas, top_n=50)
    st.plotly_chart(fig_parallel, use_container_width=True)

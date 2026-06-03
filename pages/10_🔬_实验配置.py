"""实验配置页面 - 实验设计与DOE"""
import streamlit as st
import pandas as pd
import numpy as np
import sys, os
from itertools import product
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core import material_config, data_engine

st.header("🔬 实验配置")
st.markdown("设计实验方案，系统化探索配方空间")

with st.expander("💡 使用帮助"):
    st.markdown("""
    - **全因子实验**：对所有成分的所有水平进行组合（精确但实验数多）
    - **正交实验**：用少量实验覆盖主要影响因素
    - **自定义实验**：手动设定各成分的水平
    - 生成的实验方案可导出为CSV或直接加入数据引擎
    """)

materials = material_config.get_materials()
target = material_config.get_active_target_variable()

st.subheader("🎯 实验设计方法")

method = st.radio(
    "选择实验设计方法",
    options=["全因子设计", "正交设计", "自定义实验方案"],
    horizontal=True,
    help="全因子：完整所有组合（实验数=各水平数相乘）；正交：代表性样本"
)

if method == "全因子设计":
    st.markdown("### 设定各成分的水平数")

    levels = {}
    cols = st.columns(2)
    for i, mat in enumerate(materials):
        col = cols[i % 2]
        with col:
            n_levels = st.number_input(
                f"{mat['label']} 水平数",
                min_value=2, max_value=5, value=3,
                key=f"level_{mat['name']}",
                help=f"范围：{mat['range'][0]}-{mat['range'][1]}"
            )
            levels[mat['name']] = n_levels

    total_experiments = np.prod(list(levels.values()))
    st.info(f"📊 将生成 **{int(total_experiments)}** 组实验方案")

    if st.button("生成全因子实验方案", use_container_width=True):
        # 为每个成分生成等间隔水平
        level_values = {}
        for mat in materials:
            mat_name = mat['name']
            n = int(levels[mat_name])
            level_values[mat_name] = np.linspace(mat['range'][0], mat['range'][1], n)

        # 生成所有组合
        keys = level_values.keys()
        values = level_values.values()
        combos = list(product(*values))

        doe_df = pd.DataFrame(combos, columns=keys)

        # 四舍五入
        for col in doe_df.columns:
            doe_df[col] = doe_df[col].round(1)

        st.session_state['doe_plan'] = doe_df
        st.success(f"✅ 已生成 {len(doe_df)} 组实验方案！")

elif method == "正交设计":
    st.markdown("### 正交实验配置")

    st.markdown("""
    正交设计通过部分代表性实验覆盖主要影响因素，大幅减少实验次数。

    推荐：3因素3水平 → 9组实验（而非27组）
    """)

    n_suggested = st.slider("建议实验组数", 6, 50, 9,
                            help="根据因素数和水平数选择合适的实验组数")

    n_levels_dict = {}
    cols = st.columns(2)
    for i, mat in enumerate(materials):
        col = cols[i % 2]
        with col:
            n_levels_dict[mat['name']] = st.slider(
                f"{mat['label']} 水平数",
                2, 5, 3,
                key=f"orth_{mat['name']}"
            )

    if st.button("生成正交实验方案", use_container_width=True):
        # 使用改进的拉丁超立方采样模拟正交设计
        n_exp = n_suggested

        doe_df = pd.DataFrame()
        for mat in materials:
            mat_name = mat['name']
            n = int(n_levels_dict[mat_name])
            # 生成等间隔水平，然后随机选择
            levels_arr = np.linspace(mat['range'][0], mat['range'][1], n)
            # 利用拉丁超立方思想：将区间分成n_exp份，每份选一个
            bins = np.linspace(0, 1, n_exp + 1)
            rand_vals = np.random.uniform(0, 1, n_exp)
            selected = np.floor(rand_vals * n).astype(int).clip(0, n - 1)
            doe_df[mat_name] = levels_arr[selected]

        for col in doe_df.columns:
            doe_df[col] = doe_df[col].round(1)

        st.session_state['doe_plan'] = doe_df
        st.success(f"✅ 已生成 {len(doe_df)} 组正交实验方案！")

else:  # 自定义
    st.markdown("### 自定义成分水平")

    custom_levels = {}
    for mat in materials:
        st.markdown(f"**{mat['label']}**（{mat['range'][0]}-{mat['range'][1]}%）：")
        # 默认水平
        default_levels = [
            mat['range'][0] + (mat['range'][1] - mat['range'][0]) * 0.25,
            mat['range'][0] + (mat['range'][1] - mat['range'][0]) * 0.50,
            mat['range'][0] + (mat['range'][1] - mat['range'][0]) * 0.75,
        ]
        input_str = st.text_input(
            f"输入水平值（逗号分隔）",
            value=", ".join([f"{x:.0f}" for x in default_levels]),
            key=f"custom_{mat['name']}",
            placeholder="如：20, 50, 80"
        )
        try:
            custom_levels[mat['name']] = [float(x.strip()) for x in input_str.split(",")]
        except:
            custom_levels[mat['name']] = default_levels
            st.warning(f"输入格式错误，使用默认水平")

    if st.button("生成自定义实验方案", use_container_width=True):
        keys = custom_levels.keys()
        values = custom_levels.values()
        combos = list(product(*values))

        doe_df = pd.DataFrame(combos, columns=keys)
        for col in doe_df.columns:
            doe_df[col] = doe_df[col].round(1)

        st.session_state['doe_plan'] = doe_df
        st.success(f"✅ 已生成 {len(doe_df)} 组自定义实验方案！")


# 显示生成的实验方案
st.markdown("---")
st.subheader("📋 实验方案")

if 'doe_plan' in st.session_state:
    doe_df = st.session_state['doe_plan']

    col1, col2, col3 = st.columns(3)
    col1.metric("实验组数", len(doe_df))
    col2.metric("成分数", len(materials))
    col3.metric("覆盖率", f"{len(doe_df) / (5**len(materials))*100:.1f}%") if len(materials) > 0 else None

    # 添加序号
    display_df = doe_df.copy()
    display_df.insert(0, '实验编号', range(1, len(display_df) + 1))
    st.dataframe(display_df, use_container_width=True)

    # 下载和操作
    col1, col2, col3 = st.columns(3)
    with col1:
        csv = doe_df.to_csv(index=False, encoding='utf-8-sig')
        st.download_button(
            "📥 下载CSV",
            data=csv,
            file_name="experiment_plan.csv",
            mime="text/csv",
            use_container_width=True
        )
    with col2:
        if st.button("📊 加入数据引擎", use_container_width=True):
            data_engine.set_data(doe_df)
            st.success(f"✅ 已将 {len(doe_df)} 组实验方案加载到数据引擎！")
    with col3:
        if st.button("🔄 重新生成", use_container_width=True):
            if 'doe_plan' in st.session_state:
                del st.session_state['doe_plan']
            st.rerun()
else:
    st.info("👆 选择实验设计方法并点击生成按钮")

# 实验记录表
st.markdown("---")
st.subheader("📝 实验记录模板")

st.markdown("""
方便在实验过程中记录实际测量结果的模板：
""")

# 生成带空白评分列的模板
if 'doe_plan' in st.session_state:
    template_df = st.session_state['doe_plan'].copy()
    template_df['实际评分'] = ''
    template_df['实验日期'] = ''
    template_df['备注'] = ''
    csv_template = template_df.to_csv(index=False, encoding='utf-8-sig')
    st.download_button(
        "📥 下载实验记录表（含评分列）",
        data=csv_template,
        file_name="experiment_record_template.csv",
        mime="text/csv",
        use_container_width=True
    )

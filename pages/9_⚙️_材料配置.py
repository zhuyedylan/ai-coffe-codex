"""材料配置管理页面"""
import streamlit as st
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core import material_config

st.header("⚙️ 材料配置管理")
st.markdown("管理配方中的材料成分定义")

with st.expander("💡 使用帮助"):
    st.markdown("""
    - **材料列表**：查看当前所有可用的材料成分
    - **添加材料**：新增自定义材料成分
    - 增删材料后，所有页面会自动适应变化
    - 修改会持久保存到 `data/configs/materials.json`
    """)

materials = material_config.get_materials()
target = material_config.get_active_target_variable()

st.subheader("📋 当前材料配置")
st.metric("材料数量", len(materials))

tab1, tab2 = st.tabs(["📝 材料列表", "➕ 添加材料"])

with tab1:
    for mat in materials:
        with st.expander(f"{mat['label']} ({mat['role']})"):
            st.markdown(f"""
            - **字段名：** `{mat['name']}`
            - **范围：** {mat['range'][0]} - {mat['range'][1]} {mat['unit']}
            - **默认值：** {mat['default_value']}
            - **角色：** {mat['role']}
            - **角色类型：** `{mat['role_type']}`
            - **必填：** {'是' if mat.get('is_required', False) else '否'}
            - **描述：** {mat.get('description', '无')}
            """)

            with st.expander("打印参数规则"):
                print_rules = mat.get('print_rules', {})
                st.json(print_rules)

    st.markdown("---")
    st.caption(f"目标变量：{target['label'] if target else 'score'}（{target['range'] if target else 'N/A'}）")

with tab2:
    st.markdown("添加新的材料成分到系统中。添加后将自动应用于所有页面。")

    with st.form("add_mat"):
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("字段名 (英文，如 new_material)", placeholder="example_material",
                                 help="数据列的唯一标识符，使用英文和下划线")
            label = st.text_input("显示标签", placeholder="新材料含量",
                                 help="页面上显示的中文名称")
            display_name = st.text_input("完整名称（可选）", placeholder="新材料（化学名）")

        with col2:
            range_min = st.number_input("最小值", value=0, min_value=0, max_value=100)
            range_max = st.number_input("最大值", value=50, min_value=0, max_value=100)
            default_value = st.slider("默认值", range_min, range_max,
                                      value=int((range_min + range_max) / 2))

        col1, col2 = st.columns(2)
        with col1:
            role_type = st.selectbox(
                "角色类型",
                options=["matrix", "filler", "chain_extender", "coupling_agent", "additive"],
                format_func=lambda x: {
                    'matrix': '基体材料',
                    'filler': '填料',
                    'chain_extender': '扩链剂',
                    'coupling_agent': '偶联剂',
                    'additive': '添加剂'
                }.get(x, x)
            )
            unit = st.text_input("单位", value="%")

        with col2:
            role = st.text_input("角色描述", placeholder="如：功能助剂")
            description = st.text_area("详细描述（可选）", placeholder="材料的功能和作用说明",
                                       max_chars=200)

        col1, col2 = st.columns(2)
        with col1:
            is_required = st.checkbox("必填成分", value=False)
        with col2:
            temp_adjust = st.number_input("温度调整系数", value=0.0, step=0.1,
                                          help="每增加1%对挤出温度的调整量")
            speed_adjust = st.number_input("速度调整系数", value=0.0, step=0.1,
                                           help="每增加1%对打印速度的调整量")

        submitted = st.form_submit_button("➕ 添加材料", use_container_width=True)
        if submitted:
            if not name or not label:
                st.error("字段名和显示标签不能为空！")
            else:
                print_rules = {
                    'temp_adjust_per_unit': temp_adjust,
                    'speed_adjust_per_unit': speed_adjust
                }
                success, msg = material_config.add_material(
                    name=name, label=label, display_name=display_name or label,
                    range=[range_min, range_max], default_value=default_value,
                    role=role or '添加剂', role_type=role_type,
                    description=description, is_required=is_required,
                    unit=unit, print_rules=print_rules
                )
                if success:
                    st.success(f"✅ 已添加新材料 `{name}`！")
                    st.rerun()
                else:
                    st.error(msg)

    # 添加目标变量的说明
    st.markdown("---")
    st.markdown("""
    **💡 关于目标变量**

    当前目标变量为 **{label}**（范围 {min}-{max}）。
    目标变量是模型预测的目标，即配方评分。

    修改目标变量需要编辑 `data/configs/materials.json` 中的 `target_variables` 字段。
    """.format(
        label=target['label'] if target else 'score',
        min=target['range'][0] if target else 1,
        max=target['range'][1] if target else 10
    ))

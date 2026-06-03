"""打印参数页面"""
import streamlit as st
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core import param_engine, material_config

st.header("🖨️ 打印参数建议")
st.markdown("根据配方智能推荐3D打印参数")

with st.expander("💡 使用帮助"):
    st.markdown("""
    - 调整下方各成分含量，模拟不同配方
    - 点击「生成推荐参数」获取打印设置建议
    - 每个参数下方有调整原因的说明
    - 常见问题板块提供了打印故障的解决方案
    """)

materials = material_config.get_materials()
target = material_config.get_active_target_variable()

st.subheader("📝 配方输入")
st.markdown("拖动滑块调整各成分含量")

formula = {}
cols = st.columns(2)
for i, mat in enumerate(materials):
    col = cols[i % 2]
    with col:
        formula[mat['name']] = st.slider(
            f"{mat['label']} ({mat['range'][0]}-{mat['range'][1]}%)",
            float(mat['range'][0]), float(mat['range'][1]), float(mat['default_value']),
            help=f"{mat['role']}：{mat.get('description', '')}"
        )

st.markdown("---")
if st.button("⚡ 生成推荐参数", use_container_width=True):
    params = param_engine.recommend_params(formula)
    st.session_state['print_params'] = params
    st.session_state['current_formula'] = formula
    st.success("✅ 参数推荐完成！")
    st.rerun()

if 'print_params' in st.session_state:
    params = st.session_state['print_params']

    st.subheader("🎯 推荐打印参数")

    # 温度参数
    st.markdown("**🌡️ 温度设置**")
    col1, col2 = st.columns(2)
    with col1:
        st.metric("挤出温度", f"{params['nozzle_temp']}°C",
                  help=param_engine.get_param_reason('nozzle_temp'))
    with col2:
        st.metric("热床温度", f"{params['bed_temp']}°C",
                  help=param_engine.get_param_reason('bed_temp'))

    # 速度和运动参数
    st.markdown("**⚡ 速度和运动**")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("打印速度", f"{params['print_speed']} mm/s",
                  help=param_engine.get_param_reason('print_speed'))
    with col2:
        st.metric("回抽距离", f"{params['retraction_dist']:.1f} mm",
                  help=param_engine.get_param_reason('retraction_dist'))
    with col3:
        st.metric("回抽速度", f"{params['retraction_speed']} mm/s",
                  help=param_engine.get_param_reason('retraction_speed'))

    # 其他参数
    st.markdown("**🔧 其他参数**")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("层高", f"{params['layer_height']} mm",
                  help=param_engine.get_param_reason('layer_height'))
    with col2:
        st.metric("风扇速度", f"{params['fan_speed']}%",
                  help=param_engine.get_param_reason('fan_speed'))
    with col3:
        st.metric("流量补偿", f"{params['flow_rate']}%",
                  help=param_engine.get_param_reason('flow_rate'))

    st.markdown("---")
    st.subheader("❓ 常见打印问题及解决方案")

    problems = param_engine.get_all_faqs()
    tabs = st.tabs(problems)
    for i, problem in enumerate(problems):
        with tabs[i]:
            solution = param_engine.get_faq_solution(problem)
            st.markdown(f"**{problem}**")
            if solution.get('symptoms'):
                st.markdown("**典型症状：**")
                for sym in solution['symptoms']:
                    st.markdown(f"- {sym}")
            st.markdown("**解决方案：**")
            for sol in solution['solutions']:
                st.markdown(f"- ✅ {sol}")
else:
    st.info("💡 调整上方配方后点击「生成推荐参数」")

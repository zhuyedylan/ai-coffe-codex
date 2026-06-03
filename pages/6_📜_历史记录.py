"""历史记录页面"""
import streamlit as st
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core import storage_engine

st.header("📜 历史记录")
st.markdown("查看模型训练和配方筛选的历史记录")

with st.expander("💡 使用帮助"):
    st.markdown("""
    - 每次训练模型和筛选配方都会自动记录
    - 最多保留最近50条记录
    - 可点击展开查看详情
    """)

records = storage_engine.get_history_list()
st.metric("总记录数", len(records))

if len(records) == 0:
    st.info("📭 暂无历史记录。进行模型训练或配方筛选后会自动生成记录。")
else:
    st.markdown("---")

    # 统计概览
    operation_counts = {}
    for r in records:
        op_type = r.get('operation_type', 'unknown')
        operation_counts[op_type] = operation_counts.get(op_type, 0) + 1

    st.subheader("📊 操作统计")
    cols = st.columns(len(operation_counts))
    for i, (op_type, count) in enumerate(operation_counts.items()):
        with cols[i]:
            st.metric(op_type, f"{count} 次")

    st.markdown("---")
    st.subheader("🕐 操作历史")

    for record in reversed(records[-50:]):
        op_type = record.get('operation_type', '未知操作')
        timestamp = record.get('timestamp', '')
        record_id = record.get('id', '')

        # 格式化时间戳
        time_str = timestamp
        if 'T' in timestamp:
            time_str = timestamp.replace('T', ' ').split('.')[0]

        icon = "🧠" if op_type == 'model_training' else "🔍"
        label = "模型训练" if op_type == 'model_training' else "配方筛选"

        with st.expander(f"{icon} {label} — {time_str}"):
            details = record.get('details', {})
            if op_type == 'model_training':
                metrics = details.get('metrics', {})
                if metrics:
                    col1, col2 = st.columns(2)
                    col1.metric("R²", f"{metrics.get('r2', 'N/A'):.3f}")
                    col2.metric("数据量", f"{metrics.get('data_count', 'N/A')} 组")

                importance = details.get('importance', {})
                if importance:
                    st.markdown("**特征重要性：**")
                    sorted_imp = sorted(importance.items(), key=lambda x: x[1], reverse=True)
                    for feat, imp in sorted_imp:
                        st.markdown(f"- {feat}: {imp*100:.1f}%")

            elif op_type == 'formula_screening':
                top_score = details.get('top_score', 'N/A')
                n_samples = details.get('n_samples', 'N/A')
                col1, col2 = st.columns(2)
                col1.metric("虚拟配方数", f"{n_samples:,}")
                col2.metric("最高评分", f"{top_score:.2f}")

            st.markdown(f"**记录ID：** `{record_id}`")

    # 清空按钮
    st.markdown("---")
    if st.button("🗑️ 清空所有历史记录", use_container_width=True):
        storage_engine.clear_history()
        st.success("✅ 历史记录已清空")
        st.rerun()

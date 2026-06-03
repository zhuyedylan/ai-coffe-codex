"""文献检索页面"""
import streamlit as st

st.header("🔍 文献检索")
st.markdown("相关科研文献与参考资料查阅")

with st.expander("💡 使用帮助"):
    st.markdown("""
    - 本页面整理了与咖啡渣/PLA 3D打印材料相关的研究文献
    - 可按关键词筛选或查看分类推荐的文献
    - 文献信息仅供学习参考，请查阅原文获取详细数据
    """)

# 预设文献数据库
LITERATURE_DB = [
    {
        'id': 'L001',
        'title': 'Utilization of spent coffee grounds for 3D printing filament production',
        'authors': 'Lee, H., et al.',
        'year': 2022,
        'journal': 'Journal of Cleaner Production',
        'keywords': ['coffee grounds', 'PLA', 'filament', 'mechanical properties'],
        'abstract': '研究将废弃咖啡渣作为填料加入PLA中制备3D打印线材，分析了咖啡渣含量对线材力学性能和打印质量的影响。',
        'category': '材料制备',
        'rating': 4
    },
    {
        'id': 'L002',
        'title': 'Effect of chain extender on the properties of PLA/coffee grounds composites',
        'authors': 'Zhang, Y., et al.',
        'year': 2023,
        'journal': 'Polymer Composites',
        'keywords': ['chain extender', 'ESO', 'PLA composite', 'toughness'],
        'abstract': '研究了ESO（环氧大豆油）作为扩链剂对PLA/咖啡渣复合材料的增韧效果，发现添加5% ESO可显著提升断裂伸长率。',
        'category': '改性研究',
        'rating': 5
    },
    {
        'id': 'L003',
        'title': 'Machine learning prediction of material properties for recycled polymer composites',
        'authors': 'Wang, X., et al.',
        'year': 2023,
        'journal': 'Materials & Design',
        'keywords': ['machine learning', 'random forest', 'polymer composite', 'prediction'],
        'abstract': '使用随机森林等机器学习算法预测再生聚合物复合材料的力学性能，证明了小样本数据下ML方法的有效性。',
        'category': 'AI方法',
        'rating': 5
    },
    {
        'id': 'L004',
        'title': 'Citric acid as a coupling agent for natural filler polymer composites',
        'authors': 'Kim, S., et al.',
        'year': 2021,
        'journal': 'Composites Part B: Engineering',
        'keywords': ['citric acid', 'coupling agent', 'interfacial adhesion'],
        'abstract': '探讨了柠檬酸作为偶联剂改善天然填料与聚合物基体界面结合的效果，界面结合强度提升约40%。',
        'category': '改性研究',
        'rating': 4
    },
    {
        'id': 'L005',
        'title': 'Optimization of 3D printing parameters for PLA/coffee grounds composites',
        'authors': 'Chen, L., et al.',
        'year': 2023,
        'journal': 'Additive Manufacturing',
        'keywords': ['3D printing', 'parameter optimization', 'PLA', 'coffee'],
        'abstract': '系统研究了打印温度、速度、层高对PLA/咖啡渣复合材料的打印质量影响，给出了最优参数区间。',
        'category': '打印工艺',
        'rating': 4
    },
    {
        'id': 'L006',
        'title': 'Thermal degradation behavior of PLA/natural filler composites during extrusion',
        'authors': 'Park, J., et al.',
        'year': 2022,
        'journal': 'Polymer Degradation and Stability',
        'keywords': ['thermal degradation', 'PLA', 'extrusion', 'molecular weight'],
        'abstract': '分析了PLA/天然填料复合材料在挤出过程中的热降解行为，阐明了分子链断裂的机理和抑制方法。',
        'category': '材料制备',
        'rating': 3
    },
    {
        'id': 'L007',
        'title': 'A review on natural fiber reinforced PLA composites for 3D printing',
        'authors': 'Martinez, R., et al.',
        'year': 2022,
        'journal': 'Composites Science and Technology',
        'keywords': ['review', 'natural fiber', 'PLA', '3D printing', 'biocomposite'],
        'abstract': '综述了天然纤维增强PLA复合材料在3D打印中的应用现状，包括材料选择、界面改性和打印工艺。',
        'category': '综述',
        'rating': 5
    },
    {
        'id': 'L008',
        'title': 'Epoxidized soybean oil as a biodegradable plasticizer for PLA',
        'authors': 'Liu, M., et al.',
        'year': 2021,
        'journal': 'ACS Sustainable Chemistry & Engineering',
        'keywords': ['ESO', 'epoxidized soybean oil', 'plasticizer', 'PLA', 'biodegradable'],
        'abstract': '评估了环氧大豆油作为可生物降解增塑剂在PLA中的应用效果，改善了PLA的柔韧性和加工性能。',
        'category': '改性研究',
        'rating': 4
    }
]

st.subheader("🔎 文献筛选")

col1, col2 = st.columns(2)
with col1:
    search_query = st.text_input("关键词搜索", placeholder="如：coffee, PLA, random forest...")
with col2:
    category_filter = st.multiselect(
        "研究领域",
        options=["全部", "材料制备", "改性研究", "AI方法", "打印工艺", "综述"],
        default=["全部"]
    )

# 过滤文献
filtered = LITERATURE_DB
if search_query:
    filtered = [l for l in filtered if
                search_query.lower() in l['title'].lower() or
                search_query.lower() in l['abstract'].lower() or
                any(search_query.lower() in kw.lower() for kw in l['keywords'])]

if "全部" not in category_filter and category_filter:
    filtered = [l for l in filtered if l['category'] in category_filter]

st.markdown(f"**共找到 {len(filtered)} 篇相关文献**")
st.markdown("---")

# 按年份分组显示
years = sorted(set(l['year'] for l in filtered), reverse=True)
for year in years:
    year_lits = [l for l in filtered if l['year'] == year]
    st.markdown(f"### 📅 {year}")

    for lit in year_lits:
        stars = "⭐" * lit['rating']
        with st.expander(f"{lit['title']}  {stars}"):
            st.markdown(f"""
            **作者：** {lit['authors']}
            **期刊：** {lit['journal']} ({lit['year']})
            **类别：** {lit['category']}
            **关键词：** `{'`, `'.join(lit['keywords'])}`

            **摘要：** {lit['abstract']}
            """)

# 研究趋势
st.markdown("---")
st.subheader("📊 研究趋势")

st.markdown("""
| 研究方向 | 热度 | 说明 |
|---------|------|------|
| 咖啡渣PLA线材制备 | 🔥🔥🔥🔥🔥 | 最活跃的研究方向 |
| 界面改性/偶联剂 | 🔥🔥🔥🔥 | 提升性能的关键 |
| AI辅助配方优化 | 🔥🔥🔥🔥 | 新兴热点方向 |
| 3D打印工艺优化 | 🔥🔥🔥 | 实用化研究 |
| 降解与回收 | 🔥🔥🔥 | 环保相关 |
""")

st.info("💡 提示：本页面文献数据为示例展示。实际使用中可通过网络检索或导入真实文献数据。")

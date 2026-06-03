"""
可视化引擎 - 图表生成
"""
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from typing import Dict, List, Optional

def _get_material_config():
    from .material_config import material_config
    return material_config

COLORS = {
    'features': ['#2ca02c', '#ff7f0e', '#1f77b4', '#d62728', '#9467bd', '#8c564b', '#e377c2', '#7f7f7f'],
}

# 图表解读文案
CHART_INTERPRETATIONS = {
    'scatter': {
        'title': '预测值 vs 实际值',
        'description': '散点图用于评估模型预测准确度。点越靠近对角线，预测越准确。',
        'metrics': {
            'r2': '决定系数 R²，衡量模型解释方差的比例。>0.85 优秀，0.70-0.85 可用。',
            'mse': '均方误差 MSE，衡量预测误差的平均大小。值越小越好。'
        }
    },
    'importance': {
        'title': '特征重要性排名',
        'description': '横轴表示特征对预测结果的贡献度百分比。数值越大，该成分对配方性能影响越大。',
        'interpretation': '如果某个特征的贡献度远高于其他特征，说明该成分是影响配方的关键因素。'
    },
    '3d_scatter': {
        'title': '配方空间分布',
        'description': '三维散点图展示虚拟配方在参数空间中的分布。颜色表示预测评分（深色=高分）。',
        'interpretation': '高分区域集中的位置，就是最佳配方所在的参数区间。'
    }
}


class VizEngine:
    """可视化引擎"""

    def create_scatter_plot(self, y_true, y_pred, r2=None) -> go.Figure:
        """创建预测vs实际散点图"""
        fig = go.Figure()
        min_val = min(y_true.min(), y_pred.min())
        max_val = max(y_true.max(), y_pred.max())

        fig.add_trace(go.Scatter(x=[min_val, max_val], y=[min_val, max_val],
                                 mode='lines', name='理想线', line=dict(color='gray', dash='dash')))
        fig.add_trace(go.Scatter(x=y_true, y=y_pred, mode='markers', name='预测点',
                                 marker=dict(color='#1f77b4', size=10, line=dict(width=1, color='DarkSlateGrey'))))

        if r2:
            fig.add_annotation(x=0.02, y=0.98, xref='paper', yref='paper',
                               text=f'R² = {r2:.3f}', showarrow=False,
                               font=dict(size=14, color='green'),
                               bgcolor='rgba(255,255,255,0.7)',
                               bordercolor='green', borderwidth=1)

        fig.update_layout(title='预测值 vs 实际值', xaxis_title='实际评分',
                          yaxis_title='预测评分', template='plotly_white', height=400)
        return fig

    def create_feature_importance_bar(self, importance: Dict) -> go.Figure:
        """创建特征重要性条形图"""
        mc = _get_material_config()
        labels_map = mc.get_feature_labels()

        sorted_items = sorted(importance.items(), key=lambda x: x[1], reverse=True)
        labels = [labels_map.get(k, k) for k, v in sorted_items]
        values = [v * 100 for k, v in sorted_items]

        fig = go.Figure(go.Bar(x=values, y=labels, orientation='h',
                               marker=dict(color=COLORS['features'][:len(labels)]),
                               text=[f'{v:.1f}%' for v in values],
                               textposition='outside'))
        fig.update_layout(title='特征重要性排名', xaxis_title='贡献度 (%)',
                          yaxis_title='成分', template='plotly_white', height=350,
                          xaxis=dict(range=[0, max(values) * 1.2]))
        return fig

    def create_3d_scatter(self, formulas: pd.DataFrame) -> go.Figure:
        """创建3D配方空间分布图"""
        mc = _get_material_config()
        materials = mc.get_materials()
        labels_map = mc.get_feature_labels()
        target = mc.get_active_target_variable()
        pred_col = f'predicted_{target["name"]}' if target else 'predicted_score'

        if len(materials) < 2:
            return go.Figure()

        x_feature = materials[0]['name']
        y_feature = materials[1]['name']

        fig = go.Figure(data=go.Scatter3d(
            x=formulas[x_feature], y=formulas[y_feature], z=formulas[pred_col],
            mode='markers',
            marker=dict(size=4, color=formulas[pred_col],
                        colorscale='Viridis', showscale=True,
                        colorbar=dict(title='预测评分')),
            text=[f'{labels_map.get(x_feature)}: {x:.1f}<br>'
                  f'{labels_map.get(y_feature)}: {y:.1f}<br>'
                  f'评分: {z:.2f}'
                  for x, y, z in zip(formulas[x_feature], formulas[y_feature], formulas[pred_col])],
            hoverinfo='text'))

        fig.update_layout(title='配方空间分布', height=500,
                          scene=dict(
                              xaxis_title=labels_map.get(x_feature, x_feature),
                              yaxis_title=labels_map.get(y_feature, y_feature),
                              zaxis_title='预测评分',
                              camera=dict(eye=dict(x=1.5, y=1.5, z=1.2))
                          ),
                          margin=dict(l=0, r=0, b=0, t=40))
        return fig

    def create_correlation_heatmap(self, data: pd.DataFrame) -> go.Figure:
        """创建相关热力图"""
        mc = _get_material_config()
        labels_map = mc.get_feature_labels()
        target = mc.get_active_target_variable()

        # 只选择配方相关的列
        plot_cols = [c for c in data.columns if c in labels_map or
                     (target and c == target['name'])]
        plot_labels = [labels_map.get(c, c) for c in plot_cols]

        corr_matrix = data[plot_cols].corr()

        fig = go.Figure(data=go.Heatmap(
            z=corr_matrix.values,
            x=plot_labels,
            y=plot_labels,
            colorscale='RdBu_r',
            zmin=-1, zmax=1,
            text=np.round(corr_matrix.values, 2),
            texttemplate='%{text}',
            textfont=dict(size=10)))

        fig.update_layout(title='成分相关性热力图', height=500,
                          xaxis=dict(tickangle=45),
                          template='plotly_white')
        return fig

    def create_parallel_coordinates(self, formulas: pd.DataFrame, top_n: int = 50) -> go.Figure:
        """创建平行坐标图"""
        mc = _get_material_config()
        labels_map = mc.get_feature_labels()
        target = mc.get_active_target_variable()
        pred_col = f'predicted_{target["name"]}' if target else 'predicted_score'

        top_formulas = formulas.head(top_n)

        dimensions = []
        for mat in mc.get_materials():
            if mat['name'] in top_formulas.columns:
                dimensions.append(dict(
                    label=mat['label'],
                    values=top_formulas[mat['name']],
                    range=mat['range']
                ))

        if pred_col in top_formulas.columns:
            dimensions.append(dict(
                label='预测评分',
                values=top_formulas[pred_col],
                range=[top_formulas[pred_col].min(), top_formulas[pred_col].max()]
            ))

        fig = go.Figure(data=go.Parcoords(
            line=dict(color=top_formulas[pred_col], colorscale='Viridis', showscale=True),
            dimensions=dimensions
        ))
        fig.update_layout(title='Top 配方平行坐标', height=500)
        return fig


# 全局实例
viz_engine = VizEngine()

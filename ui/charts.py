"""Charts - Biểu đồ Plotly cho báo cáo."""

import plotly.graph_objects as go
import plotly.express as px
from typing import List, Dict
from utils.constants import CHART_COLORS


def income_expense_bar(trend_data: List[dict]) -> go.Figure:
    """Biểu đồ cột thu nhập / chi tiêu theo tháng."""
    months = [d["month"] for d in trend_data]
    incomes = [d.get("income", 0) for d in trend_data]
    expenses = [d.get("expense", 0) for d in trend_data]

    fig = go.Figure()
    fig.add_trace(go.Bar(
        name="Thu nhập", x=months, y=incomes,
        marker_color="#38ef7d", text=[f"{v/1e6:.1f}M" for v in incomes],
        textposition="outside",
    ))
    fig.add_trace(go.Bar(
        name="Chi tiêu", x=months, y=expenses,
        marker_color="#f45c43", text=[f"{v/1e6:.1f}M" for v in expenses],
        textposition="outside",
    ))
    fig.update_layout(
        barmode="group",
        margin=dict(l=10, r=10, t=30, b=10),
        height=350,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        xaxis_title="",
        yaxis_title="",
        yaxis_tickformat=",",
        font=dict(size=12),
    )
    return fig


def expense_pie(category_data: List[dict]) -> go.Figure:
    """Biểu đồ tròn chi tiêu theo danh mục."""
    labels = [d["category"] for d in category_data]
    values = [d["total"] for d in category_data]

    fig = go.Figure(data=[go.Pie(
        labels=labels,
        values=values,
        hole=0.4,
        marker_colors=CHART_COLORS[:len(labels)],
        textinfo="label+percent",
        textposition="outside",
    )])
    fig.update_layout(
        margin=dict(l=10, r=10, t=30, b=10),
        height=350,
        showlegend=False,
        font=dict(size=11),
    )
    return fig


def cashflow_line(trend_data: List[dict]) -> go.Figure:
    """Biểu đồ đường dòng tiền ròng."""
    months = [d["month"] for d in trend_data]
    nets = [d.get("net", 0) for d in trend_data]

    colors = ["#38ef7d" if n >= 0 else "#f45c43" for n in nets]

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=months, y=nets,
        mode="lines+markers",
        line=dict(color="#2196F3", width=2),
        marker=dict(size=8, color=colors),
        fill="tozeroy",
        fillcolor="rgba(33,150,243,0.1)",
        name="Dòng tiền ròng",
    ))
    fig.add_hline(y=0, line_dash="dash", line_color="grey", opacity=0.5)
    fig.update_layout(
        margin=dict(l=10, r=10, t=30, b=10),
        height=300,
        yaxis_tickformat=",",
        font=dict(size=12),
    )
    return fig


def budget_gauge(spent: float, budget: float, label: str = "") -> go.Figure:
    """Gauge chart cho tiến độ ngân sách."""
    pct = (spent / budget * 100) if budget > 0 else 0

    if pct >= 100:
        bar_color = "#eb3349"
    elif pct >= 80:
        bar_color = "#F09819"
    else:
        bar_color = "#11998e"

    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=pct,
        number={"suffix": "%"},
        delta={"reference": 100, "decreasing": {"color": "#11998e"}, "increasing": {"color": "#eb3349"}},
        gauge={
            "axis": {"range": [0, 120]},
            "bar": {"color": bar_color},
            "steps": [
                {"range": [0, 70], "color": "#e8f5e9"},
                {"range": [70, 90], "color": "#fff3e0"},
                {"range": [90, 120], "color": "#ffebee"},
            ],
            "threshold": {"line": {"color": "red", "width": 2}, "thickness": 0.75, "value": 100},
        },
        title={"text": label},
    ))
    fig.update_layout(
        margin=dict(l=20, r=20, t=50, b=10),
        height=250,
        font=dict(size=12),
    )
    return fig


def goal_progress_bar(goals_data: List[dict]) -> go.Figure:
    """Biểu đồ ngang tiến độ mục tiêu."""
    names = [d["goal"].name for d in goals_data]
    percentages = [min(100, d["percentage"]) for d in goals_data]
    colors = ["#38ef7d" if p >= 100 else "#2196F3" if p >= 50 else "#F09819" for p in percentages]

    fig = go.Figure(go.Bar(
        x=percentages,
        y=names,
        orientation="h",
        marker_color=colors,
        text=[f"{p:.0f}%" for p in percentages],
        textposition="auto",
    ))
    fig.add_vline(x=100, line_dash="dash", line_color="red", opacity=0.5)
    fig.update_layout(
        margin=dict(l=10, r=10, t=30, b=10),
        height=max(200, len(names) * 50),
        xaxis_title="Tiến độ (%)",
        yaxis_title="",
        font=dict(size=12),
    )
    return fig


def daily_expense_bar(daily_data: List[dict]) -> go.Figure:
    """Biểu đồ chi tiêu hàng ngày."""
    dates = [d["date"] for d in daily_data]
    totals = [d["total"] for d in daily_data]

    fig = go.Figure(go.Bar(
        x=dates, y=totals,
        marker_color="#f45c43",
        opacity=0.8,
    ))
    # Đường trung bình
    if totals:
        avg = sum(totals) / len(totals)
        fig.add_hline(y=avg, line_dash="dash", line_color="#2196F3",
                      annotation_text=f"TB: {avg/1e6:.1f}M")
    fig.update_layout(
        margin=dict(l=10, r=10, t=30, b=10),
        height=300,
        xaxis_title="",
        yaxis_title="",
        yaxis_tickformat=",",
        font=dict(size=11),
    )
    return fig


def account_balance_donut(accounts: List[dict]) -> go.Figure:
    """Biểu đồ donut phân bổ tài sản."""
    labels = [a["name"] for a in accounts if a["balance"] > 0]
    values = [a["balance"] for a in accounts if a["balance"] > 0]

    if not labels:
        labels = ["Chưa có dữ liệu"]
        values = [1]

    fig = go.Figure(data=[go.Pie(
        labels=labels,
        values=values,
        hole=0.5,
        marker_colors=CHART_COLORS[:len(labels)],
        textinfo="label+percent",
        textposition="inside",
    )])
    fig.update_layout(
        margin=dict(l=10, r=10, t=30, b=10),
        height=350,
        font=dict(size=11),
        showlegend=True,
        legend=dict(orientation="h", yanchor="top", y=-0.05),
    )
    return fig

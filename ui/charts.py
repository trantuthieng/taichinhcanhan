"""Charts - Biểu đồ Plotly cho báo cáo (dark glassmorphism theme)."""

import plotly.graph_objects as go
import plotly.express as px
from typing import List, Dict
from utils.constants import CHART_COLORS

# Dark theme chart palette
DARK_CHART_COLORS = [
    "#6C5CE7", "#00cec9", "#ff6b6b", "#fdcb6e",
    "#a29bfe", "#74b9ff", "#e84393", "#55efc4",
    "#fd79a8", "#81ecec", "#fab1a0", "#dfe6e9",
]

_DARK_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Inter, sans-serif", size=12, color="#a0a0b8"),
    margin=dict(l=10, r=10, t=30, b=10),
    xaxis=dict(
        gridcolor="rgba(108,92,231,0.08)",
        zerolinecolor="rgba(108,92,231,0.15)",
    ),
    yaxis=dict(
        gridcolor="rgba(108,92,231,0.08)",
        zerolinecolor="rgba(108,92,231,0.15)",
    ),
    legend=dict(
        bgcolor="rgba(0,0,0,0)",
        font=dict(color="#a0a0b8"),
    ),
)


def _apply_dark(fig: go.Figure, **extra) -> go.Figure:
    layout = {**_DARK_LAYOUT, **extra}
    fig.update_layout(**layout)
    return fig


def income_expense_bar(trend_data: List[dict]) -> go.Figure:
    """Biểu đồ cột thu nhập / chi tiêu theo tháng."""
    months = [d["month"] for d in trend_data]
    incomes = [d.get("income", 0) for d in trend_data]
    expenses = [d.get("expense", 0) for d in trend_data]

    fig = go.Figure()
    fig.add_trace(go.Bar(
        name="Thu nhập", x=months, y=incomes,
        marker_color="#00cec9",
        marker_line=dict(width=0),
        text=[f"{v/1e6:.1f}M" for v in incomes],
        textposition="outside",
        textfont=dict(color="#00cec9", size=10),
    ))
    fig.add_trace(go.Bar(
        name="Chi tiêu", x=months, y=expenses,
        marker_color="#ff6b6b",
        marker_line=dict(width=0),
        text=[f"{v/1e6:.1f}M" for v in expenses],
        textposition="outside",
        textfont=dict(color="#ff6b6b", size=10),
    ))
    return _apply_dark(fig,
        barmode="group",
        height=350,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        yaxis_tickformat=",",
        bargap=0.25,
        bargroupgap=0.1,
    )


def expense_pie(category_data: List[dict]) -> go.Figure:
    """Biểu đồ tròn chi tiêu theo danh mục."""
    labels = [d["category"] for d in category_data]
    values = [d["total"] for d in category_data]

    fig = go.Figure(data=[go.Pie(
        labels=labels,
        values=values,
        hole=0.55,
        marker=dict(
            colors=DARK_CHART_COLORS[:len(labels)],
            line=dict(color="rgba(15,15,26,0.8)", width=2),
        ),
        textinfo="label+percent",
        textposition="outside",
        textfont=dict(color="#a0a0b8", size=11),
        pull=[0.03] * len(labels),
    )])
    return _apply_dark(fig, height=350, showlegend=False)


def cashflow_line(trend_data: List[dict]) -> go.Figure:
    """Biểu đồ đường dòng tiền ròng."""
    months = [d["month"] for d in trend_data]
    nets = [d.get("net", 0) for d in trend_data]

    colors = ["#00cec9" if n >= 0 else "#ff6b6b" for n in nets]

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=months, y=nets,
        mode="lines+markers",
        line=dict(color="#6C5CE7", width=3, shape="spline"),
        marker=dict(size=9, color=colors, line=dict(color="rgba(15,15,26,1)", width=2)),
        fill="tozeroy",
        fillcolor="rgba(108,92,231,0.08)",
        name="Dòng tiền ròng",
    ))
    fig.add_hline(y=0, line_dash="dash", line_color="rgba(160,160,184,0.3)", line_width=1)
    return _apply_dark(fig, height=300, yaxis_tickformat=",")


def budget_gauge(spent: float, budget: float, label: str = "") -> go.Figure:
    """Gauge chart cho tiến độ ngân sách."""
    pct = (spent / budget * 100) if budget > 0 else 0

    if pct >= 100:
        bar_color = "#ff6b6b"
    elif pct >= 80:
        bar_color = "#fdcb6e"
    else:
        bar_color = "#00cec9"

    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=pct,
        number={"suffix": "%", "font": {"color": "#E8E8F0", "size": 28}},
        delta={"reference": 100, "decreasing": {"color": "#00cec9"}, "increasing": {"color": "#ff6b6b"}},
        gauge={
            "axis": {"range": [0, 120], "tickcolor": "#6c6c8a"},
            "bar": {"color": bar_color, "thickness": 0.7},
            "bgcolor": "rgba(26,26,46,0.8)",
            "borderwidth": 0,
            "steps": [
                {"range": [0, 70], "color": "rgba(0,206,201,0.08)"},
                {"range": [70, 90], "color": "rgba(253,203,110,0.08)"},
                {"range": [90, 120], "color": "rgba(255,107,107,0.08)"},
            ],
            "threshold": {"line": {"color": "#ff6b6b", "width": 2}, "thickness": 0.75, "value": 100},
        },
        title={"text": label, "font": {"color": "#a0a0b8", "size": 13}},
    ))
    return _apply_dark(fig, height=250, margin=dict(l=20, r=20, t=50, b=10))


def goal_progress_bar(goals_data: List[dict]) -> go.Figure:
    """Biểu đồ ngang tiến độ mục tiêu."""
    names = [d["goal"].name for d in goals_data]
    percentages = [min(100, d["percentage"]) for d in goals_data]
    colors = ["#00cec9" if p >= 100 else "#6C5CE7" if p >= 50 else "#fdcb6e" for p in percentages]

    fig = go.Figure(go.Bar(
        x=percentages,
        y=names,
        orientation="h",
        marker_color=colors,
        marker_line=dict(width=0),
        text=[f"{p:.0f}%" for p in percentages],
        textposition="auto",
        textfont=dict(color="#E8E8F0", size=11),
    ))
    fig.add_vline(x=100, line_dash="dash", line_color="#ff6b6b", opacity=0.4)
    return _apply_dark(fig,
        height=max(200, len(names) * 50),
        xaxis_title="Tiến độ (%)",
    )


def daily_expense_bar(daily_data: List[dict]) -> go.Figure:
    """Biểu đồ chi tiêu hàng ngày."""
    dates = [d["date"] for d in daily_data]
    totals = [d["total"] for d in daily_data]

    fig = go.Figure(go.Bar(
        x=dates, y=totals,
        marker_color="#ff6b6b",
        marker_line=dict(width=0),
        opacity=0.85,
    ))
    if totals:
        avg = sum(totals) / len(totals)
        fig.add_hline(y=avg, line_dash="dash", line_color="#6C5CE7",
                      annotation_text=f"TB: {avg/1e6:.1f}M",
                      annotation_font=dict(color="#a29bfe"))
    return _apply_dark(fig, height=300, yaxis_tickformat=",")


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
        hole=0.6,
        marker=dict(
            colors=DARK_CHART_COLORS[:len(labels)],
            line=dict(color="rgba(15,15,26,0.8)", width=2),
        ),
        textinfo="label+percent",
        textposition="inside",
        textfont=dict(color="#E8E8F0", size=10),
    )])
    return _apply_dark(fig,
        height=350,
        showlegend=True,
        legend=dict(orientation="h", yanchor="top", y=-0.05),
    )


def stock_portfolio_chart(holdings: List[dict]) -> go.Figure:
    """Biểu đồ donut danh mục chứng khoán."""
    labels = [h["ticker"] for h in holdings]
    values = [h["market_value"] for h in holdings]

    fig = go.Figure(data=[go.Pie(
        labels=labels,
        values=values,
        hole=0.6,
        marker=dict(
            colors=DARK_CHART_COLORS[:len(labels)],
            line=dict(color="rgba(15,15,26,0.8)", width=2),
        ),
        textinfo="label+percent",
        textposition="inside",
        textfont=dict(color="#E8E8F0", size=11),
    )])
    return _apply_dark(fig, height=350, showlegend=True,
        legend=dict(orientation="h", yanchor="top", y=-0.05))


def stock_profit_bar(holdings: List[dict]) -> go.Figure:
    """Biểu đồ lãi/lỗ từng mã."""
    tickers = [h["ticker"] for h in holdings]
    profits = [h["profit"] for h in holdings]
    colors = ["#00cec9" if p >= 0 else "#ff6b6b" for p in profits]

    fig = go.Figure(go.Bar(
        x=tickers, y=profits,
        marker_color=colors,
        marker_line=dict(width=0),
        text=[f"{p/1e6:+.1f}M" for p in profits],
        textposition="outside",
        textfont=dict(size=10),
    ))
    fig.add_hline(y=0, line_color="rgba(160,160,184,0.3)", line_width=1)
    return _apply_dark(fig, height=300, yaxis_tickformat=",")

"""Dashboard page - Trang tổng quan."""

import streamlit as st
from datetime import datetime

from services.report_service import ReportService
from services.account_service import AccountService
from services.savings_service import SavingsService
from services.budget_service import BudgetService
from services.goal_service import GoalService
from services.stock_service import StockService
from services.gold_service import GoldService
from services.fx_service import FxService
from ui.components import metric_card, section_header, empty_state, page_title, stock_card
from ui.charts import (
    income_expense_bar, expense_pie, cashflow_line,
    account_balance_donut, stock_portfolio_chart, stock_profit_bar,
)
from utils.formatters import format_currency, short_amount
from utils.helpers import get_current_month_range


def render_dashboard():
    """Render trang tổng quan."""
    user_id = st.session_state["user_id"]
    now = datetime.now()
    start, end = get_current_month_range()

    page_title("Tổng quan", "📊", f"Tháng {now.month}/{now.year}")

    # ===== CHECK IF NEW USER =====
    accounts_list = AccountService.get_accounts(user_id)
    is_new_user = len(accounts_list) == 0

    if is_new_user:
        _render_getting_started(user_id)
        return

    # ===== QUICK ACTIONS =====
    _render_quick_actions()

    st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)

    # ===== METRIC CARDS =====
    summary = ReportService.get_income_expense_summary(user_id, start, end)
    accounts = ReportService.get_account_balances(user_id)

    # --- Tổng tài sản: VND accounts + ngoại tệ quy đổi + vàng + chứng khoán ---
    total_vnd_accounts = sum(a["balance"] for a in accounts if a["currency"] == "VND")

    # Ngoại tệ quy đổi VND
    total_fx_vnd = 0.0
    for a in accounts:
        if a["currency"] != "VND" and a["balance"] > 0:
            converted = FxService.convert_to_vnd(a["balance"], a["currency"])
            total_fx_vnd += converted if converted else 0.0

    # Vàng quy đổi VND
    total_gold_vnd = GoldService.get_total_gold_value(user_id)

    # Chứng khoán (giá trị thị trường)
    stock_info = StockService.get_total_portfolio_value(user_id)
    total_stock_vnd = stock_info.get("total_market_value", 0)

    total_balance = total_vnd_accounts + total_fx_vnd + total_gold_vnd + total_stock_vnd

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        metric_card("Thu nhập", short_amount(summary["income"]),
                     delta=f"+{short_amount(summary['income'])} tháng này", card_type="income")
    with c2:
        metric_card("Chi tiêu", short_amount(summary["expense"]),
                     delta=f"-{short_amount(summary['expense'])} tháng này", card_type="expense")
    with c3:
        net_pct = f"{summary['net']/max(summary['income'],1)*100:.0f}% thu nhập"
        metric_card("Tiết kiệm ròng", short_amount(summary["net"]),
                     delta=net_pct, card_type="balance")
    with c4:
        metric_card("Tổng tài sản", short_amount(total_balance), card_type="savings")

    st.markdown("<div style='height:1.5rem'></div>", unsafe_allow_html=True)

    # ===== BIỂU ĐỒ =====
    col_left, col_right = st.columns(2)

    with col_left:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        section_header("Xu hướng thu chi", "📈")
        trend = ReportService.get_monthly_trend(user_id, 6)
        if trend:
            st.plotly_chart(income_expense_bar(trend), use_container_width=True, config={"displayModeBar": False})
        else:
            empty_state("Chưa có dữ liệu giao dịch", "📊")
        st.markdown('</div>', unsafe_allow_html=True)

    with col_right:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        section_header("Chi tiêu theo danh mục", "🍕")
        cat_data = ReportService.get_expense_by_category(user_id, start, end)
        if cat_data:
            st.plotly_chart(expense_pie(cat_data), use_container_width=True, config={"displayModeBar": False})
        else:
            empty_state("Chưa có chi tiêu tháng này", "🍕")
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)

    # ===== DÒNG TIỀN & TÀI SẢN =====
    col_a, col_b = st.columns(2)

    with col_a:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        section_header("Dòng tiền ròng", "💹")
        if trend:
            st.plotly_chart(cashflow_line(trend), use_container_width=True, config={"displayModeBar": False})
        else:
            empty_state("Chưa có dữ liệu", "💹")
        st.markdown('</div>', unsafe_allow_html=True)

    with col_b:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        section_header("Phân bổ tài sản", "🏦")
        if accounts:
            st.plotly_chart(account_balance_donut(accounts), use_container_width=True, config={"displayModeBar": False})
        else:
            empty_state("Chưa có tài khoản", "🏦")
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)

    # ===== NGÂN SÁCH & MỤC TIÊU =====
    col_x, col_y = st.columns(2)

    with col_x:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        section_header("Ngân sách tháng này", "📋")
        budgets = BudgetService.get_budgets(user_id, now.month, now.year)
        if budgets:
            for b in budgets[:5]:
                label = b["budget"].category.name if b["budget"].category_id else "Tổng chi tiêu"
                pct = b["percentage"]
                if pct < 70:
                    color, bar_color = "🟢", "#00cec9"
                elif pct < 90:
                    color, bar_color = "🟡", "#fdcb6e"
                else:
                    color, bar_color = "🔴", "#ff6b6b"
                st.markdown(
                    f"""<div style="margin-bottom:0.6rem;">
                        <div style="display:flex; justify-content:space-between; margin-bottom:0.25rem;">
                            <span style="color:#E8E8F0; font-size:0.9rem;">{color} {label}</span>
                            <span style="color:#a0a0b8; font-size:0.85rem;">{pct}%</span>
                        </div>
                        <div style="background:rgba(108,92,231,0.1); border-radius:6px; height:8px; overflow:hidden;">
                            <div style="width:{min(pct,100)}%; height:100%; background:{bar_color}; border-radius:6px;"></div>
                        </div>
                        <div style="color:#6c6c8a; font-size:0.75rem; margin-top:2px;">
                            {format_currency(b['spent'])} / {format_currency(b['budget'].amount)}
                        </div>
                    </div>""",
                    unsafe_allow_html=True,
                )
        else:
            empty_state("Chưa thiết lập ngân sách", "📋")
        st.markdown('</div>', unsafe_allow_html=True)

    with col_y:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        section_header("Mục tiêu tiết kiệm", "🎯")
        goals = GoalService.get_goals(user_id, "active")
        if goals:
            for g in goals[:5]:
                pct = g["percentage"]
                icon = "✅" if pct >= 100 else "🔵"
                bar_col = "#00cec9" if pct >= 100 else "#6C5CE7"
                st.markdown(
                    f"""<div style="margin-bottom:0.6rem;">
                        <div style="display:flex; justify-content:space-between; margin-bottom:0.25rem;">
                            <span style="color:#E8E8F0; font-size:0.9rem;">{icon} {g['goal'].name}</span>
                            <span style="color:#a0a0b8; font-size:0.85rem;">{pct}%</span>
                        </div>
                        <div style="background:rgba(108,92,231,0.1); border-radius:6px; height:8px; overflow:hidden;">
                            <div style="width:{min(pct,100)}%; height:100%; background:{bar_col}; border-radius:6px;"></div>
                        </div>
                        <div style="color:#6c6c8a; font-size:0.75rem; margin-top:2px;">
                            {format_currency(g['goal'].current_amount)} / {format_currency(g['goal'].target_amount)}
                        </div>
                    </div>""",
                    unsafe_allow_html=True,
                )
        else:
            empty_state("Chưa có mục tiêu", "🎯")
        st.markdown('</div>', unsafe_allow_html=True)

    # ===== CHỨNG KHOÁN NHANH =====
    st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)
    portfolio = StockService.get_portfolio_summary(user_id)
    if portfolio:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        section_header("Danh mục chứng khoán", "📈")
        cols = st.columns(min(len(portfolio), 4))
        for idx, s in enumerate(portfolio[:4]):
            with cols[idx]:
                stock_card(
                    ticker=s["ticker"],
                    name=s["name"],
                    price=s["current_price"],
                    change_pct=s["profit_pct"],
                    quantity=s["total_qty"],
                    avg_price=s["avg_price"],
                )
        st.markdown('</div>', unsafe_allow_html=True)


def _render_getting_started(user_id):
    """Hướng dẫn bắt đầu cho người dùng mới."""
    from services.category_service import CategoryService

    cat_service = CategoryService()
    categories = cat_service.get_categories(user_id)
    has_categories = len(categories) > 0 if categories else False

    st.markdown(
        """
        <div class="getting-started">
            <h3>🚀 Chào mừng bạn đến với Quản lý Tài chính!</h3>
            <p style="color:#a0a0b8; font-size:0.9rem; margin-bottom:1rem;">
                Hoàn thành các bước sau để bắt đầu quản lý tài chính hiệu quả:
            </p>
        """,
        unsafe_allow_html=True,
    )

    # Step 1: Tạo tài khoản
    st.markdown(
        """
        <div class="gs-step">
            <div class="gs-num">1</div>
            <div class="gs-text">
                <strong>Tạo tài khoản</strong> — Thêm ví tiền, tài khoản ngân hàng, thẻ tín dụng...
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    if st.button("➕ Tạo tài khoản đầu tiên", key="gs_accounts", use_container_width=True):
        st.session_state["current_page"] = "accounts"
        st.rerun()

    # Step 2: Danh mục
    done_class = " done" if has_categories else ""
    st.markdown(
        f"""
        <div class="gs-step">
            <div class="gs-num{done_class}">2</div>
            <div class="gs-text">
                <strong>Thiết lập danh mục</strong> — Tạo nhóm thu nhập & chi tiêu
                {"✅ Đã có danh mục mặc định" if has_categories else ""}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    if not has_categories:
        if st.button("📂 Tạo danh mục", key="gs_categories", use_container_width=True):
            st.session_state["current_page"] = "categories"
            st.rerun()

    # Step 3: Giao dịch
    st.markdown(
        """
        <div class="gs-step">
            <div class="gs-num">3</div>
            <div class="gs-text">
                <strong>Ghi chép giao dịch</strong> — Nhập thu nhập và chi tiêu hằng ngày
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Step 4: Ngân sách
    st.markdown(
        """
        <div class="gs-step">
            <div class="gs-num">4</div>
            <div class="gs-text">
                <strong>Lập ngân sách & Đặt mục tiêu</strong> — Kiểm soát chi tiêu hiệu quả
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("</div>", unsafe_allow_html=True)

    # Quick action cards for new users
    st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(
            """<div class="quick-action">
                <div class="qa-icon">🏦</div>
                <div class="qa-title">Tài khoản</div>
                <div class="qa-desc">Thêm ví, ngân hàng</div>
            </div>""",
            unsafe_allow_html=True,
        )
        if st.button("Tạo tài khoản", key="qa_new_acc", use_container_width=True):
            st.session_state["current_page"] = "accounts"
            st.rerun()
    with c2:
        st.markdown(
            """<div class="quick-action">
                <div class="qa-icon">📂</div>
                <div class="qa-title">Danh mục</div>
                <div class="qa-desc">Phân loại thu chi</div>
            </div>""",
            unsafe_allow_html=True,
        )
        if st.button("Xem danh mục", key="qa_new_cat", use_container_width=True):
            st.session_state["current_page"] = "categories"
            st.rerun()
    with c3:
        st.markdown(
            """<div class="quick-action">
                <div class="qa-icon">⚙️</div>
                <div class="qa-title">Cài đặt</div>
                <div class="qa-desc">Tuỳ chỉnh ứng dụng</div>
            </div>""",
            unsafe_allow_html=True,
        )
        if st.button("Mở cài đặt", key="qa_new_set", use_container_width=True):
            st.session_state["current_page"] = "settings"
            st.rerun()


def _render_quick_actions():
    """Thanh hành động nhanh trên dashboard cho người dùng đã có dữ liệu."""
    st.markdown(
        "<div style='color:#6c6c8a; font-size:0.72rem; font-weight:600; "
        "letter-spacing:1px; text-transform:uppercase; margin-bottom:0.4rem;'>Hành động nhanh</div>",
        unsafe_allow_html=True,
    )
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        if st.button("💳 Thêm giao dịch", key="qa_txn", use_container_width=True):
            st.session_state["current_page"] = "transactions"
            st.rerun()
    with c2:
        if st.button("🏦 Thêm tài khoản", key="qa_acc", use_container_width=True):
            st.session_state["current_page"] = "accounts"
            st.rerun()
    with c3:
        if st.button("📋 Lập ngân sách", key="qa_bud", use_container_width=True):
            st.session_state["current_page"] = "budgets"
            st.rerun()
    with c4:
        if st.button("📉 Xem báo cáo", key="qa_rep", use_container_width=True):
            st.session_state["current_page"] = "reports"
            st.rerun()

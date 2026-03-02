# UI Audit Report — Quản lý Tài chính Cá nhân

**Date:** 2026-03-02  
**Scope:** All 13 page files + `ui/charts.py` + utility files  
**Design System:** Dark Glassmorphism (custom CSS + components in `ui/components.py`)

---

## Executive Summary

| Metric | Count |
|---|---|
| Pages audited | 13 + charts.py |
| CRITICAL issues | 0 |
| HIGH issues | 18 |
| MEDIUM issues | 20 |
| LOW issues | 11 |
| Pages fully using design system | **2 of 13** (dashboard.py, stocks.py) |
| Pages with raw `st.metric()` calls | 3 |
| Pages missing `page_title()` | 11 of 13 |
| Imported-but-unused components | 5 instances |

The app has an excellent design system (`ui/components.py` + `ui/styles.py`) with glassmorphism cards, themed progress bars, status badges, and custom metric cards. However, **only 2 pages (dashboard, stocks) consistently use it**. The remaining 11 pages fall back to raw Streamlit widgets (`st.write`, `st.metric`, `st.markdown("## ...")`) which render with default styling and visually clash with the dark glassmorphism theme.

---

## Design System Components Available

| Component | Purpose | Used By |
|---|---|---|
| `page_title()` | Gradient-styled page header | dashboard, stocks |
| `metric_card()` | Glassmorphism metric display | dashboard, stocks |
| `account_card()` | Account display card | **imported in accounts.py but NEVER used** |
| `transaction_item()` | Transaction list item | **imported in transactions.py but NEVER used** |
| `stock_card()` | Stock holding card | dashboard, stocks |
| `progress_bar()` | Themed progress bar | budgets, goals |
| `status_badge()` | Status label (active/completed/etc) | **imported in savings, goals but NEVER used** |
| `empty_state()` | Empty data placeholder | all pages ✅ |
| `section_header()` | Section divider | most pages ✅ |
| `confirm_dialog()` | Confirm checkbox | **never used anywhere** |

---

## Per-Page Findings

---

### 1. `pages/dashboard.py`

**Overall:** ✅ Best-in-class — fully uses the design system.

| Severity | Line(s) | Issue |
|---|---|---|
| MEDIUM | 108–145 | Budget/Goal sections use **inline HTML progress bars** instead of the `progress_bar()` component. Duplicates logic and won't auto-update if `progress_bar()` styling changes. |
| LOW | — | No error handling if `ReportService` / `StockService` calls throw exceptions (would crash the page). |

**Positive:**
- Uses `page_title()`, `metric_card()`, `section_header()`, `empty_state()`, `stock_card()`
- Wraps chart sections in `<div class="glass-card">` for consistent theme
- Uses `format_currency()`, `short_amount()` from formatters
- Responsive 4-column + 2-column layouts via `st.columns`
- All charts use the dark theme from `ui/charts.py`

---

### 2. `pages/accounts.py`

**Overall:** ❌ Largely bypasses the design system.

| Severity | Line(s) | Issue |
|---|---|---|
| HIGH | 6 | `account_card` is **imported but never used**. The list renders `st.expander` + `st.write` instead, which uses Streamlit's default white/gray styling and clashes with the dark theme. |
| HIGH | 15 | `st.markdown("## 🏦 Tài khoản")` — raw Markdown header instead of `page_title("Tài khoản", "🏦")`. Missing the gradient text effect. |
| MEDIUM | 23 | `st.info(f"💰 Tổng số dư (VND): ...")` — default Streamlit info box. Should use `metric_card()` for visual consistency. |
| MEDIUM | 26–32 | Account detail content uses bare `st.write()` calls which render as plain unstyled text. |
| LOW | — | No `glass-card` wrapper around any content section. |

---

### 3. `pages/transactions.py`

**Overall:** ❌ Extensively bypasses the design system.

| Severity | Line(s) | Issue |
|---|---|---|
| HIGH | 8 | `transaction_item` is **imported but never used**. Transactions are shown as `st.expander` + `st.write` instead of the themed transaction list items with colored amounts. |
| HIGH | 18 | `st.markdown("## 💳 Giao dịch")` — should be `page_title("Giao dịch", "💳")`. |
| HIGH | 56–58 | `c1.metric("Thu", ...)`, `c2.metric("Chi", ...)`, `c3.metric("Ròng", ...)` — **plain `st.metric()`** renders with Streamlit's default white-background card, severely clashing with the dark glassmorphism theme. Should use `metric_card()`. |
| MEDIUM | 75–78 | Inside `st.expander`, transaction details use raw `st.write()` — unstyled plain text. |
| MEDIUM | 61–66 | Direct `from db.database import get_session` + raw SQLAlchemy queries inside the page render function. Architecture concern — should go through a service layer. |
| LOW | 59 | `st.markdown("---")` — raw divider. Consistent with theme CSS `hr` styling, but a `section_header()` would be better. |

---

### 4. `pages/categories.py`

**Overall:** ⚠️ Partially themed.

| Severity | Line(s) | Issue |
|---|---|---|
| HIGH | 13 | `st.markdown("## 📂 Danh mục")` — should use `page_title("Danh mục", "📂")`. |
| MEDIUM | 22, 24 | `st.write("**Loại:** ...")`, `st.write("**Icon:** ...")` — raw text bypasses theme. |
| MEDIUM | 30, 32 | Subcategory items use raw `st.write("  • {sub.name}")` — no themed styling. |
| MEDIUM | 38 | `st.info("Chưa có danh mục con")` — should be `empty_state()` for consistency. |
| LOW | — | No `glass-card` wrapper around category content. |

**Positive:**
- Uses `empty_state()` for empty category list
- Uses `st.tabs`, `st.form` properly
- Proper `st.success`/`st.error` messages

---

### 5. `pages/stocks.py`

**Overall:** ✅ Excellent — second-best page, fully uses the design system.

| Severity | Line(s) | Issue |
|---|---|---|
| LOW | 80 | `cols = st.columns(min(len(portfolio), 3))` then `cols[idx % len(cols)]` — if portfolio has >3 items, cards will stack but without any spacing between rows. |
| LOW | — | The `st.dataframe` inside a `glass-card` is fine, but table cell styling is Streamlit's default (cannot be changed). |

**Positive:**
- Uses `page_title()`, `metric_card()`, `section_header()`, `empty_state()`, `stock_card()`
- All chart sections wrapped in `<div class="glass-card">`
- Uses `format_currency()`, `short_amount()`
- Responsive layouts with `st.columns`
- Forms properly styled with `st.form`

---

### 6. `pages/savings.py`

**Overall:** ❌ Significantly under-themed.

| Severity | Line(s) | Issue |
|---|---|---|
| HIGH | 15 | `st.markdown("## 🏧 Sổ tiết kiệm")` — should use `page_title("Sổ tiết kiệm", "🏧")`. |
| HIGH | 7 | `status_badge` and `progress_bar` are **imported but never used**. Deposit status is shown as plain text (`DEPOSIT_STATUS_LABELS.get(d.status, d.status)`) and there's no visual progress indicator for deposit term. |
| MEDIUM | 39 | `st.info(f"💰 Tổng tiền gửi ...")` — should use `metric_card()`. |
| MEDIUM | 55–63 | All deposit details use bare `st.write()` — 9 consecutive plain-text lines. |
| LOW | — | No maturity progress bar (e.g., 3/12 months elapsed). `progress_bar()` is imported specifically for this but unused. |

---

### 7. `pages/forex.py`

**Overall:** ⚠️ Acceptably themed with minor gaps.

| Severity | Line(s) | Issue |
|---|---|---|
| HIGH | 16 | `st.markdown("## 💱 Tỷ giá ngoại tệ")` — should use `page_title("Tỷ giá ngoại tệ", "💱")`. |
| LOW | — | Converter result shown via `st.success()` — functional but could use a styled result card. |
| LOW | — | No `glass-card` wrapper around the data table or converter section. |

**Positive:**
- Uses `section_header()`, `empty_state()` correctly
- Uses `format_currency()`, `format_number()` from formatters
- `st.dataframe` for rates table is appropriate
- Sync button with spinner feedback

---

### 8. `pages/gold.py`

**Overall:** ❌ Significant theme bypass.

| Severity | Line(s) | Issue |
|---|---|---|
| HIGH | 15 | `st.markdown("## 🥇 Vàng")` — should use `page_title("Vàng", "🥇")`. |
| HIGH | 80–82 | `c1.metric("Giá trị thị trường", ...)`, `c2.metric("Giá vốn", ...)`, `c3.metric("Lãi/Lỗ", ...)` — **plain `st.metric()`** with Streamlit's default styling. Clashes with dark theme. Should use `metric_card()`. |
| MEDIUM | 93–99 | Gold holding details use bare `st.write()` — 7 consecutive plain-text lines inside expanders. |
| MEDIUM | 88 | `st.markdown("---")` divider between metrics and list — fine but should use spacing `div`. |
| LOW | 8 | `format_weight` is imported but never used in the display. Gold quantities show raw numbers instead of formatted weights. |

---

### 9. `pages/budgets.py`

**Overall:** ⚠️ Partially themed.

| Severity | Line(s) | Issue |
|---|---|---|
| HIGH | 16 | `st.markdown("## 📋 Ngân sách")` — should use `page_title("Ngân sách", "📋")`. |
| MEDIUM | 10 | `budget_gauge` is **imported from `ui.charts` but never used**. The gauge chart was designed specifically for budget visualization. |
| MEDIUM | 43–49 | Direct `from db.database import get_session` and raw `session.query(Category)` inside the render function. Should use the service layer. |
| MEDIUM | 75 | `st.write(f"• {label}: {format_currency(budget_obj.amount)}")` — plain text for budget list items. |
| LOW | — | No `glass-card` wrapper around budget tracking content. |

**Positive:**
- Uses `progress_bar()` for budget tracking ✅
- Uses `section_header()`, `empty_state()` correctly
- Uses `format_currency()` from formatters

---

### 10. `pages/goals.py`

**Overall:** ⚠️ Partially themed.

| Severity | Line(s) | Issue |
|---|---|---|
| HIGH | 16 | `st.markdown("## 🎯 Mục tiêu tài chính")` — should use `page_title("Mục tiêu tài chính", "🎯")`. |
| MEDIUM | 7 | `status_badge` is **imported but never used**. Goal status is displayed as emoji text icons instead. |
| MEDIUM | 53–56 | Goal details use bare `st.write()` calls — plain unstyled text. |
| MEDIUM | 60–67 | Conditional logic for deadline display uses `st.write()`, `st.warning()`, and `st.error()` inline — inconsistent presentation. |
| LOW | — | No `glass-card` wrapper around goal details. |

**Positive:**
- Uses `progress_bar()` ✅ for individual goal progress
- Uses `goal_progress_bar()` chart for overview ✅
- Uses `empty_state()` correctly
- Uses `format_currency()` from formatters
- Rich interaction: contribute, edit, cancel with popovers

---

### 11. `pages/reports.py`

**Overall:** ❌ Significant theme bypass.

| Severity | Line(s) | Issue |
|---|---|---|
| HIGH | 17 | `st.markdown("## 📈 Báo cáo tài chính")` — should use `page_title("Báo cáo tài chính", "📈")`. |
| HIGH | 47–49 | `c1.metric("💚 Thu nhập", ...)`, `c2.metric("❤️ Chi tiêu", ...)`, `c3.metric("💙 Ròng", ...)` — **plain `st.metric()`** with emoji prefix in label. Renders with default white background, severely clashes with dark theme. Should use `metric_card("Thu nhập", ..., card_type="income")`. |
| MEDIUM | 56 | `st.write(f"• **{item['category']}**: ...")` — category breakdown as plain text. Could use themed list items. |
| MEDIUM | 58 | `st.info("Chưa có dữ liệu chi tiêu")` — should use `empty_state()` for consistency. |
| MEDIUM | 74 | Account balances displayed as `st.write(f"• **{a['name']}** ...")` — plain text. |
| MEDIUM | 78–93 | Charts in the "Biểu đồ" tab lack `glass-card` wrappers (unlike same charts in dashboard.py). Same charts look different between pages. |
| LOW | — | Export tab download buttons are functionally correct but lack visual polish. |

---

### 12. `pages/settings_page.py`

**Overall:** ⚠️ Acceptable with some gaps.

| Severity | Line(s) | Issue |
|---|---|---|
| HIGH | 16 | `st.markdown("## ⚙️ Cài đặt")` — should use `page_title("Cài đặt", "⚙️")`. |
| MEDIUM | 106 | `st.write(f"📁 {b['name']} ({b['size_mb']} MB)")` — backup list items use plain text. |
| MEDIUM | 113 | `st.write(b["date"].strftime(...))` — date display as plain text. |
| LOW | 127–133 | Provider status uses `st.success/st.warning/st.info` for token status — functional but could use `status_badge()`. |
| LOW | 138–143 | FxService sync result uses ternary `st.success(msg) if ok else st.warning(msg)`. The `ok` variable here is actually a result object, could cause type confusion. |

**Positive:**
- Uses `section_header()`, `empty_state()` correctly
- Forms properly structured with `st.form`
- Uses `st.tabs` with clear organization
- Download button for database backup

---

### 13. `pages/login.py`

**Overall:** ✅ Good — custom themed independently.

| Severity | Line(s) | Issue |
|---|---|---|
| LOW | — | No `glass-card` wrapper around the login form area. The form tabs and inputs float on the dark background without a glass container. |
| LOW | 84–88 | Default credentials hint displayed at bottom — security concern in production. |

**Positive:**
- Custom gradient title matching the app's branding
- Centered layout with `st.columns([1, 2, 1])`
- Forms with proper validation and error messages
- Registration form with password confirmation
- Uses inline CSS matching the theme's color variables

---

### 14. `ui/charts.py`

**Overall:** ✅ Excellent — fully themed.

| Severity | Line(s) | Issue |
|---|---|---|
| LOW | — | No issues. All charts consistently use `_apply_dark()` with transparent backgrounds, the Inter font, and matching color palette. |

**Positive:**
- Centralized `_DARK_LAYOUT` dict ensures consistency
- `_apply_dark()` helper applies consistent theming
- Color palette matches CSS variables from `ui/styles.py`
- Transparent backgrounds allow charts to sit properly inside glass-card containers
- All formatters use Vietnamese-friendly number formatting (M, B suffixes)

---

## Cross-Cutting Issues

### 1. `page_title()` — Inconsistent Page Headers (HIGH)

11 of 13 pages use raw `st.markdown("## 🔹 Title")` instead of `page_title()`. This means those pages show a plain Streamlit H2 heading (default white text) instead of the gradient-styled header that dashboard and stocks use.

**Affected:** accounts, transactions, categories, savings, forex, gold, budgets, goals, reports, settings_page (login has its own custom header)

### 2. Raw `st.metric()` — Theme Clash (HIGH)

3 pages use Streamlit's built-in `st.metric()` which renders with a default white/light background card that **severely clashes** with the dark glassmorphism theme:

| Page | Line(s) |
|---|---|
| transactions.py | 56–58 |
| gold.py | 80–82 |
| reports.py | 47–49 |

Dashboard.py correctly uses `metric_card()` instead.

### 3. Imported-but-Unused Components (HIGH)

5 instances of importing custom components but falling back to plain Streamlit:

| Page | Component | What's Used Instead |
|---|---|---|
| accounts.py | `account_card` | `st.expander` + `st.write` |
| transactions.py | `transaction_item` | `st.expander` + `st.write` |
| savings.py | `status_badge`, `progress_bar` | Plain text labels |
| goals.py | `status_badge` | Emoji text |
| budgets.py | `budget_gauge` (chart) | `progress_bar` only |
| components.py | `confirm_dialog` | Never used anywhere |

### 4. Missing `glass-card` Wrappers (MEDIUM)

Dashboard and stocks consistently wrap content in `<div class="glass-card">` for the themed container effect. Other pages display their content directly — charts, tables, and forms float without the glass container.

**Affected:** accounts, transactions, categories, savings, forex, gold, budgets, goals, reports, settings

### 5. Raw `st.write()` for Detail Views (MEDIUM)

Most detail views inside `st.expander` use bare `st.write(f"**Label:** value")` which renders as plain unstyled text. This creates a visual disconnect — the outer shell (tabs, expanders) looks acceptable, but inner content looks like a prototype.

**Affected pages:** accounts, transactions, categories, savings, gold, goals, reports, settings

### 6. Direct DB Queries in Page Layer (MEDIUM, Architecture)

Two page files bypass the service layer and query the database directly:

| Page | Lines | Query |
|---|---|---|
| transactions.py | 61–66 | `session.query(SubCategory)`, `session.query(Account)` |
| budgets.py | 43–49 | `session.query(Category)` |

This violates the app's otherwise clean service-layer architecture.

---

## Utility Files Assessment

### `utils/formatters.py` — ✅ Well-implemented

- `format_currency()`: Correct VND formatting (dots as thousands separator, ₫ symbol) and foreign currency formatting (commas, 2 decimals)
- `format_number()`: Vietnamese number formatting
- `format_date()`: Supports dd/mm/yyyy and yyyy-mm-dd
- `format_percentage()`: Simple percentage formatter
- `format_weight()`: Gold weight (chỉ/lượng) — imported in gold.py but **never used**
- `short_amount()`: Compact display (K/M/B) — correctly used in dashboard/stocks
- Label dictionaries (`ACCOUNT_TYPE_LABELS`, etc.) — properly used across the app

### `utils/constants.py` — ✅ Well-organized

- All constants are properly defined and used across service/page layers
- `CHART_COLORS` defined but superseded by `DARK_CHART_COLORS` in `ui/charts.py` (unused import in charts.py line 4 — minor)

---

## Recommendations Summary (Priority Order)

### Quick Wins (1–2 hours)

1. **Replace all `st.markdown("## ...")` with `page_title()`** across 11 pages — instant visual consistency
2. **Replace all `st.metric()` with `metric_card()`** in transactions.py, gold.py, reports.py — fixes the most jarring theme clash
3. **Remove unused imports** — `account_card`, `transaction_item`, `status_badge`, `confirm_dialog`, unused `budget_gauge`

### Medium Effort (3–5 hours)

4. **Use `account_card()` in accounts.py** — render account list with themed cards
5. **Use `transaction_item()` in transactions.py** — render recent transactions with themed items (keep expander for edit/delete actions)
6. **Use `status_badge()` in savings.py and goals.py** — replace plain text status labels
7. **Add `glass-card` wrappers** to chart and table sections in reports.py, and content sections across other pages
8. **Use `progress_bar()`** in savings.py for deposit term elapsed progress
9. **Use `budget_gauge()`** in budgets.py for individual budget items

### Larger Refactors (5+ hours)

10. **Replace raw `st.write()` detail views** with themed HTML components or a new `detail_card()` component
11. **Move direct DB queries** out of transactions.py and budgets.py into their respective services
12. **Create a `data_card()` component** for showing key-value pairs in a themed card (would replace 90%+ of `st.write("**Key:** value")` patterns)
13. **Add `glass-card` wrappers** to all forms for consistency with dashboard/stocks

---

## Visual Consistency Score by Page

| Page | Score | Notes |
|---|---|---|
| dashboard.py | ⭐⭐⭐⭐⭐ | Fully themed, reference implementation |
| stocks.py | ⭐⭐⭐⭐⭐ | Fully themed, charts wrapped correctly |
| login.py | ⭐⭐⭐⭐ | Custom themed header, good layout |
| charts.py | ⭐⭐⭐⭐⭐ | Consistent dark theme throughout |
| forex.py | ⭐⭐⭐ | Missing page_title, but otherwise acceptable |
| budgets.py | ⭐⭐⭐ | Uses progress_bar, missing page_title & gauge |
| goals.py | ⭐⭐⭐ | Uses progress_bar & chart, missing badges |
| categories.py | ⭐⭐ | Raw st.write throughout |
| settings_page.py | ⭐⭐ | Functional but not themed |
| savings.py | ⭐⭐ | Imported components unused |
| accounts.py | ⭐⭐ | account_card imported but unused |
| gold.py | ⭐⭐ | Raw st.metric clashes with theme |
| transactions.py | ⭐⭐ | Raw st.metric + unused transaction_item |
| reports.py | ⭐⭐ | Raw st.metric + no glass-card wrappers |

---

*End of UI audit report*

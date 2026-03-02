# 🔍 BÁO CÁO KIỂM TRA TOÀN DIỆN DỰ ÁN "QUẢN LÝ TÀI CHÍNH CÁ NHÂN"

**Ngày kiểm tra:** Tháng 6/2025  
**Phạm vi:** Toàn bộ mã nguồn (87 file Python + cấu hình)  
**Công nghệ:** Streamlit + SQLAlchemy + Pydantic v2 + Plotly  

---

## 📁 I. DANH SÁCH FILE ĐẦY ĐỦ

### Cấu trúc dự án

```
tài chính cá nhân/
├── app.py                          # Entry point Streamlit
├── config.py                       # Cấu hình ứng dụng (Settings)
├── requirements.txt                # Dependencies
├── run.bat                         # Script chạy ứng dụng
├── README.md                       # Tài liệu
├── assets/                         # Tài nguyên tĩnh
│
├── db/                             # Database layer
│   ├── __init__.py
│   ├── database.py                 # Session factory, engine (SQLite/PostgreSQL)
│   ├── init_db.py                  # Tạo bảng ban đầu
│   └── seed.py                     # Dữ liệu mẫu (categories, admin user)
│
├── models/                         # SQLAlchemy ORM models (16 models)
│   ├── __init__.py
│   ├── base.py                     # Base, TimestampMixin, SoftDeleteMixin
│   ├── user.py                     # User
│   ├── account.py                  # Account (cash/bank/ewallet/forex/gold/savings/other)
│   ├── transaction.py              # Transaction (income/expense/transfer/adjustment)
│   ├── category.py                 # Category + SubCategory
│   ├── budget.py                   # Budget (ngân sách tháng)
│   ├── goal.py                     # SavingsGoal (mục tiêu tiết kiệm)
│   ├── savings.py                  # SavingsDeposit + SavingsInterestEvent
│   ├── stock.py                    # StockHolding (chứng khoán)
│   ├── gold.py                     # GoldPrice + GoldHolding
│   ├── fx_rate.py                  # FxRate (tỷ giá ngoại tệ)
│   ├── recurring.py                # RecurringTransaction (giao dịch định kỳ)
│   ├── settings.py                 # UserSetting
│   ├── audit.py                    # AuditLog
│   └── sync_log.py                 # SyncLog
│
├── repositories/                   # Data access layer (14 repos)
│   ├── __init__.py
│   ├── base.py                     # BaseRepository[T] generic CRUD
│   ├── user_repo.py
│   ├── account_repo.py
│   ├── transaction_repo.py
│   ├── category_repo.py
│   ├── budget_repo.py
│   ├── goal_repo.py
│   ├── savings_repo.py
│   ├── stock_repo.py
│   ├── gold_repo.py
│   ├── fx_repo.py
│   ├── settings_repo.py
│   └── audit_repo.py
│
├── services/                       # Business logic (14 services)
│   ├── __init__.py
│   ├── account_service.py
│   ├── transaction_service.py
│   ├── category_service.py
│   ├── budget_service.py
│   ├── goal_service.py
│   ├── savings_service.py
│   ├── stock_service.py
│   ├── gold_service.py
│   ├── fx_service.py
│   ├── report_service.py
│   ├── auth_service.py
│   ├── settings_service.py
│   ├── backup_service.py
│   └── providers/                  # API data providers
│       ├── __init__.py
│       ├── base.py                 # ProviderResult, RateData, GoldData
│       ├── vn_appmob_exchange.py   # Provider chính tỷ giá
│       ├── vn_appmob_gold.py       # Provider chính giá vàng
│       ├── vietcombank_fallback.py # Fallback tỷ giá (XML)
│       ├── manual_provider.py      # Nhập tay tỷ giá/giá vàng
│       ├── cache_service.py        # In-memory cache (TTL)
│       └── token_manager.py        # Token VNAppMob API
│
├── schemas/                        # Pydantic v2 validation
│   ├── __init__.py
│   ├── common.py                   # BaseSchema, PaginationParams
│   ├── account.py                  # AccountCreate, AccountUpdate
│   ├── transaction.py              # TransactionCreate, TransactionUpdate
│   ├── savings.py                  # SavingsDepositCreate, SavingsDepositUpdate
│   └── user.py                     # UserCreate, UserLogin, PasswordChange
│
├── pages/                          # Streamlit UI pages (13 pages)
│   ├── __init__.py
│   ├── login.py
│   ├── dashboard.py
│   ├── accounts.py
│   ├── transactions.py
│   ├── categories.py
│   ├── budgets.py
│   ├── goals.py
│   ├── savings.py
│   ├── stocks.py
│   ├── forex.py
│   ├── gold.py
│   ├── reports.py
│   └── settings_page.py
│
├── ui/                             # UI components
│   ├── __init__.py
│   ├── components.py               # metric_card, account_card, stock_card, etc.
│   ├── charts.py                   # Plotly charts (dark theme)
│   └── styles.py                   # CSS glassmorphism injection
│
└── utils/                          # Utility modules
    ├── __init__.py
    ├── constants.py                # ACCOUNT_TYPES, CURRENCIES, GOLD_TYPES, etc.
    ├── formatters.py               # format_currency, format_number, short_amount
    ├── helpers.py                   # get_month_range, safe_divide, parse_amount_input
    └── validators.py               # validate_amount, validate_username, etc.
```

---

## 🐛 II. BUGS & ERRORS (21 lỗi — có file path + line number)

### 🔴 CRITICAL — Sẽ crash ngay khi chạy tới

| # | File | Line | Mô tả | Nguyên nhân |
|---|------|------|-------|-------------|
| 1 | `services/stock_service.py` | 49, 70, 87 | `AuditRepository(session).log(...)` | Method tên `log_action()`, không có `log()`. Crash `AttributeError` khi add/update/delete holding. |
| 2 | `services/goal_service.py` | 35, 82 | `log_action(..., extra=name)` | `extra` không phải tham số hợp lệ của `log_action()`. Crash `TypeError`. |
| 3 | `services/goal_service.py` | 30 | `SavingsGoal(target_date=target_date)` | Model dùng `deadline`, không có `target_date`. SQLAlchemy im lặng bỏ qua → deadline luôn NULL. |
| 4 | `services/goal_service.py` | 102, 104 | `g.target_date` | Model chỉ có `deadline`. Crash `AttributeError` khi get_goals. |
| 5 | `pages/goals.py` | 77, 83 | `goal.target_date` | Tương tự #4, truy cập field không tồn tại. |
| 6 | `pages/transactions.py` | 127 | `category_map, subcategory_map = cat_service.get_category_map(user_id)` | `get_category_map()` trả về 1 dict, không phải tuple. Crash `ValueError` khi unpack. |
| 7 | `pages/accounts.py` | 33 | `acc.type` | Model Account dùng `account_type`, không có `type`. Crash `AttributeError`. |
| 8 | `pages/accounts.py` | 39, 46 | `acc.notes` | Model Account dùng `description`, không có `notes`. Crash `AttributeError`. |
| 9 | `pages/accounts.py` | 53 | `AccountService.update_account(user_id, acc.id, name=..., balance=..., notes=...)` | Method yêu cầu `data: AccountUpdate` object, không nhận keyword args. Crash `TypeError`. |
| 10 | `pages/accounts.py` | 60 | `AccountService.delete_account(...)` | Method không tồn tại trên AccountService (chỉ có `close_account`). Crash `AttributeError`. |
| 11 | `pages/accounts.py` | 88 | `AccountCreate(type=acc_type, balance=balance)` | Schema dùng `account_type` và `initial_balance`. Pydantic v2 sẽ raise `ValidationError` vì thiếu required field `account_type`. |
| 12 | `services/report_service.py` | ~204 | `a.type` | Model Account dùng `account_type`. Crash `AttributeError` trong `get_account_balances()`. |
| 13 | `pages/forex.py` | 52–54 | `r.buy_cash`, `r.buy_transfer`, `r.sell` | (a) `FxService.get_latest_rates()` trả về **dict** — dùng dot notation sẽ crash. (b) Tên key sai: model/service dùng `buy_rate`, `sell_rate`, `transfer_rate`. **Double bug.** |
| 14 | `pages/forex.py` | 80 | `FxService.convert_to_vnd(currency, amount)` | Thứ tự tham số sai. Service: `convert_to_vnd(amount, currency_code)`. Kết quả sẽ sai nếu không crash. |
| 15 | `pages/gold.py` | 56–60 | `p.gold_type`, `p.buy_price`, etc. | `GoldService.get_latest_prices()` trả về **dict**, dùng dot notation crash `AttributeError`. |
| 16 | `pages/gold.py` | 95–96 | `holding.weight_gram` | GoldHolding model dùng `quantity`, không có `weight_gram`. Crash `AttributeError`. |
| 17 | `pages/gold.py` | 116–117 | `GoldService.add_holding(user_id, gold_type, weight, buy_price, buy_date, notes)` | Thiếu tham số `unit` (tham số thứ 4). Các giá trị positional bị lệch: `buy_price` → `unit`, `buy_date` → `buy_price`, `notes` → `buy_date`. |
| 18 | `pages/dashboard.py` | 119 | `b["budget"].category.name` | Budget model không có relationship đến Category. Crash `AttributeError`. |
| 19 | `pages/categories.py` | 83 | `cat_service.create_subcategory(user_id, cat_id, sub_name)` | Method nhận 2 args `(category_id, name)` nhưng page truyền 3. Crash `TypeError`. |
| 20 | `pages/categories.py` | 47, 55 | `cat_service.delete_subcategory(...)`, `cat_service.delete_category(...)` | Các method này không tồn tại trên `CategoryService`. Crash `AttributeError`. |

### 🟡 LOGIC BUGS — Không crash nhưng cho kết quả sai

| # | File | Line | Mô tả |
|---|------|------|-------|
| 21 | `pages/gold.py` | 91 | `h.get("total_cost", 0)` — dict key là `"cost"` chứ không phải `"total_cost"`. Luôn trả về 0. |

---

## 📊 III. DASHBOARD — TỔNG TÀI SẢN (VND + Ngoại tệ + Vàng + Chứng khoán)

### Trạng thái hiện tại: ❌ KHÔNG ĐÚNG

**File:** `pages/dashboard.py` dòng 32:
```python
total_balance = sum(a["balance"] for a in accounts if a["currency"] == "VND")
```

**Vấn đề:** Chỉ cộng số dư **tài khoản VND**. Hoàn toàn bỏ sót:

| Loại tài sản | Trạng thái | Có service hỗ trợ? |
|---|---|---|
| Tiền VND (cash/bank/ewallet) | ✅ Có cộng | ✓ |
| Ngoại tệ → quy đổi VND | ❌ Bỏ sót | ✓ `FxService.convert_to_vnd()` |
| Vàng → quy đổi VND | ❌ Bỏ sót | ✓ `GoldService.get_total_gold_value()` |
| Chứng khoán → VND | ❌ Bỏ sót | ✓ `StockService.get_total_portfolio_value()` |
| Tiết kiệm → VND | ❌ Bỏ sót | ✓ `SavingsService` (tổng principal) |

### Gợi ý fix:

```python
# 1. Tổng tài khoản (tất cả tiền tệ → VND)
total_account = 0
for a in accounts:
    if a["currency"] == "VND":
        total_account += a["balance"]
    else:
        total_account += FxService.convert_to_vnd(a["balance"], a["currency"])

# 2. Giá trị vàng
total_gold = GoldService.get_total_gold_value(user_id)

# 3. Giá trị chứng khoán
total_stock = StockService.get_total_portfolio_value(user_id)

# 4. Tổng tài sản
total_assets = total_account + total_gold + total_stock
```

---

## 🏦 IV. ACCOUNT SERVICE — KIỂM TRA

### Trạng thái: ✅ Service tốt, ❌ Page gọi sai

**`services/account_service.py`** — Cấu trúc đúng:
- `create_account(user_id, data: AccountCreate)` ✅
- `get_accounts(user_id)` ✅
- `update_account(user_id, account_id, data: AccountUpdate)` ✅
- `close_account(user_id, account_id)` ✅
- `adjust_balance(user_id, account_id, new_balance)` ✅
- `get_total_balance(user_id)` → dict theo currency ✅

**Vấn đề ở `pages/accounts.py`:**
- Gọi `update_account` bằng keyword args thay vì `AccountUpdate` object (Bug #9)
- Gọi `delete_account` không tồn tại thay vì `close_account` (Bug #10)
- Tạo `AccountCreate` sai field names (Bug #11)
- Truy cập `acc.type` thay vì `acc.account_type` (Bug #7)
- Truy cập `acc.notes` thay vì `acc.description` (Bug #8)

---

## 💱 V. TỈ GIÁ NGOẠI TỆ (FX) — REAL-TIME FETCHING

### Kiến trúc Provider Chain: ✅ Thiết kế tốt

```
VNAppMob API (primary)
    ↓ fail
Vietcombank XML (fallback)
    ↓ fail
DB Cache (cached data)
    ↓ fail
Manual Input (user enters rates)
```

**Đánh giá chi tiết:**

| Thành phần | Trạng thái | Ghi chú |
|---|---|---|
| `VNAppMobExchangeProvider` | ✅ Hoạt động | Token auto-refresh, API `vnappmob.vn` |
| `VietcombankXmlFallbackProvider` | ✅ Hoạt động | Parse XML từ Vietcombank |
| `TokenManager` | ✅ Singleton | Quản lý token, tự refresh khi hết hạn |
| `CacheService` | ✅ In-memory TTL | Cache 1800s (30 phút) |
| `FxService.sync_rates()` | ✅ Fallback chain | 4 cấp fallback |
| `FxService.convert_to_vnd()` | ✅ Hoạt động | Dùng sell_rate |
| Auto-sync (app.py) | ✅ Có | Tự sync FX mỗi lần mở app |
| `SyncLog` logging | ✅ Có | Ghi lại lịch sử đồng bộ |

**Vấn đề:**
- ❌ **forex.py page truy cập sai tên field** (Bug #13): `buy_cash`/`buy_transfer`/`sell` thay vì `buy_rate`/`sell_rate`/`transfer_rate`
- ❌ **convert_to_vnd argument order sai** (Bug #14)
- ⚠️ FxRate model chỉ có `buy_rate`, `sell_rate`, `transfer_rate` — thiếu `buy_cash` (mua tiền mặt) vs `buy_transfer` (mua chuyển khoản) distinction nếu cần

---

## 🥇 VI. GIÁ VÀNG — REAL-TIME FETCHING

### Kiến trúc: ✅ Tốt (tương tự FX)

```
VNAppMob Gold API (primary)
    ↓ fail
DB Cache (last known prices)
    ↓ fail
Manual Input
```

**Đánh giá:**

| Thành phần | Trạng thái |
|---|---|
| `VNAppMobGoldProvider` | ✅ Hoạt động |
| `GoldService.sync_prices()` | ✅ Fallback chain 3 cấp |
| `GoldService.get_total_gold_value()` | ✅ Quy đổi VND theo sell_price |
| `GoldService.get_holdings_with_pnl()` | ✅ Tính P&L |
| Auto-sync (app.py) | ✅ Có |

**Vấn đề ở gold.py page:**
- ❌ `get_latest_prices()` trả dict nhưng page dùng dot notation (Bug #15)
- ❌ `holding.weight_gram` — field không tồn tại, phải là `quantity` (Bug #16)
- ❌ `add_holding()` thiếu tham số `unit` (Bug #17)
- ❌ `h.get("total_cost", 0)` — key sai thành `"cost"` (Bug #21)

---

## 📈 VII. CHỨNG KHOÁN (STOCKS) — INTEGRATION CHECK

### Trạng thái: ⚠️ Tích hợp một phần

**Đã có:**
- ✅ `StockHolding` model đầy đủ (ticker, exchange, quantity, avg_price, current_price)
- ✅ `StockHoldingRepository` với portfolio aggregation
- ✅ `StockService` CRUD + `get_portfolio_summary()` + `get_total_portfolio_value()`
- ✅ `pages/stocks.py` — UI hoàn chỉnh: thêm/sửa/xóa cổ phiếu, biểu đồ
- ✅ `ui/components.py` — `stock_card()` component
- ✅ `ui/charts.py` — `stock_portfolio_chart()`, `stock_profit_bar()`
- ✅ Dashboard hiển thị cards chứng khoán (cuối trang)

**Thiếu/Lỗi:**
- ❌ `AuditRepository.log()` sai tên method → crash khi add/update/delete (Bug #1)
- ❌ Dashboard KHÔNG cộng giá trị CK vào tổng tài sản (Bug trong dashboard.py L32)
- ❌ Không có account type "stock" — chỉ có cash/bank/ewallet/forex/gold/savings/other
- ❌ Giá chứng khoán chỉ **nhập tay** (`current_price` manual update), không có API real-time
- ⚠️ Không có kết nối API sàn chứng khoán (SSI, VNDirect, TCBS, etc.)
- ⚠️ Không hỗ trợ lịch sử giá, biến động intraday
- ⚠️ Không có cảnh báo giá (price alerts)

---

## 💳 VIII. GIAO DỊCH MUA TÀI SẢN (CROSS-ASSET TRANSACTIONS)

### Trạng thái: ❌ KHÔNG HỖ TRỢ

**Transaction model** chỉ hỗ trợ 4 loại: `income`, `expense`, `transfer`, `adjustment`.

Không có khả năng ghi nhận:
- Dùng VND mua vàng (trừ account VND → thêm GoldHolding)
- Dùng VND mua chứng khoán (trừ account VND → thêm StockHolding)
- Dùng VND mua ngoại tệ (trừ account VND → cộng account forex)
- Bán vàng/CK → nhận VND (xóa holding → cộng account VND)

**Hiện tại:** Mua vàng/chứng khoán và giao dịch tài khoản là **hoàn toàn tách biệt** — không có link giữa Transaction và GoldHolding/StockHolding. Người dùng phải:
1. Tự tạo giao dịch chi tiêu "Mua vàng" để trừ VND
2. Tự thêm GoldHolding riêng
3. Không có kiểm tra tính nhất quán

### Gợi ý thiết kế:

```python
# Thêm loại giao dịch mới
TRANSACTION_TYPES = ["income", "expense", "transfer", "adjustment", 
                      "buy_asset", "sell_asset"]

# Thêm fields cho Transaction model
asset_type = Column(String(20))      # "gold", "stock", "forex"
asset_holding_id = Column(Integer)   # FK tới GoldHolding/StockHolding
```

Hoặc tạo service `AssetTransactionService` quản lý việc mua/bán:
```python
class AssetTransactionService:
    @staticmethod
    def buy_gold(user_id, account_id, gold_type, quantity, unit, price):
        # 1. Trừ balance tài khoản
        # 2. Tạo GoldHolding
        # 3. Tạo Transaction type="buy_asset"
        # 4. Link transaction ↔ holding
```

---

## 🔧 IX. FIX SUGGESTIONS CHI TIẾT

### Fix #1: stock_service.py — AuditRepository method name
```python
# Sai (3 chỗ):
AuditRepository(session).log(user_id, "stock_holding", holding.id, "create")

# Đúng:
AuditRepository(session).log_action(user_id, "create_stock", "stock_holding", holding.id)
```

### Fix #2: goal_service.py — `extra` param & `target_date`/`deadline`
```python
# Sai:
g = SavingsGoal(user_id=user_id, target_date=target_date, ...)
AuditRepository(session).log_action(user_id, "create_goal", "goal", extra=name)

# Đúng:
g = SavingsGoal(user_id=user_id, deadline=target_date, ...)
AuditRepository(session).log_action(user_id, "create_goal", "goal")

# Cũng sửa get_goals():
if g.deadline:           # thay vì g.target_date
    days_left = (g.deadline - date.today()).days
```

### Fix #3: pages/accounts.py — Toàn bộ page cần sửa
```python
# Model field names:
acc.account_type    # thay vì acc.type
acc.description     # thay vì acc.notes

# Create account:
data = AccountCreate(
    account_type=acc_type,      # thay vì type=acc_type
    initial_balance=balance,    # thay vì balance=balance
    description=notes or None,  # thay vì notes=
    ...
)

# Update account:
from schemas.account import AccountUpdate
data = AccountUpdate(name=new_name, balance=new_balance, description=new_notes)
ok, msg = AccountService.update_account(user_id, acc.id, data)

# Delete account:
ok, msg = AccountService.close_account(user_id, acc.id)  # thay vì delete_account
```

### Fix #4: pages/transactions.py — get_category_map unpack
```python
# Sai:
category_map, subcategory_map = cat_service.get_category_map(user_id)

# Đúng:
category_map = cat_service.get_category_map(user_id)
subcategory_map = cat_service.get_subcategory_map(user_id)
```

### Fix #5: pages/forex.py — Field names & dict access & arg order
```python
# Sai:
for r in rates:
    rows.append({
        "Ngoại tệ": r.currency_code,           # dot trên dict
        "Mua TM": format_number(r.buy_cash, 2), # field sai
        "Mua CK": format_number(r.buy_transfer, 2),
        "Bán": format_number(r.sell, 2),
    })

# Đúng:
for r in rates:
    rows.append({
        "Ngoại tệ": r["currency_code"],
        "Mua": format_number(r["buy_rate"], 2) if r["buy_rate"] else "-",
        "Bán": format_number(r["sell_rate"], 2) if r["sell_rate"] else "-",
        "Chuyển khoản": format_number(r["transfer_rate"], 2) if r["transfer_rate"] else "-",
    })

# Sửa convert_to_vnd argument order:
result = FxService.convert_to_vnd(amount, currency)  # thay vì (currency, amount)
```

### Fix #6: pages/gold.py — weight_gram, total_cost, dict access, add_holding args
```python
# Dot notation trên dict → bracket notation:
for p in prices:
    rows.append({
        "Loại vàng": p["gold_type"],
        "Mua": format_currency(p["buy_price"]) if p["buy_price"] else "-",
        "Bán": format_currency(p["sell_price"]) if p["sell_price"] else "-",
        ...
    })

# weight_gram → quantity:
format_weight(holding.quantity)

# total_cost → cost:
total_cost = sum(h.get("cost", 0) for h in holdings)

# add_holding thiếu unit:
ok, msg = GoldService.add_holding(
    user_id, gold_type, weight, "gram", buy_price, buy_date, notes=notes or None
)
```

### Fix #7: report_service.py — a.type → a.account_type
```python
# Sai:
{"name": a.name, "type": a.type, "currency": a.currency, ...}

# Đúng:
{"name": a.name, "type": a.account_type, "currency": a.currency, ...}
```

### Fix #8: dashboard.py — Budget category label
```python
# Sai:
label = b["budget"].category.name if b["budget"].category_id else "Tổng chi tiêu"

# Đúng (copy cách budgets.py page làm):
if b["budget"].category_id:
    from db.database import get_session
    from models.category import Category
    session = get_session()
    try:
        cat = session.query(Category).get(b["budget"].category_id)
        label = cat.name if cat else f"Danh mục #{b['budget'].category_id}"
    finally:
        session.close()
else:
    label = "Tổng chi tiêu"
```

### Fix #9: pages/categories.py — delete methods & create_subcategory args
```python
# Thêm methods vào CategoryService:
@staticmethod
def delete_category(user_id: int, category_id: int) -> tuple:
    session = get_session()
    try:
        repo = CategoryRepository(session)
        cat = repo.get_by_id(category_id)
        if not cat or cat.user_id != user_id:
            return False, "Không tìm thấy"
        if cat.is_system:
            return False, "Không thể xóa danh mục hệ thống"
        repo.soft_delete(cat)
        session.commit()
        return True, "Đã xóa danh mục"
    except Exception as e:
        session.rollback()
        return False, f"Lỗi: {e}"
    finally:
        session.close()

@staticmethod
def delete_subcategory(user_id: int, subcategory_id: int) -> tuple:
    # Tương tự

# Sửa create_subcategory call:
ok, msg = cat_service.create_subcategory(cat_id, sub_name.strip())
# (bỏ user_id ở đầu)
```

---

## 📋 X. TỔNG KẾT

### Thống kê bugs

| Mức độ | Số lượng | Ảnh hưởng |
|--------|----------|-----------|
| 🔴 Critical (crash) | 20 | App crash khi dùng chức năng |
| 🟡 Logic bug | 1 | Kết quả sai nhưng không crash |
| **Tổng** | **21** | |

### Tính năng thiếu quan trọng

| # | Tính năng | Mức ưu tiên |
|---|-----------|-------------|
| 1 | Dashboard tổng tài sản = VND + Forex + Vàng + CK | 🔴 Cao |
| 2 | Cross-asset transactions (mua/bán vàng/CK từ tài khoản) | 🟡 Trung bình |
| 3 | API giá chứng khoán real-time (thay vì manual) | 🟡 Trung bình |
| 4 | Account type "stock" cho danh mục đầu tư CK | 🟢 Thấp |
| 5 | Recurring transaction auto-execution (model có, logic chưa) | 🟡 Trung bình |
| 6 | Price alerts (cảnh báo giá vàng/CK) | 🟢 Thấp |

### Điểm mạnh của dự án

- ✅ **Kiến trúc phân tầng rõ ràng**: Model → Repository → Service → Page
- ✅ **Provider pattern** cho FX/Gold với 3-4 cấp fallback, rất resilient
- ✅ **Token management** tự động refresh, xử lý 403
- ✅ **In-memory cache** với TTL
- ✅ **Soft delete** pattern nhất quán
- ✅ **Audit logging** (khi gọi đúng method)
- ✅ **Dark glassmorphism UI** đẹp với custom CSS + Plotly charts
- ✅ **Dual database** support (SQLite + PostgreSQL)
- ✅ **Export** Excel/CSV
- ✅ **Backup/Restore** database
- ✅ **Pydantic v2** validation cho input

### Ưu tiên sửa

1. **Ngay lập tức:** Fix 20 critical bugs (nhiều page không thể hoạt động)
2. **Ngắn hạn:** Dashboard tổng tài sản toàn diện
3. **Trung hạn:** Cross-asset transactions, API CK real-time
4. **Dài hạn:** Recurring auto-execution, price alerts, multi-currency portfolio analytics

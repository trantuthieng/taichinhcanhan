"""Constants - Hằng số toàn ứng dụng."""

# Loại tài khoản
ACCOUNT_TYPES = ["cash", "bank", "ewallet", "forex", "gold", "savings", "other"]

# Loại giao dịch
TRANSACTION_TYPES = ["income", "expense", "transfer"]

# Đơn vị tiền tệ chính
CURRENCIES = ["VND", "USD", "EUR", "JPY", "GBP", "AUD", "CAD", "CHF", "CNY", "KRW", "SGD", "THB", "TWD", "HKD"]

# Tần suất giao dịch định kỳ
RECURRING_FREQUENCIES = {
    "daily": "Hàng ngày",
    "weekly": "Hàng tuần",
    "monthly": "Hàng tháng",
    "quarterly": "Hàng quý",
    "yearly": "Hàng năm",
}

# Kỳ hạn gửi tiết kiệm phổ biến (tháng)
SAVINGS_TERMS = [1, 2, 3, 6, 9, 12, 13, 15, 18, 24, 36]

# Phương thức trả lãi
INTEREST_PAYMENT_METHODS = {
    "prepaid": "Trả lãi trước",
    "monthly": "Trả lãi hàng tháng",
    "maturity": "Trả lãi cuối kỳ",
}

# Loại vàng phổ biến
GOLD_TYPES = [
    "SJC 1 lượng",
    "SJC 5 chỉ",
    "SJC 2 chỉ",
    "SJC 1 chỉ",
    "Nhẫn SJC 99.99",
    "Nhẫn PNJ 99.99",
    "Nhẫn DOJI 99.99",
    "Vàng 24K",
    "Vàng 18K",
    "Vàng 14K",
]

# Trạng thái tiết kiệm
DEPOSIT_STATUSES = ["active", "closed", "matured"]

# Trạng thái mục tiêu
GOAL_STATUSES = ["active", "completed", "cancelled"]

# Ngân hàng Việt Nam phổ biến
VN_BANKS = [
    "Vietcombank", "VietinBank", "BIDV", "Agribank",
    "Techcombank", "MB Bank", "ACB", "VPBank",
    "TPBank", "Sacombank", "HDBank", "SHB",
    "MSB", "VIB", "SeABank", "LienVietPostBank",
    "OCB", "Nam A Bank", "Bac A Bank", "Eximbank",
]

# Ví điện tử phổ biến
VN_EWALLETS = [
    "Momo", "ZaloPay", "VNPay", "ShopeePay",
    "ViettelPay", "Moca", "VNPT Pay",
]

# Màu sắc cho biểu đồ
CHART_COLORS = [
    "#FF6384", "#36A2EB", "#FFCE56", "#4BC0C0",
    "#9966FF", "#FF9F40", "#C9CBCF", "#7BC225",
    "#E7515A", "#2196F3", "#00BCD4", "#8BC34A",
    "#FF5722", "#607D8B", "#795548", "#9C27B0",
]

# Tháng tiếng Việt
VN_MONTHS = {
    1: "Tháng 1", 2: "Tháng 2", 3: "Tháng 3",
    4: "Tháng 4", 5: "Tháng 5", 6: "Tháng 6",
    7: "Tháng 7", 8: "Tháng 8", 9: "Tháng 9",
    10: "Tháng 10", 11: "Tháng 11", 12: "Tháng 12",
}

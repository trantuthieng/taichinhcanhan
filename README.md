# 💰 Quản lý Tài chính Cá nhân

Ứng dụng quản lý tài chính cá nhân / hộ gia đình viết bằng Python + Streamlit.

## Tính năng chính

- **📊 Tổng quan (Dashboard)**: Biểu đồ thu chi, dòng tiền, phân bổ tài sản
- **🏦 Tài khoản**: Quản lý tiền mặt, ngân hàng, ví điện tử, ngoại tệ, vàng
- **💳 Giao dịch**: Thu/chi/chuyển khoản, lọc theo thời gian, loại, danh mục
- **📂 Danh mục**: Tự quản lý nhóm + danh mục con, mặc định danh mục Việt Nam
- **🏧 Tiết kiệm**: Sổ tiết kiệm, tính lãi (trả trước/hàng tháng/cuối kỳ), lãi kép, đáo hạn
- **💱 Tỷ giá**: Đồng bộ tỷ giá tự động (VNAppMob → Vietcombank XML → DB cache), quy đổi
- **🥇 Vàng**: Giá vàng SJC/PNJ/DOJI, quản lý vàng nắm giữ, tính P&L
- **📋 Ngân sách**: Thiết lập hạn mức chi tiêu theo tháng, theo dõi tiến độ
- **🎯 Mục tiêu**: Mục tiêu tiết kiệm với tiến độ, cảnh báo hạn
- **📈 Báo cáo**: Tổng hợp thu chi, biểu đồ phân tích, xuất Excel/CSV
- **⚙️ Cài đặt**: Đổi mật khẩu, sao lưu/khôi phục, trạng thái API

## Yêu cầu

- Python 3.11+
- Windows / macOS / Linux

## Cài đặt & Chạy

### Cách 1: Tự động (Windows)
```bash
# Chạy file run.bat
run.bat
```

### Cách 2: Thủ công
```bash
# Tạo virtual environment
python -m venv venv

# Kích hoạt (Windows)
venv\Scripts\activate

# Kích hoạt (macOS/Linux)
source venv/bin/activate

# Cài đặt gói
pip install -r requirements.txt

# Tạo file .env
copy .env.example .env   # Windows
cp .env.example .env     # macOS/Linux

# Chạy ứng dụng
streamlit run app.py
```

## Tài khoản mặc định

- **Username**: admin
- **Password**: admin123

## Cấu hình

Chỉnh sửa file `.env`:

```env
# Database
DATABASE_URL=sqlite:///finance.db

# Admin mặc định
ADMIN_USERNAME=admin
ADMIN_PASSWORD=admin123
ADMIN_FULLNAME=Quản trị viên

# API VNAppMob (tỷ giá & giá vàng)
VNAPPMOB_BASE_URL=https://appmob.vn/api

# Vietcombank XML (fallback)
VCB_EXCHANGE_URL=https://portal.vietcombank.com.vn/Usercontrols/TVPortal.TyGia/pXML.aspx
```

## Kiến trúc

```
app.py                  # Entry point
config.py               # Settings
├── db/                 # Database layer
│   ├── database.py     # SQLAlchemy engine
│   ├── init_db.py      # Khởi tạo DB
│   └── seed.py         # Dữ liệu mặc định
├── models/             # ORM models (SQLAlchemy)
├── schemas/            # Pydantic validation
├── repositories/       # Data access layer
├── services/           # Business logic
│   └── providers/      # API providers (VNAppMob, VCB, Manual)
├── pages/              # Streamlit pages
├── ui/                 # UI components, styles, charts
├── utils/              # Helpers, formatters, validators
└── backups/            # Auto-generated backup folder
```

## Công nghệ

| Thành phần | Công nghệ |
|---|---|
| Web framework | Streamlit |
| Database | SQLite (WAL mode) |
| ORM | SQLAlchemy 2.x |
| Validation | Pydantic v2 |
| Charts | Plotly |
| Password | bcrypt |
| Data | pandas |
| Export | openpyxl, xlsxwriter |

## License

MIT

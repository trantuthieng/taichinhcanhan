# CODEX TASKS — Backlog kỹ thuật để giao cho Codex code từ đầu đến cuối

> Tạo 11/07/2026. File này là bản dịch kỹ thuật (schema, đường dẫn file, function signature, acceptance criteria) của roadmap ở `note.txt` mục 29, viết để giao thẳng cho một coding agent (Codex) thực thi, không cần hỏi lại. `note.txt` là tài liệu ý tưởng sản phẩm đầy đủ (bối cảnh, lý do); file này là backlog thực thi. Khi giao việc, copy nguyên 1 khối `## Sprint X.Y` làm prompt — mỗi khối tự chứa đủ ngữ cảnh để làm độc lập, miễn Sprint phụ thuộc đã xong.

## Cách dùng file này

1. Làm tuần tự theo thứ tự Phase 1 → 2 → 3 → 4 → 5, và trong mỗi Phase theo thứ tự Sprint — có phụ thuộc kỹ thuật thật (ghi rõ ở mỗi Sprint), không nhảy cóc.
2. Mỗi Sprint có: Mục tiêu, Phụ thuộc, Việc cần làm (đủ chi tiết để code thẳng), Schema/API nếu có, Acceptance Criteria, Không làm (out of scope — quan trọng để agent không tự ý mở rộng).
3. **Giới hạn quan trọng cần biết trước khi giao Codex:** các Sprint thuộc `AssetTracker/` (Swift/SwiftUI) cần **Xcode trên macOS** để build và tự kiểm tra Acceptance Criteria. Nếu Codex chạy trong sandbox Linux/cloud không có Xcode, Codex vẫn sinh code Swift đúng cấu trúc được, nhưng bạn phải tự mở Xcode trên Mac để build/chạy simulator và xác nhận Definition of Done. Ngược lại, các Sprint thuộc `supabase/` (SQL migration, Edge Function Deno/TypeScript) không cần macOS — Codex tự chạy `supabase db push`, `supabase functions serve`/`deploy`, `deno test` được, không cần con người can thiệp để verify.
4. Việc **thủ công không giao được cho Codex** (cần tài khoản/thao tác trên web dashboard của bạn) được đánh dấu rõ **[THỦ CÔNG]** — làm trước khi tới Sprint liên quan.

---

## 0. Quy ước chung toàn dự án

### 0.1. Tech stack đã chốt (không đổi, không đề xuất thay thế)

- iOS, Swift, SwiftUI, Swift Charts, Local Notifications, LocalAuthentication (Face ID/Touch ID/PIN)
- Backend: Supabase (Postgres + Storage + Edge Functions/Deno), client `supabase-swift`, **không dùng Supabase Auth** (mô hình no-auth, `note.txt` mục 28.3)
- Cache cục bộ: SwiftData (offline cache + hàng đợi ghi khi mất mạng), Supabase luôn là source of truth
- Không dùng CloudKit/iCloud, không dùng Firebase/Mixpanel/Sentry hay bất kỳ SDK phân tích/theo dõi bên thứ ba nào

### 0.2. Cấu trúc thư mục chốt

```text
22 quản lý tài sản/
├── note.txt
├── CODEX_TASKS.md
├── AssetTracker/                        (Xcode project — tạo bằng Xcode "App" template, SwiftUI, iOS, tên "AssetTracker")
│   ├── AssetTracker.xcodeproj
│   └── AssetTracker/
│       ├── App/
│       │   └── AssetTrackerApp.swift
│       ├── Config/
│       │   ├── Secrets.example.swift      (commit vào git, chỉ có placeholder)
│       │   └── Secrets.swift              (gitignore — chứa URL + anon key thật)
│       ├── Core/
│       │   ├── Models/
│       │   │   ├── Enums.swift
│       │   │   ├── AssetAccount.swift
│       │   │   ├── Asset.swift
│       │   │   ├── AssetTransaction.swift
│       │   │   ├── SavingsDeposit.swift
│       │   │   ├── Liability.swift
│       │   │   └── ValuationSnapshot.swift
│       │   ├── Services/
│       │   │   ├── SupabaseClientProvider.swift
│       │   │   ├── FinanceCalculator.swift
│       │   │   ├── SnapshotScheduler.swift
│       │   │   ├── PriceAlertService.swift
│       │   │   ├── ReminderScheduler.swift
│       │   │   ├── CSVExportService.swift
│       │   │   ├── PDFReportGenerator.swift
│       │   │   ├── ConcentrationAnalyzer.swift
│       │   │   └── CashFlowForecastService.swift
│       │   └── Security/
│       │       ├── BiometricAuthManager.swift
│       │       └── PrivacyModeManager.swift
│       ├── Data/
│       │   ├── Repositories/
│       │   │   ├── Repository.swift              (protocol chung)
│       │   │   ├── AssetAccountRepository.swift
│       │   │   ├── AssetRepository.swift
│       │   │   ├── AssetTransactionRepository.swift
│       │   │   ├── SavingsDepositRepository.swift
│       │   │   ├── LiabilityRepository.swift
│       │   │   ├── ValuationSnapshotRepository.swift
│       │   │   └── PriceSnapshotRepository.swift
│       │   └── LocalCache/
│       │       ├── CachedModels.swift            (SwiftData @Model, mirror các struct trên)
│       │       ├── PendingWriteOperation.swift
│       │       └── OfflineSyncManager.swift
│       ├── Features/
│       │   ├── Dashboard/
│       │   ├── Assets/
│       │   │   ├── Cash/
│       │   │   ├── Stocks/
│       │   │   ├── Gold/
│       │   │   ├── Savings/
│       │   │   └── Other/
│       │   ├── Transactions/
│       │   ├── Liabilities/
│       │   ├── Reports/
│       │   ├── Simulation/
│       │   ├── Security/
│       │   └── Settings/
│       └── UI/
│           ├── Components/
│           ├── Charts/
│           └── Themes/
├── AssetTrackerWidget/                  (WidgetKit extension target, thêm ở Sprint 2.4)
├── AssetTrackerTests/                   (unit test target)
└── supabase/
    ├── config.toml
    ├── migrations/
    │   ├── 0001_init_schema.sql
    │   ├── 0002_price_snapshots.sql
    │   ├── 0003_expand_liabilities.sql
    │   ├── 0004_extend_asset_category.sql
    │   └── 0005_add_edited_by.sql
    └── functions/
        ├── _shared/
        │   ├── types.ts
        │   ├── supabaseAdminClient.ts
        │   └── dnseSignature.ts
        ├── fetch-gold-price/index.ts
        ├── fetch-stock-price/index.ts
        └── generate-ai-summary/index.ts
```

### 0.3. Coding conventions

- Tiền tệ/số lượng luôn dùng `Decimal` trong Swift và `numeric` trong Postgres — **không bao giờ dùng `Double`/`Float`** cho tiền.
- Postgres: tên bảng/cột `snake_case`. Swift: `camelCase` — map qua `CodingKeys` trong từng struct `Codable`.
- Enum lưu dưới dạng `text` trong Postgres kèm `CHECK` constraint liệt kê giá trị hợp lệ, khớp chính xác raw value của Swift enum tương ứng (mục 0.2 style).
- Mọi bảng đều bật RLS + policy cho phép role `anon` đọc/ghi toàn bộ (không tắt RLS, theo `note.txt` mục 28.4).
- Repository pattern bắt buộc cho mọi truy cập dữ liệu — UI/ViewModel không được gọi thẳng `SupabaseClientProvider`.
- Số dư/số lượng tài sản luôn **tính lại từ `asset_transactions`** (append-only log), không lưu và đồng bộ trực tiếp field `balance`/`quantity` (theo `note.txt` mục 26.4 — quan trọng để an toàn khi nhiều thiết bị ghi cùng lúc ở Phase 4).
- App không bao giờ gọi thẳng API BTMC/DNSE — luôn đọc từ bảng `price_snapshots` do Edge Function ghi (theo `note.txt` mục 29.3).

### 0.4. Không làm ở bất kỳ Sprint nào (áp dụng toàn dự án)

- Không thêm màn hình đăng nhập/tài khoản, không thêm Supabase Auth.
- Không thêm license/paywall/in-app purchase/feature gating.
- Không thêm SDK phân tích, crash reporting, quảng cáo bên thứ ba.
- Không tự ý thêm tính năng ngoài checklist của Sprint đang làm, kể cả khi "tiện làm luôn" — sinh ra ở đúng Sprint dự kiến trong roadmap.
- Không đặt lệnh mua/bán thật qua DNSE — chỉ đọc giá.

### 0.5. Definition of Done chung cho mọi Sprint

- Build không lỗi, không warning mới phát sinh.
- Test (nếu Sprint yêu cầu) chạy pass.
- Với Sprint có UI: chạy được trên iOS Simulator, luồng chính trong Acceptance Criteria thao tác được bằng tay.
- Với Sprint Edge Function: `supabase functions serve` chạy local gọi thử thành công trước khi deploy.

---

# PHASE 1 — Nền tảng và MVP đủ 4 nhóm tài sản

## Sprint 1.1 — Setup hạ tầng

**Mục tiêu:** dựng khung Xcode + Supabase project, schema Postgres đầy đủ theo `note.txt` mục 14.

**Phụ thuộc:** không.

**[THỦ CÔNG] trước khi bắt đầu:**
- Tạo project mới tại supabase.com/dashboard, ghi lại Project URL và anon key.
- Cài Supabase CLI (`npm install -g supabase` hoặc brew), `supabase login`, `supabase link --project-ref <ref>`.

### Việc cần làm

1. `git init` tại thư mục gốc dự án, tạo `.gitignore` (loại trừ `Secrets.swift`, `.build/`, `DerivedData/`, `.env`).
2. Tạo Xcode project SwiftUI mới tên `AssetTracker` theo đúng cấu trúc thư mục ở mục 0.2 (deployment target iOS 17+, để dùng được SwiftData và Swift Charts đầy đủ).
3. Thêm package `supabase-swift` qua Swift Package Manager.
4. Tạo `Config/Secrets.example.swift`:
   ```swift
   enum Secrets {
       static let supabaseURL = "https://YOUR_PROJECT.supabase.co"
       static let supabaseAnonKey = "YOUR_ANON_KEY"
   }
   ```
   Copy thành `Secrets.swift` (gitignored) và điền giá trị thật.
5. Tạo `Core/Services/SupabaseClientProvider.swift`:
   ```swift
   import Supabase

   enum SupabaseClientProvider {
       static let shared = SupabaseClient(
           supabaseURL: URL(string: Secrets.supabaseURL)!,
           supabaseKey: Secrets.supabaseAnonKey
       )
   }
   ```
6. Dựng `App/AssetTrackerApp.swift` với `TabView` 5 tab rỗng (Tổng quan, Tài sản, Giao dịch, Báo cáo, Cài đặt) theo `note.txt` mục 7.
7. Tạo `supabase/migrations/0001_init_schema.sql`:

```sql
-- asset_accounts
create table public.asset_accounts (
    id uuid primary key default gen_random_uuid(),
    name text not null,
    institution text,
    account_type text not null check (account_type in (
        'cash_personal','cash_family','bank_account','salary_account',
        'spending_account','e_wallet','emergency_fund','travel_fund',
        'investment_fund','foreign_currency_cash'
    )),
    currency text not null default 'VND',
    balance numeric not null default 0,
    exchange_rate_at_opening numeric,
    current_exchange_rate numeric,
    is_included_in_net_worth boolean not null default true,
    target_group text,
    note text,
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now()
);

-- assets (chứng khoán + vàng ở Phase 1; mở rộng category ở Phase 3)
create table public.assets (
    id uuid primary key default gen_random_uuid(),
    name text not null,
    category text not null check (category in (
        'stock','fund_certificate','etf','listed_bond','warrant',
        'foreign_stock','open_end_fund','other_security',
        'gold_bar_sjc','gold_ring_9999','gold_bar_other_brand','gold_jewelry',
        'gold_24k','gold_18k','gold_14k','gold_international','other_gold'
    )),
    account_id uuid references public.asset_accounts(id),
    symbol text,
    brand text,
    unit text not null check (unit in ('share','luong','cay','chi','phan','gram','ounce')),
    quantity numeric not null default 0,
    average_cost numeric not null default 0,
    current_price numeric not null default 0,
    currency text not null default 'VND',
    acquisition_date date,
    valuation_date timestamptz not null default now(),
    purchase_location text,
    storage_location text,
    invoice_number text,
    invoice_attachment_url text,
    gross_weight numeric,
    pure_gold_weight numeric,
    gold_purity numeric,
    labor_cost numeric,
    gemstone_value numeric,
    depreciation_rate numeric,
    expected_buyback_price numeric,
    note text,
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now()
);

-- asset_transactions (append-only log)
create table public.asset_transactions (
    id uuid primary key default gen_random_uuid(),
    asset_id uuid references public.assets(id),
    type text not null check (type in (
        'deposit','withdrawal','transfer','buy','sell','interest',
        'dividend','maturity','repayment','fee','tax','adjustment'
    )),
    date timestamptz not null,
    quantity numeric,
    unit_price numeric,
    amount numeric not null,
    fee numeric not null default 0,
    tax numeric not null default 0,
    source_account_id uuid references public.asset_accounts(id),
    destination_account_id uuid references public.asset_accounts(id),
    note text,
    attachment_url text,
    created_at timestamptz not null default now()
);

-- savings_deposits
create table public.savings_deposits (
    id uuid primary key default gen_random_uuid(),
    name text not null,
    bank_name text not null,
    principal numeric not null,
    currency text not null default 'VND',
    annual_interest_rate numeric not null,
    start_date date not null,
    maturity_date date not null,
    term_in_months int not null,
    interest_payment_type text not null check (interest_payment_type in ('end_of_term','monthly','upfront')),
    auto_renewal_type text check (auto_renewal_type in ('none','principal_only','principal_and_interest')),
    early_withdrawal_rate numeric,
    status text not null default 'active' check (status in ('active','matured','closed','withdrawn_early')),
    contract_number text,
    attachment_url text,
    account_id uuid references public.asset_accounts(id),
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now()
);

-- liabilities
create table public.liabilities (
    id uuid primary key default gen_random_uuid(),
    name text not null,
    lender text,
    original_principal numeric not null,
    current_balance numeric not null,
    annual_interest_rate numeric not null,
    start_date date not null,
    maturity_date date,
    payment_frequency text check (payment_frequency in ('monthly','quarterly','semi_annual','annual','one_time')),
    next_payment_date date,
    monthly_payment numeric,
    collateral text,
    note text,
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now()
);

-- valuation_snapshots
create table public.valuation_snapshots (
    id uuid primary key default gen_random_uuid(),
    date date not null unique,
    total_assets numeric not null,
    total_liabilities numeric not null,
    net_worth numeric not null,
    cash_value numeric not null,
    stock_value numeric not null,
    gold_value numeric not null,
    savings_value numeric not null,
    other_asset_value numeric not null default 0,
    fx_rates_snapshot jsonb,
    created_at timestamptz not null default now()
);

-- RLS: bật cho toàn bộ bảng, cho phép anon đọc/ghi (mô hình no-auth, note.txt mục 28.4)
do $$
declare t text;
begin
  for t in select unnest(array[
    'asset_accounts','assets','asset_transactions',
    'savings_deposits','liabilities','valuation_snapshots'
  ])
  loop
    execute format('alter table public.%I enable row level security;', t);
    execute format('create policy "allow anon all" on public.%I for all to anon using (true) with check (true);', t);
  end loop;
end $$;
```

8. Chạy `supabase db push` để áp migration.
9. Test tay: gọi `SupabaseClientProvider.shared.from("asset_accounts").insert(...)` từ 1 nút debug tạm trong app, xác nhận ghi được, rồi xóa nút debug.

### Acceptance Criteria
- [ ] `supabase db push` chạy thành công, 6 bảng xuất hiện trong Supabase Dashboard, RLS bật (không có cảnh báo "Unrestricted" trong Dashboard).
- [ ] App build chạy trên Simulator, thấy 5 tab rỗng.
- [ ] Ghi thử 1 row vào `asset_accounts` từ app thành công, thấy trong Supabase Dashboard.

### Không làm
- Chưa cần UI thật cho từng tab — chỉ khung điều hướng.
- Chưa tạo bảng `price_snapshots` (thuộc Sprint 2.1).

---

## Sprint 1.2 — Data layer & Repository

**Mục tiêu:** models Swift + Repository pattern + cache offline.

**Phụ thuộc:** Sprint 1.1.

### Việc cần làm

1. `Core/Models/Enums.swift`:
   ```swift
   enum AccountType: String, Codable, CaseIterable {
       case cashPersonal = "cash_personal", cashFamily = "cash_family"
       case bankAccount = "bank_account", salaryAccount = "salary_account"
       case spendingAccount = "spending_account", eWallet = "e_wallet"
       case emergencyFund = "emergency_fund", travelFund = "travel_fund"
       case investmentFund = "investment_fund", foreignCurrencyCash = "foreign_currency_cash"
   }

   enum AssetCategory: String, Codable, CaseIterable {
       case stock, fundCertificate = "fund_certificate", etf
       case listedBond = "listed_bond", warrant
       case foreignStock = "foreign_stock", openEndFund = "open_end_fund", otherSecurity = "other_security"
       case goldBarSJC = "gold_bar_sjc", goldRing9999 = "gold_ring_9999"
       case goldBarOtherBrand = "gold_bar_other_brand", goldJewelry = "gold_jewelry"
       case gold24K = "gold_24k", gold18K = "gold_18k", gold14K = "gold_14k"
       case goldInternational = "gold_international", otherGold = "other_gold"
   }

   enum AssetUnit: String, Codable, CaseIterable {
       case share, luong, cay, chi, phan, gram, ounce
   }

   enum CurrencyCode: String, Codable, CaseIterable {
       case vnd = "VND", usd = "USD", eur = "EUR", jpy = "JPY", aud = "AUD"
       case cad = "CAD", sgd = "SGD", cny = "CNY", krw = "KRW", other = "OTHER"
   }

   enum TransactionType: String, Codable, CaseIterable {
       case deposit, withdrawal, transfer, buy, sell, interest
       case dividend, maturity, repayment, fee, tax, adjustment
   }

   enum InterestPaymentType: String, Codable, CaseIterable {
       case endOfTerm = "end_of_term", monthly, upfront
   }

   enum AutoRenewalType: String, Codable, CaseIterable {
       case none, principalOnly = "principal_only", principalAndInterest = "principal_and_interest"
   }

   enum DepositStatus: String, Codable, CaseIterable {
       case active, matured, closed, withdrawnEarly = "withdrawn_early"
   }

   enum PaymentFrequency: String, Codable, CaseIterable {
       case monthly, quarterly, semiAnnual = "semi_annual", annual, oneTime = "one_time"
   }
   ```
2. Tạo 6 struct `Codable` trong `Core/Models/` khớp 1-1 với schema Sprint 1.1 (mỗi struct dùng `CodingKeys` map `snake_case` ↔ `camelCase`), theo đúng field đã liệt kê trong migration — bao gồm `AssetAccount` đã có thêm `exchangeRateAtOpening`/`currentExchangeRate` (`note.txt` mục 14.1).
3. `Data/Repositories/Repository.swift`:
   ```swift
   protocol Repository {
       associatedtype Model: Codable, Identifiable
       func fetchAll() async throws -> [Model]
       func fetchByID(_ id: UUID) async throws -> Model?
       func insert(_ model: Model) async throws -> Model
       func update(_ model: Model) async throws -> Model
       func delete(id: UUID) async throws
   }
   ```
4. Implement 6 repository tương ứng (`AssetAccountRepository`, `AssetRepository`, `AssetTransactionRepository`, `SavingsDepositRepository`, `LiabilityRepository`, `ValuationSnapshotRepository`), mỗi cái gọi `SupabaseClientProvider.shared.from("<table>")`.
5. `Data/LocalCache/CachedModels.swift`: khai báo `@Model` SwiftData cho từng entity (mirror struct ở bước 2), dùng làm cache đọc offline.
6. `Data/LocalCache/PendingWriteOperation.swift`: `@Model` lưu `id`, `entityType: String`, `operationType: String` (insert/update/delete), `payloadJSON: Data`, `createdAt: Date`.
7. `Data/LocalCache/OfflineSyncManager.swift`: actor theo dõi kết nối mạng (`NWPathMonitor`), khi có mạng lại thì đọc `PendingWriteOperation` theo thứ tự `createdAt` và gọi lại repository tương ứng, xóa khỏi hàng đợi khi thành công.
8. Mỗi repository: khi gọi insert/update mà network fail → ghi vào `PendingWriteOperation` thay vì throw thẳng ra UI, đồng thời cập nhật cache cục bộ ngay (optimistic).
9. `AssetTransactionRepository` cần thêm hàm `computeCurrentQuantityAndCost(forAssetID:) -> (quantity: Decimal, averageCost: Decimal)` tính lại từ toàn bộ `asset_transactions` liên quan — đây là hàm dùng xuyên suốt Sprint 1.4, không lưu số dư trực tiếp.

### Acceptance Criteria
- [ ] Thêm/sửa/xóa 1 bản ghi test cho cả 6 entity qua code (không qua UI) thành công.
- [ ] Tắt wifi, đọc lại danh sách vẫn thấy dữ liệu (từ cache SwiftData).
- [ ] Tắt wifi, thêm 1 bản ghi mới → bật wifi lại → bản ghi tự động xuất hiện trên Supabase Dashboard (verify qua `OfflineSyncManager`).

### Không làm
- Chưa nối UI thật — test bằng unit test hoặc nút debug tạm.
- Chưa xử lý conflict phức tạp giữa nhiều thiết bị (đó là Sprint 4.1, sau khi có nhiều thiết bị thật để test).

---

## Sprint 1.3 — CRUD UI cho 4 nhóm tài sản

**Mục tiêu:** màn hình thêm/sửa/xóa cho Tiền mặt, Chứng khoán, Vàng, Tiết kiệm.

**Phụ thuộc:** Sprint 1.2.

### Việc cần làm

1. `Features/Assets/Cash/`: `CashAccountListView.swift`, `CashAccountFormView.swift`, `CashAccountViewModel.swift` (`@MainActor @Observable` hoặc `ObservableObject`).
   - Form theo `note.txt` luồng 8.1: tên tài khoản, loại tài khoản (picker `AccountType`), số dư, `Tiền tệ` (picker `CurrencyCode`) — **nếu chọn khác VND, hiện thêm 2 field: tỷ giá mua, tỷ giá hiện tại** (`note.txt` mục 4.1.5), tổ chức quản lý, nhóm mục tiêu, ghi chú.
2. `Features/Assets/Stocks/`: `StockListView.swift`, `StockFormView.swift`, `StockViewModel.swift`.
   - Form theo luồng 8.2: mã CK (text), tài khoản CK (picker `AssetAccount` lọc theo loại phù hợp), ngày mua, số lượng, giá mua, phí — tạo `Asset` (category = stock) **và** 1 `AssetTransaction` (type = buy) cùng lúc.
3. `Features/Assets/Gold/`: `GoldListView.swift`, `GoldFormView.swift`, `GoldViewModel.swift`.
   - Form theo luồng 8.4: loại vàng (picker `AssetCategory` lọc nhóm gold_*), thương hiệu, số lượng, đơn vị (picker `AssetUnit`), giá mua, ngày mua, nơi mua, nơi lưu giữ, đính kèm hóa đơn (dùng Supabase Storage, bucket `attachments`).
   - Nếu category = `goldJewelry`: hiện thêm field trọng lượng tổng, trọng lượng vàng thực, tuổi vàng, tiền công, giá trị đá quý (`note.txt` mục 4.3.6).
4. `Features/Assets/Savings/`: `SavingsListView.swift`, `SavingsFormView.swift`, `SavingsViewModel.swift`.
   - Form theo luồng 8.5: ngân hàng, số tiền, kỳ hạn, lãi suất, ngày gửi, hình thức nhận lãi, hình thức tái tục — `maturityDate` tự tính = `startDate + termInMonths`.
5. `Features/Assets/AssetsTabView.swift`: danh sách 4 nhóm (`note.txt` mục 7.2), mỗi nhóm hiện tổng giá trị/giá vốn/lãi-lỗ/tỷ trọng/số lượng khoản mục — tính từ `FinanceCalculator` (Sprint 1.4) và dữ liệu Repository.
6. Sửa/xóa cho cả 4 nhóm (swipe-to-delete + form sửa dùng lại form thêm với dữ liệu prefill).

### Acceptance Criteria
- [ ] Nhập được ít nhất 1 khoản mục thật (dữ liệu thật của người dùng) cho cả 4 nhóm, hiện đúng trong danh sách.
- [ ] Tạo tài khoản Tiền mặt với `Tiền tệ` = USD, nhập tỷ giá, thấy giá trị quy đổi VND hiển thị đúng ở list.
- [ ] Sửa và xóa hoạt động cho cả 4 nhóm không crash.

### Không làm
- Chưa cần Dashboard tổng hợp (Sprint 1.5).
- Chưa cần validate nâng cao (ví dụ tra cứu mã CK hợp lệ qua API) — nhập tay tự do ở Phase 1.

---

## Sprint 1.4 — Giao dịch & công thức tài chính

**Mục tiêu:** engine tính toán tài chính + màn hình giao dịch, có unit test.

**Phụ thuộc:** Sprint 1.3.

### Việc cần làm

1. `Core/Services/FinanceCalculator.swift`:
   ```swift
   enum FinanceCalculator {
       // mục 4.2.5 — giá vốn bình quân
       static func averageCost(lots: [(quantity: Decimal, unitPrice: Decimal, fee: Decimal)]) -> Decimal

       // mục 3.6 / 3.7
       static func profitLoss(currentValue: Decimal, remainingCost: Decimal) -> Decimal
       static func profitRate(profitLoss: Decimal, cost: Decimal) -> Decimal

       // mục 4.4.3 / 4.4.4 / 4.4.5
       static func expectedInterestAtMaturity(principal: Decimal, annualRate: Decimal, days: Int) -> Decimal
       static func monthlyInterest(principal: Decimal, annualRate: Decimal) -> Decimal
       static func earlyWithdrawalInterest(principal: Decimal, noTermRate: Decimal, actualDays: Int) -> Decimal

       // mục 26.4 — thuế bán chứng khoán VN 0,1% trên giá trị bán
       static func stockSellTax(sellValue: Decimal) -> Decimal

       // mục 4.1.5 — ngoại tệ
       static func fxConvertedValue(amount: Decimal, exchangeRate: Decimal) -> Decimal
       static func fxGainLoss(currentRate: Decimal, rateAtReceipt: Decimal, amount: Decimal) -> Decimal
   }
   ```
2. `Features/Transactions/TransactionFormView.swift`: form chung theo `TransactionType`, dùng cho nạp/rút/điều chỉnh.
3. `Features/Transactions/BuyStockView.swift` / `SellStockView.swift`: luồng 8.2/8.3 — bán một phần phải trừ đúng số lượng còn lại (dùng `computeCurrentQuantityAndCost` từ Sprint 1.2), tự động điền `stockSellTax` làm giá trị mặc định cho trường thuế, cho sửa tay.
4. `Features/Transactions/TransferFundsView.swift`: luồng 8.7 — trừ tài khoản nguồn, cộng tài khoản đích trong 1 transaction Postgres (dùng RPC hoặc 2 insert trong 1 batch) để không cộng trùng (`note.txt` mục 4.1.4).
5. `Features/Transactions/SavingsMaturityView.swift`: luồng 8.6 — tất toán đúng hạn/trước hạn, gọi `expectedInterestAtMaturity` hoặc `earlyWithdrawalInterest` tương ứng, cập nhật `status` của `SavingsDeposit`.
6. Tạo target `AssetTrackerTests`, viết unit test cho **toàn bộ** hàm ở `FinanceCalculator`:
   - `averageCost`: dùng đúng ví dụ số ở `note.txt` mục 4.2.5 (1.000 CP giá 24.000 + 500 CP giá 26.000 → bình quân 24.666,67).
   - `expectedInterestAtMaturity`, `monthlyInterest`: dùng ví dụ mục 4.4.3/4.4.4.
   - `stockSellTax`: 0,1% đúng giá trị bán.
   - `fxConvertedValue`, `fxGainLoss`: vài case số tròn.

### Acceptance Criteria
- [ ] Mua 2 lần 1 mã CK giá khác nhau → giá vốn bình quân đúng theo ví dụ mục 4.2.5.
- [ ] Bán một phần → số lượng còn lại và giá vốn bình quân còn lại tính đúng.
- [ ] Chuyển tiền giữa 2 tài khoản → tổng tài sản không đổi ngay sau khi chuyển.
- [ ] Toàn bộ test trong `AssetTrackerTests` pass.

### Không làm
- Chưa cần Dashboard hiển thị tổng hợp (Sprint 1.5).
- Chưa tích hợp giá tự động (Phase 2) — `currentPrice` vẫn nhập tay ở Phase 1.

---

## Sprint 1.5 — Dashboard & biểu đồ

**Mục tiêu:** tab Tổng quan với số liệu và biểu đồ.

**Phụ thuộc:** Sprint 1.4.

### Việc cần làm

1. `Core/Services/SnapshotScheduler.swift`: tạo `ValuationSnapshot` khi (a) mở app lần đầu trong ngày (so sánh `date` mới nhất trong bảng với hôm nay), hoặc (b) sau một giao dịch làm thay đổi tổng tài sản trên một ngưỡng % (ví dụ >1%) — upsert theo `date` (unique constraint đã có ở Sprint 1.1). Lưu `fx_rates_snapshot` (jsonb) chứa tỷ giá hiện tại của mọi tài khoản ngoại tệ tại thời điểm snapshot (`note.txt` mục 26.4 — không tính lại lịch sử từ tỷ giá hiện tại).
2. `Features/Dashboard/DashboardView.swift`: tổng tài sản, tài sản ròng, tổng nợ, biến động trong tháng (`note.txt` mục 6.1), các thẻ chỉ số (mục 6.2).
3. `Features/Dashboard/AllocationPieChartView.swift`: donut chart Swift Charts, dữ liệu theo nhóm tài sản (mục 6.3).
4. `Features/Dashboard/GrowthLineChartView.swift`: line chart từ `valuation_snapshots`, filter 7 ngày/1 tháng/3 tháng/6 tháng/1 năm/toàn bộ. Xử lý nội suy khi có ngày trống dữ liệu (nối thẳng điểm liền trước/sau).

### Acceptance Criteria
- [ ] Dùng app liên tục 3 ngày thật, `valuation_snapshots` có 3 dòng đúng ngày, biểu đồ tăng trưởng vẽ đúng.
- [ ] Đổi filter khoảng thời gian trên biểu đồ tăng trưởng hoạt động đúng.
- [ ] Donut chart tổng tỷ trọng = 100%.

### Không làm
- Chưa có cảnh báo nhanh (mục 6.4) — đó là Sprint 2.4/3.3.

---

## Sprint 1.6 — Bảo mật cơ bản

**Mục tiêu:** Face ID/PIN, ẩn số dư.

**Phụ thuộc:** Sprint 1.1 (không phụ thuộc UI khác, có thể làm song song với 1.3-1.5).

### Việc cần làm

1. `Core/Security/BiometricAuthManager.swift`: dùng `LocalAuthentication` (`LAContext.evaluatePolicy(.deviceOwnerAuthentication...)`), fallback mã PIN 6 số lưu trong Keychain (không lưu plaintext).
2. `Features/Security/LockScreenView.swift`: hiện khi app mở lại từ background hoặc mở lần đầu — chặn toàn bộ nội dung tới khi xác thực qua.
3. `Core/Security/PrivacyModeManager.swift`: `@AppStorage` toggle "ẩn số dư" — khi bật, mọi Text hiển thị tiền thay bằng `•••••••••` (tạo `View` modifier `.privacySensitiveAmount()` dùng lại khắp app thay vì sửa từng nơi).
4. Che nội dung trong App Switcher: dùng `UIApplication` `willResignActiveNotification` để overlay 1 view che màn hình.
5. `Features/Settings/SecuritySettingsView.swift`: bật/tắt Face ID, đổi PIN, bật/tắt ẩn số dư.

### Acceptance Criteria
- [ ] Mở app phải qua Face ID hoặc PIN mới vào được.
- [ ] Bật "ẩn số dư" → toàn bộ số tiền trên mọi tab hiện `•••••••••`.
- [ ] Vào App Switcher, nội dung tài chính bị che.

### Không làm
- Chưa mã hóa file cache SwiftData ở mức nâng cao (đủ dùng bảo vệ bằng Face ID ở tầng app cho Phase 1; mã hóa file cụ thể có thể bổ sung sau nếu cần).

---

## Sprint 1.7 — QA tổng thể Phase 1

**Mục tiêu:** kiểm thử toàn bộ tiêu chí nghiệm thu + xuất CSV.

**Phụ thuộc:** Sprint 1.1 → 1.6 xong hết.

### Việc cần làm

1. `Core/Services/CSVExportService.swift`: export toàn bộ asset + transaction ra CSV, dùng `ShareLink` (hoặc `UIActivityViewController`) để chia sẻ/lưu file.
2. Đối chiếu tiêu chí nghiệm thu `note.txt` mục 22.1-22.4 từng dòng một, ghi log kết quả (pass/fail) — sửa bug nếu có trước khi coi Phase 1 xong.
3. Nhập dữ liệu thật của chính người dùng cho cả 4 nhóm, đối chiếu thủ công (tính tay hoặc Excel) xem tổng tài sản/tài sản ròng có khớp không.

### Acceptance Criteria
- [ ] Toàn bộ mục 22.1-22.4 trong `note.txt` pass.
- [ ] Xuất CSV mở được bằng Excel/Numbers, dữ liệu khớp với trong app.
- [ ] Tổng tài sản tính bằng app khớp với tính tay/Excel cho dữ liệu thật.

### Không làm
- Không thêm tính năng mới ngoài checklist Phase 1 dù phát hiện "tiện thể làm luôn" trong lúc QA — ghi lại thành ý tưởng, đưa vào Phase phù hợp.

---

# PHASE 2 — Tự động hóa giá thị trường (API BTMC + DNSE)

## Sprint 2.1 — Hạ tầng chung: Edge Function + bảng snapshot giá

**Mục tiêu:** khung Edge Function + bảng `price_snapshots` dùng chung.

**Phụ thuộc:** Sprint 1.2 (repository layer đã có).

### Việc cần làm

1. `supabase/migrations/0002_price_snapshots.sql`:
   ```sql
   create table public.price_snapshots (
       id uuid primary key default gen_random_uuid(),
       asset_key text not null,           -- vd: 'gold_bar_sjc', mã CK 'HPG'
       asset_type text not null check (asset_type in ('gold','stock')),
       buy_price numeric,
       sell_price numeric,
       source text not null,              -- 'BTMC', 'DNSE'
       fetched_at timestamptz not null,
       created_at timestamptz not null default now()
   );

   create index idx_price_snapshots_lookup
       on public.price_snapshots (asset_type, asset_key, fetched_at desc);

   alter table public.price_snapshots enable row level security;
   create policy "allow anon read" on public.price_snapshots for select to anon using (true);
   ```
   (Chỉ cho `anon` quyền `select` — việc ghi do Edge Function dùng service_role key thực hiện, không qua client app.)
2. `supabase/functions/_shared/types.ts`: định nghĩa interface `PriceSnapshotRow { assetKey: string; assetType: "gold" | "stock"; buyPrice: number; sellPrice?: number; source: string; fetchedAt: string }`.
3. `supabase/functions/_shared/supabaseAdminClient.ts`: khởi tạo client Supabase trong Edge Function bằng `SUPABASE_SERVICE_ROLE_KEY` (biến môi trường, không phải anon key) để có quyền ghi bất chấp RLS chỉ cho phép `select` với `anon`.
4. `Data/Repositories/PriceSnapshotRepository.swift`: hàm `latestPrice(assetType:assetKey:) async throws -> PriceSnapshot?` — lấy dòng mới nhất theo `asset_key`.
5. Sửa `AssetRepository`/ViewModel Chứng khoán & Vàng (Sprint 1.3): khi hiển thị, ưu tiên đọc `PriceSnapshotRepository.latestPrice` để set `currentPrice`; nếu không có snapshot (chưa chạy Phase 2 hoặc lỗi), dùng giá trị nhập tay đã lưu trong `assets.current_price` làm fallback.
6. UI: thêm dòng nhỏ "Nguồn: BTMC/DNSE · cập nhật lúc HH:mm" cạnh giá tự động (`note.txt` mục 13.2); nếu đang dùng fallback nhập tay thì hiện "Giá nhập tay".

### Acceptance Criteria
- [ ] Insert thử 1 dòng `price_snapshots` bằng service role key qua `supabase functions serve` local, app đọc và hiển thị đúng giá + nhãn nguồn/thời gian.
- [ ] Client dùng anon key **không insert được** vào `price_snapshots` (RLS chỉ cho select) — verify bằng thử insert từ app và xác nhận bị từ chối.

### Không làm
- Chưa gọi BTMC/DNSE thật (Sprint 2.2/2.3).

---

## Sprint 2.2 — Tích hợp API giá vàng BTMC

**Mục tiêu:** cron job lấy giá vàng tự động.

**Phụ thuộc:** Sprint 2.1.

**Thông tin kỹ thuật đã xác minh thực tế (curl trực tiếp ngày 11/07/2026):**

```text
Endpoint: GET http://api.btmc.vn/api/BTMCAPI/getpricebtmc?key={API_KEY}
Auth: key nhúng trong query string, không có OAuth/HMAC
Response: JSON thật (trang tài liệu BTMC mô tả là XML nhưng response thực tế là JSON)

Field có suffix số thay đổi theo "@row" của từng phần tử (@n_1, @n_2, @n_3...),
KHÔNG cố định tên field — phải parse động theo giá trị "@row".

{
  "DataList": {
    "Data": [
      {
        "@row": "9",
        "@n_9": "VÀNG MIẾNG SJC (Vàng SJC)",
        "@k_9": "24k",
        "@h_9": "999.9",
        "@pb_9": "14500000",   // giá công ty MUA VÀO — dùng số này để định giá tài sản đang giữ (mục 4.3.4)
        "@ps_9": "14990000",   // giá công ty BÁN RA
        "@pt_9": "4120",       // ý nghĩa chưa xác định rõ — KHÔNG dùng, chỉ log lại
        "@d_9": "11/07/2026 08:58"
      }
    ]
  }
}
```

### Việc cần làm

1. **[THỦ CÔNG]** `supabase secrets set BTMC_API_KEY=3kd8ub1llcg9t45hnoh8hmn7t5kc2v` (key public đã có sẵn trong tài liệu BTMC).
2. `supabase/functions/fetch-gold-price/index.ts`:
   ```ts
   import { supabaseAdmin } from "../_shared/supabaseAdminClient.ts";

   const BTMC_URL = `http://api.btmc.vn/api/BTMCAPI/getpricebtmc?key=${Deno.env.get("BTMC_API_KEY")}`;

   const NAME_TO_ASSET_KEY: Record<string, string> = {
     "VÀNG MIẾNG SJC (Vàng SJC)": "gold_bar_sjc",
     "NHẪN TRÒN TRƠN (Vàng Rồng Thăng Long)": "gold_ring_9999",
     "VÀNG THƯƠNG HIỆU DOJI, PNJ, PHÚ QUÝ... (Vàng Đối Tác)": "gold_bar_other_brand",
     "TRANG SỨC VÀNG RỒNG THĂNG LONG 999.9 (Vàng BTMC)": "gold_jewelry",
     "TRANG SỨC VÀNG RỒNG THĂNG LONG 99.9 (Vàng BTMC)": "gold_jewelry",
   };
   // Lưu ý: đối chiếu lại tên chính xác bằng cách gọi thử endpoint tại thời điểm code,
   // vì BTMC có thể đổi cách đặt tên sản phẩm.

   Deno.serve(async () => {
     const res = await fetch(BTMC_URL);
     const json = await res.json();
     const rows: Record<string, string>[] = json?.DataList?.Data ?? [];

     const snapshots = rows
       .map((row) => {
         const idx = row["@row"];
         const name = row[`@n_${idx}`];
         const assetKey = NAME_TO_ASSET_KEY[name];
         if (!assetKey) return null; // bỏ qua sản phẩm chưa map (vd: bạc)
         return {
           asset_key: assetKey,
           asset_type: "gold",
           buy_price: Number(row[`@pb_${idx}`]),
           sell_price: Number(row[`@ps_${idx}`]),
           source: "BTMC",
           fetched_at: new Date().toISOString(),
         };
       })
       .filter(Boolean);

     if (snapshots.length > 0) {
       await supabaseAdmin.from("price_snapshots").insert(snapshots);
     }
     return new Response(JSON.stringify({ inserted: snapshots.length }), { status: 200 });
   });
   ```
3. Lên lịch chạy Edge Function mỗi 30-60 phút bằng Supabase Scheduled Triggers (Dashboard → Edge Functions → Cron) hoặc `pg_cron` gọi `net.http_post` tới function URL.
4. Fallback trong app (đã có từ Sprint 2.1): nếu không có snapshot mới trong X giờ, tự động hiện lại giá nhập tay + cảnh báo nhỏ "chưa cập nhật giá tự động".

### Acceptance Criteria
- [ ] Gọi function thủ công (`supabase functions serve` rồi `curl`) → có dòng mới trong `price_snapshots` với `asset_type = 'gold'`.
- [ ] Tài sản Vàng thật (SJC hoặc nhẫn 9999 đang có) trong app tự động hiện giá theo BTMC, đúng bằng `pb` (giá mua vào) tại thời điểm gọi.
- [ ] Cron chạy tự động sau khi deploy, không cần gọi tay.

### Không làm
- Không dùng field `@pt` (world price) — chưa xác định rõ ý nghĩa, không tạo tính năng dựa trên nó.
- Không hỗ trợ các sản phẩm Bạc trong API (ngoài phạm vi `AssetCategory` hiện tại).

---

## Sprint 2.3 — Tích hợp API DNSE (chứng khoán)

**Mục tiêu:** lấy giá chứng khoán tự động cho các mã đang nắm giữ.

**Phụ thuộc:** Sprint 2.1. Đây là sprint phức tạp nhất kỹ thuật trong Phase 2.

**[THỦ CÔNG] trước khi bắt đầu:** lấy API Key + API Secret từ DNSE Developer Portal (đã có tài khoản DNSE).

**Cơ chế xác thực DNSE (khác hẳn BTMC — không phải key đơn giản):**

```text
Mỗi request REST cần 3 header: X-Api-Key, X-Signature, Date

Cách tạo X-Signature:
1. Chuỗi ký (signing string):
   (request-target): [method] [path]
   date: [RFC1123 date]
   nonce: [UUID4 hex]
2. HMAC-SHA256(chuỗi ký, API_SECRET) → Base64 → URL-encode riêng các ký tự + / =
3. Header: Signature keyId="{API_KEY}",algorithm="hmac-sha256",
   headers="(request-target) date",signature="{ENCODED}",nonce="{NONCE}"

Ràng buộc: Date lệch server DNSE không quá ±1 phút; mỗi request 1 Date + Nonce mới.
OTP/trading-token CHỈ cần cho đặt lệnh — ứng dụng này chỉ đọc giá, không cần.
```

**Bảo mật bắt buộc:** `DNSE_API_SECRET` **chỉ tồn tại trong biến môi trường của Edge Function**, không bao giờ xuất hiện trong code app iOS hay git repo công khai — vì secret dùng để ký request, lộ ra nguy hiểm hơn cả service_role key.

### Việc cần làm

1. **[THỦ CÔNG]** Task khám phá bắt buộc trước khi code: dùng Postman/curl với API Key + Secret thật để xác nhận chính xác endpoint market-data trả giá đóng cửa/giá khớp lệnh theo mã CK (tài liệu công khai DNSE không liệt kê đầy đủ field response) — ghi lại path và response mẫu thật vào comment đầu file `fetch-stock-price/index.ts` trước khi code phần parse.
2. **[THỦ CÔNG]** `supabase secrets set DNSE_API_KEY=... DNSE_API_SECRET=...`.
3. `supabase/functions/_shared/dnseSignature.ts`:
   ```ts
   export async function signDnseRequest(method: string, path: string) {
     const apiKey = Deno.env.get("DNSE_API_KEY")!;
     const apiSecret = Deno.env.get("DNSE_API_SECRET")!;
     const date = new Date().toUTCString();
     const nonce = crypto.randomUUID().replace(/-/g, "");
     const signingString = `(request-target): ${method.toLowerCase()} ${path}\ndate: ${date}\nnonce: ${nonce}`;

     const key = await crypto.subtle.importKey(
       "raw",
       new TextEncoder().encode(apiSecret),
       { name: "HMAC", hash: "SHA-256" },
       false,
       ["sign"],
     );
     const sigBuffer = await crypto.subtle.sign("HMAC", key, new TextEncoder().encode(signingString));
     const sigBase64 = btoa(String.fromCharCode(...new Uint8Array(sigBuffer)));
     const encodedSig = encodeURIComponent(sigBase64);

     const signatureHeader =
       `Signature keyId="${apiKey}",algorithm="hmac-sha256",` +
       `headers="(request-target) date",signature="${encodedSig}",nonce="${nonce}"`;

     return { "X-Api-Key": apiKey, "X-Signature": signatureHeader, Date: date };
   }
   ```
4. `supabase/functions/fetch-stock-price/index.ts`:
   - Đọc danh sách mã CK duy nhất đang có trong bảng `assets` (`category = 'stock'`) bằng `supabaseAdmin`.
   - Xử lý phiên giao dịch: chỉ gọi API trong giờ HOSE/HNX/UPCOM (9:00-11:30, 13:00-15:00 giờ VN các ngày thường) — ngoài giờ, function trả về sớm không gọi DNSE.
   - Với mỗi mã, gọi endpoint market-data (path xác nhận ở bước 1) kèm header từ `signDnseRequest`, parse giá đóng cửa/khớp lệnh, insert vào `price_snapshots` với `asset_type = 'stock'`, `asset_key = <mã CK>`, `source = 'DNSE'`.
5. Lên lịch chạy mỗi 5-15 phút trong giờ giao dịch (Supabase Scheduled Triggers).
6. UI: badge "Thị trường đang mở/đã đóng cửa" cạnh giá CK tự động, dựa vào khung giờ giao dịch ở trên.

### Acceptance Criteria
- [ ] Gọi function thủ công trong giờ giao dịch → có dòng mới `price_snapshots` với `asset_type = 'stock'` cho đúng mã CK đang nắm giữ.
- [ ] Gọi ngoài giờ giao dịch → function không gọi DNSE, trả về sớm, không tạo dòng rác.
- [ ] Mã CK thật đang giữ tự động cập nhật giá trong giờ giao dịch, lãi/lỗ tính lại theo giá mới.
- [ ] Xác nhận bằng cách đọc code: `DNSE_API_SECRET` không xuất hiện ở bất kỳ file nào trong `AssetTracker/` (chỉ trong `supabase/functions`).

### Không làm
- Không implement luồng OTP/trading-token — ứng dụng không đặt lệnh.
- Không gọi API ngoài giờ giao dịch.

---

## Sprint 2.4 — Hoàn thiện trải nghiệm giá tự động

**Mục tiêu:** cảnh báo giá mục tiêu + widget.

**Phụ thuộc:** Sprint 2.2, 2.3.

### Việc cần làm

1. `Core/Services/PriceAlertService.swift`: người dùng đặt "giá mục tiêu" cho 1 Asset (cột mới `target_price numeric` — thêm qua migration nhỏ nếu chưa có); khi `PriceSnapshotRepository` phát hiện giá mới vượt ngưỡng, bắn Local Notification (`note.txt` mục 11.4).
2. Nhắc khi Edge Function lỗi liên tục nhiều ngày: kiểm tra `fetched_at` mới nhất trong `price_snapshots` theo `asset_type`, nếu quá X giờ so với hiện tại thì nhắc (`note.txt` mục 11.2, thích ứng lại vì giờ là lỗi hệ thống chứ không phải quên nhập tay).
3. Tạo target `AssetTrackerWidget` (WidgetKit extension): hiển thị tổng tài sản + tài sản ròng, đọc qua App Group + `UserDefaults(suiteName:)` được app chính ghi mỗi lần tính lại Dashboard.
4. (Tùy chọn) Nếu sau này tìm được API tỷ giá phù hợp, thêm provider tỷ giá tự động vào Edge Function dùng chung theo đúng khuôn mẫu `fetch-gold-price`/`fetch-stock-price` — trước mắt tài khoản ngoại tệ (mục 4.1.5) dùng tỷ giá nhập tay.

### Acceptance Criteria
- [ ] Đặt giá mục tiêu cho 1 mã CK/vàng, khi `price_snapshots` có giá vượt ngưỡng → nhận được Local Notification.
- [ ] Widget trên Home Screen hiện đúng tổng tài sản/tài sản ròng, tự cập nhật sau khi mở app.

### Không làm
- Chưa cần widget tương tác (chỉ hiển thị, không cần deep link/interactive widget ở Phase 2).

---

# PHASE 3 — Mở rộng loại tài sản + báo cáo/nhắc nhở đầy đủ

> Ngoại tệ không có sprint riêng ở đây — đã xử lý trong Phase 1 (Sprint 1.3/1.4) vì là 1 phần của tài khoản Tiền mặt (`note.txt` mục 4.1.5).

## Sprint 3.1 — Nợ phải trả

**Mục tiêu:** CRUD đầy đủ cho 3 cơ chế nợ khác nhau (vay có kỳ hạn / thẻ tín dụng / khoản phải trả khác — `note.txt` mục 5), lịch trả nợ tự sinh, cảnh báo trả tối thiểu thẻ tín dụng, báo cáo nợ.

**Phụ thuộc:** Phase 1 xong (bảng `liabilities` đã tồn tại từ Sprint 1.1 ở dạng đơn giản — sprint này mở rộng schema thêm).

### Việc cần làm

1. `supabase/migrations/0003_expand_liabilities.sql`:
```sql
alter table public.liabilities
    add column liability_type text not null default 'other_payable' check (liability_type in (
        'mortgage_loan','car_loan','consumer_loan','unsecured_loan',
        'family_loan','installment_plan','credit_card','other_payable'
    )),
    add column currency text not null default 'VND',
    add column interest_rate_type text check (interest_rate_type in ('fixed','floating')),
    add column fixed_rate_end_date date,
    add column repayment_method text check (repayment_method in ('equal_principal','annuity')),
    add column term_in_months int,
    add column early_repayment_fee_rate numeric,
    add column grace_period_months int,
    add column credit_limit numeric,
    add column statement_day int check (statement_day between 1 and 31),
    add column payment_due_day int check (payment_due_day between 1 and 31),
    add column interest_free_days int,
    add column min_payment_rate numeric,
    add column min_payment_fixed_amount numeric,
    add column annual_fee numeric,
    add column late_fee numeric,
    add column last_statement_balance numeric,
    add column last_statement_date date;

alter table public.asset_transactions
    add column liability_id uuid references public.liabilities(id),
    add column payment_type text check (payment_type in ('full','minimum','partial'));
```
   (`liability_id` cho phép giao dịch loại `repayment` gắn với 1 khoản nợ, song song với `asset_id` đã có cho tài sản — 1 giao dịch chỉ nên gắn 1 trong 2, không cả hai.)
2. Cập nhật `Core/Models/Enums.swift`: thêm `LiabilityType`, `InterestRateType`, `RepaymentMethod` đúng raw value ở migration trên (theo `note.txt` mục 14.5).
3. Cập nhật `Core/Models/Liability.swift` theo struct đầy đủ ở `note.txt` mục 14.5.
4. `Core/Services/FinanceCalculator.swift` — thêm:
   ```swift
   struct AmortizationRow {
       let periodIndex: Int
       let dueDate: Date
       let principalDue: Decimal
       let interestDue: Decimal
       let totalDue: Decimal
       let remainingBalance: Decimal
   }

   extension FinanceCalculator {
       // Nhóm A — mục 5.2.2
       static func equalPrincipalSchedule(principal: Decimal, annualRate: Decimal, termInMonths: Int, startDate: Date) -> [AmortizationRow]
       static func annuityPayment(remainingBalance: Decimal, annualRate: Decimal, remainingPeriods: Int) -> Decimal
       static func annuitySchedule(principal: Decimal, annualRate: Decimal, termInMonths: Int, startDate: Date) -> [AmortizationRow]
       static func earlyRepaymentFee(prepaidAmount: Decimal, feeRate: Decimal) -> Decimal

       // Nhóm B — mục 5.3.3
       static func creditCardMinimumPayment(currentBalance: Decimal, minRate: Decimal, minFixedAmount: Decimal) -> Decimal
       static func creditUtilization(currentBalance: Decimal, creditLimit: Decimal) -> Decimal
       static func estimatedInterestIfUnderpaid(balance: Decimal, annualRate: Decimal, days: Int) -> Decimal
   }
   ```
   Unit test bắt buộc cho toàn bộ hàm trên trong `AssetTrackerTests`, đối chiếu số với ví dụ ở `note.txt` mục 5.2.2/5.3.3.
5. `Features/Liabilities/LiabilityListView.swift`: danh sách nhóm theo 3 nhóm (mục 5.1), mỗi khoản hiện dư nợ hiện tại + ngày đến hạn gần nhất.
6. `Features/Liabilities/TermLoanFormView.swift`: form Nhóm A — chọn phương thức trả (Gốc đều/Trả đều); app tự sinh lịch trả dự kiến ngay sau khi lưu bằng `equalPrincipalSchedule`/`annuitySchedule`.
7. `Features/Liabilities/AmortizationScheduleView.swift`: bảng lịch trả nợ (kỳ số, ngày đến hạn, gốc, lãi, tổng, dư nợ còn lại), đánh dấu kỳ đã trả/trễ hạn/chưa trả dựa trên `asset_transactions` loại `repayment` đã ghi cho `liability_id` tương ứng.
8. `Features/Liabilities/CreditCardFormView.swift`: form Nhóm B — hạn mức, ngày sao kê, ngày đến hạn, lãi suất, tỷ lệ tối thiểu, phí thường niên/trả chậm.
9. `Features/Liabilities/CreditCardStatementUpdateView.swift`: cập nhật `current_balance`/`last_statement_balance` mỗi kỳ sao kê mới (nhập tay theo sao kê ngân hàng gửi — **không** tính lại từ transaction log, đúng ngoại lệ có chủ đích ở mục 5.3.1).
10. `Features/Liabilities/OtherPayableFormView.swift`: form Nhóm C, tối giản theo mục 5.4.
11. `Features/Liabilities/LiabilityRepaymentView.swift`: ghi nhận thanh toán — với thẻ tín dụng, bắt buộc chọn 1 trong 3: "Trả toàn bộ" / "Trả tối thiểu" / "Trả số khác"; nếu chọn khác "Trả toàn bộ", **hiện banner cảnh báo lãi hồi tố** (mục 5.3.1) trước khi cho xác nhận. Lưu `payment_type` tương ứng vào `asset_transactions`.
12. `LiabilityViewModel.swift`.
13. Cập nhật `DashboardView` (Sprint 1.5): tài sản ròng = tổng tài sản − tổng nợ (mục 3.3) hiển thị xuyên suốt thay vì chỉ tổng tài sản.
14. `Core/Services/ReminderScheduler.swift` (khởi tạo ở đây, mở rộng thêm ở Sprint 3.3):
    - Nhắc trước ngày đến hạn từng kỳ vay Nhóm A (`next_payment_date`).
    - Nhắc trước ngày đến hạn thanh toán thẻ tín dụng (`payment_due_day`).
    - Cảnh báo tỷ lệ sử dụng hạn mức vượt ngưỡng cấu hình.
    - Cảnh báo khi phát hiện ≥ 3 kỳ liên tiếp `payment_type = 'minimum'` cho cùng 1 thẻ tín dụng.
15. `Features/Reports/DebtReportView.swift`: tổng nợ theo nhóm, nợ ngắn/dài hạn, khoản phải trả tháng này, tỷ lệ nợ/tài sản, tỷ lệ nợ/tài sản ròng, tổng lãi đã trả, tỷ lệ sử dụng hạn mức trung bình (mục 5.5).

### Acceptance Criteria
- [ ] Thêm 1 khoản vay có kỳ hạn thật (Nhóm A) — app sinh đúng lịch trả nợ, đối chiếu tay vài kỳ đầu khớp công thức mục 5.2.2.
- [ ] Thêm 1 thẻ tín dụng thật (Nhóm B), cập nhật dư nợ theo sao kê gần nhất, ghi nhận thử "trả tối thiểu" → thấy đúng cảnh báo lãi hồi tố trước khi xác nhận.
- [ ] Tỷ lệ sử dụng hạn mức và thanh toán tối thiểu tính đúng theo công thức mục 5.3.3.
- [ ] Dashboard cập nhật đúng tài sản ròng sau khi thêm nợ.
- [ ] Nhận Local Notification đúng ngày trước hạn thanh toán (cả vay và thẻ tín dụng).
- [ ] Giả lập 3 kỳ liên tiếp `payment_type = 'minimum'` → nhận cảnh báo nợ xấu tiềm ẩn.
- [ ] Toàn bộ unit test `FinanceCalculator` cho Nhóm A/B pass.

### Không làm
- Không ghi từng giao dịch quẹt thẻ chi tiết (quyết định phạm vi ở mục 5.3.1) — chỉ cập nhật dư nợ theo kỳ sao kê.
- Chưa làm nhắc nhở nhóm khác (đáo hạn tiết kiệm/giá, cảnh báo tỷ trọng) — đó là Sprint 3.3, gộp chung `ReminderScheduler`.
- Không tự động trừ tiền/thanh toán hộ — chỉ ghi nhận sau khi người dùng đã thanh toán thật ở ngân hàng.

---

## Sprint 3.2 — Bất động sản & tài sản khác

**Mục tiêu:** mở rộng nhóm tài sản khác (mục 4.6).

**Phụ thuộc:** Sprint 3.1 (dùng chung `ReminderScheduler` vừa tạo).

### Việc cần làm

1. `supabase/migrations/0004_extend_asset_category.sql`:
   ```sql
   alter table public.assets drop constraint assets_category_check;
   alter table public.assets add constraint assets_category_check check (category in (
       'stock','fund_certificate','etf','listed_bond','warrant',
       'foreign_stock','open_end_fund','other_security',
       'gold_bar_sjc','gold_ring_9999','gold_bar_other_brand','gold_jewelry',
       'gold_24k','gold_18k','gold_14k','gold_international','other_gold',
       'real_estate','car','motorbike','non_listed_bond','crypto',
       'insurance_cash_value','loan_receivable','business_equity',
       'collectible','digital_asset','rental_asset'
   ));
   ```
2. Cập nhật `AssetCategory` enum (Swift) thêm các case mới tương ứng.
3. `Features/Assets/Other/OtherAssetListView.swift`, `OtherAssetFormView.swift`: trường chung theo mục 4.6.1 (tên, loại, ngày mua, giá mua, giá trị hiện tại, nguồn định giá, thu nhập tạo ra, chi phí liên quan, nơi lưu giữ, tài liệu, ghi chú).
4. Mở rộng `ReminderScheduler`: nhắc cập nhật giá bất động sản sau 90 ngày chưa cập nhật (mục 11.2).

### Acceptance Criteria
- [ ] Thêm được 1 tài sản Bất động sản/tài sản khác thật, hiện đúng trong Dashboard và tổng tài sản.
- [ ] Sau 90 ngày mô phỏng (chỉnh giờ hệ thống test hoặc mock date), nhận nhắc cập nhật giá.

### Không làm
- Không tích hợp định giá tự động cho nhóm này (không có API phù hợp) — luôn nhập tay.

---

## Sprint 3.3 — Báo cáo & nhắc nhở đầy đủ

**Mục tiêu:** hoàn thiện toàn bộ mục 10 và 11 của `note.txt`.

**Phụ thuộc:** Sprint 3.1, 3.2.

### Việc cần làm

1. `Features/Reports/`: `NetWorthReportView`, `ProfitLossReportView`, `AllocationReportView`, `MaturityReportView`, `PassiveIncomeReportView` — theo đúng nội dung mục 10.1-10.5.
2. `Core/Services/PDFReportGenerator.swift`: dùng `UIGraphicsPDFRenderer` xuất báo cáo tổng tài sản ra PDF (mục 17.2).
3. Hoàn thiện `ReminderScheduler` với toàn bộ mục 11 còn thiếu: nhắc đáo hạn tiết kiệm 30/14/7/1 ngày (11.1), nhắc cập nhật giá CK/ngoại tệ (11.2, phần còn lại ngoài vàng/BĐS đã làm), cảnh báo tỷ trọng (11.3 — vượt ngưỡng % cấu hình được trong Settings), cảnh báo lãi/lỗ (11.4, phần chưa làm ở Sprint 2.4).

### Acceptance Criteria
- [ ] Mỗi báo cáo ở mục 10 hiển thị số liệu đúng với dữ liệu thật đang có.
- [ ] Xuất PDF mở được, số liệu khớp trong app.
- [ ] Toàn bộ loại nhắc nhở ở mục 11 bắn đúng thời điểm cấu hình (test bằng cách set ngày đáo hạn gần, hoặc mock `Date()`).

### Không làm
- Không thêm loại báo cáo ngoài mục 10.

---

# PHASE 4 — Chia sẻ dữ liệu với người thân

> Theo mô hình no-auth đã chốt ở `note.txt` mục 28.3 — có thể làm xen kẽ bất cứ lúc nào sau Phase 1, không cần đợi Phase 2/3.

## Sprint 4.1 — QA đồng bộ đa thiết bị

**Mục tiêu:** xác nhận nhiều thiết bị dùng chung 1 Supabase project không lệch dữ liệu.

**Phụ thuộc:** Phase 1 (đặc biệt Sprint 1.2 — cơ chế tính lại từ transaction log).

### Việc cần làm

1. `supabase/migrations/0005_add_edited_by.sql`:
   ```sql
   alter table public.asset_transactions add column edited_by text;
   alter table public.asset_accounts add column edited_by text;
   alter table public.savings_deposits add column edited_by text;
   alter table public.liabilities add column edited_by text;
   ```
2. `Features/Settings/DisplayNameSettingView.swift`: cho người dùng đặt tên hiển thị cục bộ (`@AppStorage("displayName")`, ví dụ "Chồng"/"Vợ") — nhãn thuần hiển thị, không phải xác thực (`note.txt` mục 28.3). Mọi insert/update transaction/account gắn `edited_by` = tên này.
3. **[THỦ CÔNG]** Cài build lên 1 thiết bị thứ hai (hoặc Simulator thứ hai), trỏ cùng `Secrets.swift` (cùng Supabase project).
4. **[THỦ CÔNG]** Test tay: ghi đồng thời từ 2 thiết bị (vd: cả hai cùng thêm 1 giao dịch mua CK trong vòng vài giây), xác nhận `computeCurrentQuantityAndCost` (Sprint 1.2) tính đúng tổng hợp cả 2 giao dịch, không mất dữ liệu, không lệch số lượng.

### Acceptance Criteria
- [ ] 2 thiết bị cùng thấy dữ liệu chung real-time (hoặc sau khi pull-to-refresh).
- [ ] Ghi đồng thời từ 2 máy không làm sai số lượng/giá vốn tính lại.
- [ ] Cột `edited_by` hiển thị đúng người vừa thêm giao dịch trong lịch sử giao dịch.

### Không làm
- Không xây cơ chế phân quyền owner/viewer ở tầng backend (đã xác nhận không khả thi với no-auth, `note.txt` mục 28.3) — chỉ làm UI-only ở Sprint 4.3.

---

## Sprint 4.2 — Phân phối bản build

**Mục tiêu:** đưa app lên máy người thân.

**Phụ thuộc:** Sprint 4.1.

### Việc cần làm (chủ yếu thủ công, không phải code)

1. **[THỦ CÔNG]** Quyết định: đăng ký Apple Developer Program ($99/năm) nếu muốn dùng TestFlight (`note.txt` mục 27.4) — không bắt buộc nếu vẫn cài trực tiếp qua Xcode/cáp USB được.
2. **[THỦ CÔNG]** Nếu dùng TestFlight: tạo App Store Connect record (không cần public listing), mời người thân qua email, theo dõi build hết hạn 90 ngày để renew.
3. Code: đảm bảo `Secrets.swift` không bị thiếu khi build Release/TestFlight (kiểm tra build script không phụ thuộc file gitignored bị thiếu trên máy CI nếu dùng Xcode Cloud).

### Acceptance Criteria
- [ ] Người thân cài được app (qua TestFlight hoặc cáp USB trực tiếp).

### Không làm
- Không public app lên App Store công khai (đúng định hướng phi thương mại, `note.txt` mục 27).

---

## Sprint 4.3 — Tinh chỉnh trải nghiệm dùng chung

**Mục tiêu:** giảm rủi ro sửa nhầm dữ liệu khi nhiều người cùng dùng.

**Phụ thuộc:** Sprint 4.1.

### Việc cần làm

1. `Features/Settings/`: công tắc "Chế độ chỉ xem" cục bộ (`@AppStorage`, chỉ ẩn nút Thêm/Sửa/Xóa trên UI của thiết bị đó — không phải bảo mật thật, đúng đánh đổi đã ghi ở `note.txt` mục 28.3).
2. (Tùy chọn) Local Notification khi phát hiện giao dịch giá trị lớn (ngưỡng cấu hình được) do người khác (`edited_by` ≠ tên hiển thị của mình) vừa thêm — polling định kỳ hoặc Supabase Realtime subscription.

### Acceptance Criteria
- [ ] Bật "Chế độ chỉ xem" → không còn thấy nút Thêm/Sửa/Xóa trên thiết bị đó, nhưng vẫn xem đầy đủ dữ liệu.

### Không làm
- Không enforce chế độ chỉ xem ở tầng backend/RLS — chỉ UI, đúng giới hạn đã biết trước.

---

# PHASE 5 — Thông minh hóa

> Nên làm sau cùng — cần vài tháng dữ liệu lịch sử thật từ `valuation_snapshots` mới có gì để phân tích có ý nghĩa. Nếu bắt tay vào Phase 5 mà dữ liệu lịch sử còn quá ít (dưới ~2 tháng), cân nhắc lùi lại thay vì code trước.

## Sprint 5.1 — Báo cáo tóm tắt tự động bằng AI

**Mục tiêu:** tóm tắt biến động tài sản bằng AI.

**Phụ thuộc:** Phase 1 (cần đủ `valuation_snapshots` để tóm tắt có ý nghĩa).

### Việc cần làm

1. `supabase/functions/generate-ai-summary/index.ts`: đọc `valuation_snapshots` + `asset_transactions` gần đây, gọi Claude API (Anthropic — dùng `ANTHROPIC_API_KEY` secret riêng, xem skill `claude-api` nếu cần chi tiết model/pricing), trả về đoạn tóm tắt text theo mẫu `note.txt` mục 18.1.
2. `Features/Dashboard/AISummaryCardView.swift`: hiện đoạn tóm tắt trên Dashboard, kèm **disclaimer cố định trong UI** (không chỉ tài liệu nội bộ): "Đây là tóm tắt tự động, không phải tư vấn đầu tư" (`note.txt` mục 18.3, 26.5).

### Acceptance Criteria
- [ ] Dashboard hiện được 1 đoạn tóm tắt đúng dữ liệu thật gần đây (vd: "tăng X triệu tháng này, chủ yếu từ...").
- [ ] Disclaimer luôn hiển thị cùng lúc với tóm tắt, không thể ẩn vĩnh viễn.

### Không làm
- AI không được sinh ra khuyến nghị mua/bán cụ thể — nếu response từ Claude chứa gợi ý kiểu "nên mua/bán", cắt bỏ đoạn đó trước khi hiển thị (thêm kiểm tra hậu xử lý đơn giản, hoặc siết prompt hệ thống rõ ràng "chỉ tóm tắt, không tư vấn").

---

## Sprint 5.2 — Cảnh báo tập trung/thanh khoản

**Mục tiêu:** cảnh báo mất cân đối tỷ trọng.

**Phụ thuộc:** Sprint 3.3 (dùng chung `ReminderScheduler`/cấu hình ngưỡng).

### Việc cần làm

1. `Core/Services/ConcentrationAnalyzer.swift`: tính % 1 mã CK/1 loại tài sản trên tổng tài sản, so với ngưỡng cấu hình trong Settings (mục 11.3), bắn cảnh báo qua `ReminderScheduler` đã có.
2. Thêm chỉ số "tài sản thanh khoản có thể chuyển thành tiền ngay" trên Dashboard (tổng tiền mặt + tài khoản thanh toán, không tính tiết kiệm chưa đáo hạn/BĐS).

### Acceptance Criteria
- [ ] Danh mục có 1 mã CK vượt ngưỡng cấu hình (vd: 20%) → nhận cảnh báo đúng.
- [ ] Chỉ số tài sản thanh khoản hiển thị đúng, không tính nhầm tiết kiệm/BĐS vào đó.

### Không làm
- Không tự động bán/tái cân bằng — chỉ cảnh báo.

---

## Sprint 5.3 — Mô phỏng mục tiêu tài chính

**Mục tiêu:** công cụ "what-if" và dự báo dòng tiền.

**Phụ thuộc:** Sprint 5.1, 5.2.

### Việc cần làm

1. `Features/Simulation/WhatIfSimulatorView.swift`: nhập kịch bản kiểu "nếu cổ phiếu giảm X% thì tài sản ròng còn bao nhiêu" (mục 18.2) — tính lại tài sản ròng giả định dựa trên % thay đổi áp lên nhóm Chứng khoán, không sửa dữ liệu thật.
2. `Core/Services/CashFlowForecastService.swift`: dự báo dòng tiền dựa trên tiết kiệm sắp đáo hạn + lãi/cổ tức dự kiến đã biết (không dự đoán giá thị trường tương lai).
3. Gợi ý tái cân bằng: chỉ hiển thị thông tin (vd: "Vàng đang chiếm 35%, cao hơn mức bạn đặt 30%") — không tự đặt lệnh, không khuyến nghị mã cụ thể (`note.txt` mục 18.3).

### Acceptance Criteria
- [ ] Nhập kịch bản giảm 10% cổ phiếu → tài sản ròng giả định hiển thị đúng, dữ liệu thật không đổi.
- [ ] Dự báo dòng tiền liệt kê đúng các khoản tiết kiệm đáo hạn trong khoảng thời gian chọn.

### Không làm
- Không dự đoán giá tương lai của thị trường — chỉ dựa trên số liệu đã biết (lãi suất, ngày đáo hạn) và kịch bản người dùng tự nhập.

---

## Nhật ký thực thi Codex

### 11/07/2026 — Sprint 1.1 (đã bắt đầu)

Đã làm:

- Khởi tạo Git repository và thêm `.gitignore` cho secrets, Xcode/SwiftPM build artifacts, `.env` và Supabase local state.
- Tạo project `AssetTracker/AssetTracker.xcodeproj`, target iOS 17+, cấu hình SwiftUI App và Swift Package `supabase-swift` (từ phiên bản 2.0.0).
- Tạo `AssetTrackerApp.swift` với `TabView` gồm 5 tab: Tổng quan, Tài sản, Giao dịch, Báo cáo, Cài đặt.
- Tạo `Secrets.example.swift`, bản `Secrets.swift` local được gitignore, và `SupabaseClientProvider.swift`.
- Tạo `supabase/config.toml` ở chế độ không dùng Supabase Auth.
- Tạo migration `0001_init_schema.sql` gồm đủ 6 bảng, khóa ngoại, `numeric` cho tiền/số lượng, CHECK constraints, bật RLS và policy đọc/ghi cho role `anon`.
- Kiểm tra tĩnh xác nhận migration có đủ 6 lệnh tạo bảng, RLS/policy; xác nhận `Secrets.swift` đang được Git bỏ qua.

Chưa thể xác nhận / cần thực hiện thủ công:

- Chưa điền Project URL và anon key thật vì chưa được cung cấp; hiện `Secrets.swift` vẫn dùng placeholder.
- Chưa chạy `supabase db push` vì máy chưa cài Supabase CLI và chưa link Supabase project.
- Chưa build/chạy iOS Simulator vì môi trường hiện tại là Windows, không có Xcode/Swift toolchain.
- Chưa thực hiện test insert thật vào `asset_accounts`; bước này phụ thuộc Supabase project thật và app chạy trên macOS.

### 11/07/2026 — Cập nhật kết nối Supabase

Đã làm:

- Điền Project URL và publishable key thật vào `AssetTracker/AssetTracker/Config/Secrets.swift`; file này vẫn được `.gitignore` bảo vệ và không xuất hiện trong danh sách file theo dõi của Git.
- Gọi thử Supabase REST API bằng cấu hình local. Endpoint phản hồi được và key được chấp nhận.

Trạng thái migration:

- REST API trả về `PGRST205`: chưa tìm thấy bảng `public.asset_accounts` trong schema cache. Điều này xác nhận migration `supabase/migrations/0001_init_schema.sql` chưa được áp dụng lên project.
- Publishable key không có quyền tạo schema. Cần chạy migration bằng Supabase Dashboard SQL Editor, hoặc đăng nhập/link Supabase CLI bằng quyền quản trị rồi chạy `supabase db push`.

### 11/07/2026 — Hoàn tất phần Supabase của Sprint 1.1

Đã làm:

- Dùng kết nối Postgres remote để chạy `supabase db push`; migration `0001_init_schema.sql` đã được áp dụng thành công.
- Kiểm tra REST API đọc `asset_accounts` thành công (`HTTP 200`).
- Kiểm tra policy RLS role `anon` bằng cách thêm một tài khoản thử (`HTTP 201`) và xóa bản ghi đó ngay sau khi xác nhận (`HTTP 204`). Không để lại dữ liệu debug.
- Chuỗi kết nối Postgres và database password không được ghi vào bất kỳ file nào trong repository.

Kết quả:

- Phần Supabase trong Acceptance Criteria Sprint 1.1 đã đạt: đủ schema remote và role `anon` có thể đọc/ghi.
- Phần build/chạy 5 tab trên iOS Simulator vẫn cần xác nhận bằng Xcode trên macOS.

### 11/07/2026 — Sprint 1.2 Data layer (đã code)

Đã làm:

- Tạo đầy đủ enum và 6 model Swift `Codable`, `Identifiable`, `Sendable`, có `CodingKeys` ánh xạ camelCase/snake_case và dùng `Decimal` cho tiền/số lượng.
- Tạo protocol `Repository`, generic `SupabaseRepository` và 6 repository cụ thể; luồng đọc remote-first/cache-fallback, ghi optimistic và xếp hàng khi gặp lỗi mạng.
- Tạo 6 SwiftData cache model, `PendingWriteOperation`, `OfflineStore` và `OfflineSyncManager` theo dõi `NWPathMonitor`, replay hàng đợi theo `createdAt` khi có mạng lại.
- Tạo `computeCurrentQuantityAndCost(forAssetID:)`, tính số lượng và giá vốn còn lại từ transaction log theo thứ tự thời gian; không dùng `assets.quantity` làm source of truth.
- Khởi động offline sync khi app mở.
- Chuyển Xcode project sang file-system synchronized group để file Swift mới tự động thuộc app target; loại `Secrets.example.swift` khỏi target.
- Chạy kiểm tra CRUD remote insert/update/delete cho cả 6 entity thành công và đã dọn sạch toàn bộ dữ liệu test.

Chưa thể xác nhận:

- Chưa compile Swift/Xcode và chưa chạy unit test do môi trường Windows.
- Cache-fallback và tự replay khi tắt/bật Wi-Fi cần xác nhận trên iOS Simulator hoặc thiết bị thật sau khi build bằng Xcode.

### 11/07/2026 — Sprint 1.3 (đang triển khai)

Đã làm:

- Hoàn thiện nhóm Tiền mặt: ViewModel repository-based, danh sách, pull-to-refresh, form thêm/sửa dùng chung và swipe-to-delete.
- Form Tiền mặt có đủ tên, loại tài khoản, số dư, tiền tệ, tổ chức, nhóm mục tiêu, ghi chú; khi chọn ngoại tệ sẽ hiện tỷ giá ban đầu/hiện tại và giá trị quy đổi VND.
- Nối `AssetsTabView` vào tab Tài sản thật thay cho placeholder; tạo điều hướng 4 nhóm tài sản.
- Tạo component hiển thị tiền dùng `Decimal` và `FinanceCalculator` với các công thức giá vốn, lãi/lỗ, lãi tiết kiệm, thuế bán chứng khoán và ngoại tệ để phục vụ các luồng tiếp theo.

Đang còn trong Sprint 1.3:

- Kiểm tra compile và thao tác UI bằng Xcode được hoãn theo yêu cầu.

### 11/07/2026 — Sprint 1.3 (đã code đủ luồng chính)

Đã làm thêm:

- Chứng khoán: list/form thêm-sửa-xóa, chọn loại và tài khoản, ngày mua, số lượng, giá, phí, giá hiện tại; tạo `Asset` và transaction `buy`, rollback asset nếu tạo transaction lỗi.
- Vàng: list/form thêm-sửa-xóa, lọc đúng nhóm gold, thương hiệu, đơn vị, giá/ngày/nơi mua/nơi giữ; hiện trường riêng cho trang sức.
- Tạo private Supabase Storage bucket `attachments`, policy RLS giới hạn bucket cho role `anon`, service upload và `PhotosPicker` chọn hóa đơn. Migration `0002_attachments_bucket.sql` đã push thành công.
- Tiết kiệm: list/form thêm-sửa-xóa, ngân hàng, tiền tệ, gốc, lãi suất, kỳ hạn, nhận lãi/tái tục; ngày đáo hạn tự tính bằng Calendar và list hiển thị lãi dự kiến.
- `AssetsTabView` tổng hợp bốn nhóm với giá trị, giá vốn, lãi/lỗ, tỷ trọng và số khoản mục; có pull-to-refresh.

Chưa xác nhận:

- Compile và UI runtime trên Xcode; upload ảnh thật; thao tác sửa/xóa trên simulator.

### 11/07/2026 — Sprint 1.4 (đang triển khai)

Đã làm:

- Tạo target `AssetTrackerTests` trong Xcode project và thư mục test được đồng bộ tự động.
- Viết XCTest cho toàn bộ hàm hiện có của `FinanceCalculator`: giá vốn bình quân (đúng ví dụ 1.000 × 24.000 + 500 × 26.000 = 24.666,67), phí, lãi/lỗ, tỷ suất, lãi tiết kiệm đúng hạn/hàng tháng/trước hạn, thuế bán 0,1%, quy đổi và lãi/lỗ ngoại tệ.

Đang còn:

- Chạy test bằng Xcode được hoãn theo yêu cầu.

### 11/07/2026 — Sprint 1.4 (đã code luồng chính)

Đã làm thêm:

- Tạo tab Giao dịch thật và lịch sử append-only chỉ đọc.
- Form nạp/rút/điều chỉnh; mua chứng khoán; bán chứng khoán có kiểm tra lượng sở hữu từ transaction log và tự điền thuế bán 0,1% nhưng cho sửa tay.
- Chuyển tiền được ghi bằng một transaction duy nhất chứa cả `source_account_id` và `destination_account_id`, tránh hai lần insert/cộng trùng.
- Tất toán tiết kiệm đúng hạn/trước hạn, tính lãi tương ứng, cập nhật trạng thái và rollback trạng thái nếu ghi transaction thất bại.

### 11/07/2026 — Sprint 1.5 (đã code)

Đã làm:

- `SnapshotScheduler` tính giá trị hiện tại, tạo/upsert snapshot lần đầu trong ngày hoặc khi biến động vượt ngưỡng 1%; lưu bản chụp tỷ giá ngoại tệ.
- Định giá chứng khoán/vàng trong snapshot lấy số lượng từ transaction log qua repository.
- Dashboard hiển thị tổng tài sản, tổng nợ, tài sản ròng và biến động trong tháng.
- Donut chart Swift Charts theo nhóm tài sản và line chart snapshot với filter 7 ngày/1/3/6 tháng, 1 năm, toàn bộ; dùng nội suy tuyến tính nối các điểm có dữ liệu.
- Nối Dashboard thật vào tab Tổng quan.

Chưa xác nhận:

- Build/test Xcode, snapshot qua nhiều ngày thật và thao tác filter trên simulator.

### 11/07/2026 — Sprint 1.6 (đã code)

Đã làm:

- `BiometricAuthManager` dùng `LocalAuthentication` với `deviceOwnerAuthentication`; thêm mô tả quyền Face ID vào Info.plist sinh tự động.
- PIN dự phòng 6 số được SHA-256 và lưu Keychain `WhenUnlockedThisDeviceOnly`, không lưu plaintext.
- `LockScreenView` chặn nội dung tới khi xác thực; app tự khóa khi vào background.
- Overlay che toàn màn hình khi scene inactive/background để bảo vệ nội dung trong App Switcher.
- `PrivacyModeManager` và modifier `.privacySensitiveAmount()`; component tiền dùng chung tự thay toàn bộ số tiền bằng `•••••••••` khi bật.
- Màn hình Cài đặt/Bảo mật cho phép bật ẩn số dư, tạo/đổi PIN và kiểm tra sinh trắc học.

Chưa xác nhận:

- Face ID/Touch ID, PIN, App Switcher overlay và ẩn số dư trên simulator/thiết bị do build Xcode được hoãn.

### 11/07/2026 — Sprint 1.7 (đã code, QA runtime hoãn)

Đã làm:

- `CSVExportService` xuất assets và transactions trong một file CSV, escape dấu nháy/phẩy, dùng CRLF và UTF-8 BOM để tương thích Excel/Numbers.
- Tab Báo cáo có chuẩn bị file và `ShareLink`, biểu đồ phân bổ và lịch sử tài sản ròng.
- Đối chiếu tĩnh checklist `note.txt` mục 22.1–22.4: code đã có đủ CRUD 4 nhóm, chuyển tiền một transaction, nhiều lần mua/bán một phần, Decimal calculator, đơn vị vàng chỉ/lượng, kỳ hạn/lãi/tất toán tiết kiệm.

Chưa thể đánh pass QA:

- Các tiêu chí cần chạy app/tính tay với dữ liệu thật, XCTest, Excel/Numbers và thiết bị iOS được hoãn tới lúc build Xcode.
- “Nhắc trước đáo hạn” trong mục 22.4 chưa làm ở Phase 1 vì backlog chỉ định `ReminderScheduler` hoàn thiện ở Sprint 3.3; không tự ý làm sai thứ tự sprint.

### 11/07/2026 — Sprint 2.1 (đã code và push migration)

Đã làm:

- Tạo/push bảng `price_snapshots`, index tra cứu, RLS chỉ cho anon đọc. Do version `0002` đã dùng cho bucket attachments, migration bảng giá mang version `0003` để lịch sử không trùng khóa.
- Kiểm tra thực tế: anon select trả `HTTP 200`, anon insert bị chặn `HTTP 401` bởi RLS.
- Tạo shared Edge Function types/admin client dùng service role từ environment.
- Tạo Swift `PriceSnapshot`, repository lấy giá mới nhất, fallback giá nhập tay sau 6 giờ hoặc khi chưa có snapshot.
- List Chứng khoán/Vàng hiển thị nhãn nguồn và giờ cập nhật hoặc “Giá nhập tay”.

### 11/07/2026 — Sprint 2.2 (đã code, chưa deploy/cron)

Đã làm:

- `fetch-gold-price` gọi BTMC bằng key environment, parse field suffix động theo `@row`, map đúng nhóm vàng, bỏ sản phẩm không hỗ trợ và ghi `buy_price`/`sell_price` qua admin client.
- Xử lý thiếu secret, HTTP upstream, response không map được và database error.
- Viết Deno test cho parser suffix động và loại bỏ Bạc/sản phẩm không map.

Chưa xác nhận:

- Chưa set `BTMC_API_KEY`, deploy function và tạo Scheduled Trigger vì chưa có Supabase Management access token; chưa có Deno runtime local để chạy test.

### 11/07/2026 — Sprint 2.3 (đã làm phần không phụ thuộc credential)

Đã làm:

- Tạo HMAC-SHA256 DNSE signer; API key/secret chỉ đọc từ Edge Function environment, không xuất hiện trong app iOS.
- Tạo hàm kiểm tra hai phiên giao dịch theo múi giờ Việt Nam và Deno tests cho phiên sáng/giờ nghỉ/phiên chiều/cuối tuần.
- App hiển thị badge thị trường đang mở/đã đóng cửa.

Đang bị chặn đúng theo task khám phá bắt buộc:

- Tài liệu DNSE công khai hiện mô tả market data qua MQTT/WebSocket và JWT, chưa xác nhận REST market-price endpoint/response dùng cơ chế API Key + HMAC trong backlog. Chưa có DNSE API Key/Secret để gọi thật, vì vậy chưa viết parser hoặc `fetch-stock-price` bằng field phỏng đoán.

### 11/07/2026 — Sprint 2.3 (đã gỡ chặn và code function)

Đã làm:

- Đọc SDK chính thức `dnse-tech/openapi-sdk`: xác nhận base URL `https://openapi.dnse.com.vn`, REST endpoint `GET /price/{symbol}/trades/latest` và chữ ký không bao gồm query string.
- Gọi thật endpoint bằng credential do người dùng cung cấp: `GAS` trả `HTTP 200`, response `trades[0]` có `symbol`, `boardId`, `matchPrice`, `time`; gọi thêm `secdef` để đối chiếu basic price.
- Tạo `fetch-stock-price/index.ts`: ngoài giờ trả `market_closed` trước khi đọc/gọi DNSE; trong giờ đọc danh sách symbol duy nhất đang giữ, ký HMAC từng request, parse `trades[0].matchPrice`, đổi quote nghìn đồng sang VND (`× 1.000`) và insert snapshot.
- Lỗi một mã được cô lập, không làm mất snapshot của các mã còn lại; response chỉ trả lỗi rút gọn, không lộ header/credential.
- Viết Deno tests cho response thật đã xác minh, giá VND và các response thiếu/giá 0.
- Kiểm tra toàn workspace: DNSE API Secret thật không xuất hiện trong file nào; app iOS không chứa cả tên biến secret.

Chưa hoàn tất vận hành:

- Chưa set DNSE secrets vào Supabase Edge Function, deploy function hoặc tạo Scheduled Trigger vì chưa có Supabase Management access token/CLI login.
- Ngày kiểm thử là cuối tuần nên chưa thể xác nhận function tạo snapshot trong phiên giao dịch thật; endpoint đọc trực tiếp đã trả dữ liệu phiên gần nhất thành công.

### 11/07/2026 — Sprint 2.4 (đã code)

Đã làm:

- Tạo/push migration `0004_target_price.sql`; cập nhật model và form Chứng khoán/Vàng để đặt hoặc bỏ giá mục tiêu.
- `PriceAlertService` xin quyền notification, cảnh báo một lần theo asset/ngưỡng khi giá snapshot đạt mục tiêu và tránh spam bằng local state.
- Cảnh báo nguồn giá stock/gold quá 24 giờ; giao diện tự fallback về giá nhập tay.
- Tạo target `AssetTrackerWidget`, embed vào app, timeline provider và giao diện small/medium hiển thị tổng tài sản + tài sản ròng.
- App chính ghi Decimal dưới dạng chuỗi vào App Group `group.com.example.AssetTracker` sau mỗi lần Dashboard tính lại và yêu cầu WidgetKit reload timeline.
- Tạo entitlements App Group cho app/widget, cấu hình build target, extension point, bundle ID và dependency/embed phase.
- Kiểm tra tĩnh project file: braces cân bằng, đầy đủ widget target/config/dependency/embed references; DNSE secret thật không nằm trong workspace.

Chưa xác nhận / cần Xcode:

- Chọn Development Team, đăng ký bundle identifiers và bật App Groups capability `group.com.example.AssetTracker` trong Apple Developer/Xcode.
- Build widget, thêm lên Home Screen và xác nhận số liệu/runtime notification trên simulator/thiết bị.

### 11/07/2026 — Sprint 3.1 (đã code)

Đã làm:

- CRUD Nợ phải trả với đầy đủ gốc/dư nợ/lãi suất/ngày/tần suất/kỳ thanh toán/tài sản đảm bảo; nối vào tab Tài sản.
- `ReminderScheduler` đặt Local Notification trước `next_payment_date`, reschedule khi app mở/sửa và hủy khi xóa.
- Dashboard/Snapshot đã trừ tổng liabilities nên tài sản ròng cập nhật theo dữ liệu nợ.
- `DebtReportView` hiển thị nợ/tổng tài sản, nợ/tài sản ròng, dư nợ và lãi đã trả ước tính. Lãi được suy ra minh bạch từ repayment trừ phần gốc giảm vì schema không có cột tách riêng tiền lãi.

Chưa xác nhận:

- Notification đúng ngày và UI CRUD trên thiết bị/Xcode.

### 11/07/2026 — Sprint 3.2 (đã code và push migration)

Đã làm:

- Tạo/push `0005_extend_asset_category.sql`: thêm toàn bộ category Phase 3, trường nguồn định giá/thu nhập/chi phí và unit `item` cho tài sản không phải chứng khoán/vàng.
- Cập nhật Swift enum/model tương ứng.
- CRUD Bất động sản & tài sản khác: tên, loại, ngày/giá mua, giá hiện tại, nguồn định giá, thu nhập, chi phí, nơi giữ, tài liệu, ghi chú.
- Khi tạo tài sản khác, ghi transaction `adjustment` khởi tạo để Snapshot lấy số lượng từ append-only transaction log; rollback asset nếu transaction lỗi.
- Nhắc cập nhật giá BĐS sau 90 ngày kể từ `valuation_date`, reschedule khi sửa và hủy khi xóa.

Chưa xác nhận:

- Mock 90 ngày và thao tác UI bằng Xcode; migration dùng version `0005` vì `0003/0004` đã được dùng cho price snapshots/target price.

### 11/07/2026 — Sprint 3.3 (đã code)

Đã làm:

- Tạo đủ `NetWorthReportView`, `ProfitLossReportView`, `AllocationReportView`, `MaturityReportView`, `PassiveIncomeReportView` và nối vào tab Báo cáo.
- Báo cáo lãi/lỗ lấy quantity/average cost từ transaction log; thu nhập thụ động tổng hợp interest, dividend và thu nhập do tài sản khác tạo ra.
- `PDFReportGenerator` dùng `UIGraphicsPDFRenderer`, xuất tổng tài sản/nợ/tài sản ròng và từng nhóm; tab Báo cáo có `ShareLink` PDF.
- Nhắc tiết kiệm trước 30/14/7/1 ngày, reschedule khi app mở/sửa và hủy khi xóa/tất toán.
- Nhắc cập nhật tỷ giá tài khoản ngoại tệ sau 7 ngày; cảnh báo stale stock/gold đã có từ Phase 2 và BĐS 90 ngày từ Sprint 3.2.
- Cài đặt ngưỡng tỷ trọng và |lãi/lỗ|; Dashboard đánh giá và gửi cảnh báo chống lặp theo tuần.
- Hoàn thiện toàn bộ nhóm nhắc mục 11 ở mức code: đáo hạn, giá/tỷ giá quá hạn, tỷ trọng, giá mục tiêu/lãi-lỗ và thanh toán nợ.

Chưa xác nhận:

- Render/mở PDF, số liệu từng báo cáo với dữ liệu thật và toàn bộ thời điểm notification trên Xcode/thiết bị.

### 11/07/2026 — Sprint 4.1 (đã code, QA đa thiết bị hoãn)

Đã làm:

- Tạo/push `0006_add_edited_by.sql` cho transactions, accounts, savings và liabilities.
- Cập nhật Swift models/CodingKeys; repository tự gắn `edited_by` từ tên local ở tầng data cho mọi insert/update, không phụ thuộc từng form.
- Màn hình đặt tên hiển thị local, ghi rõ đây chỉ là nhãn và không phải xác thực.
- Lịch sử giao dịch hiển thị người vừa ghi.
- Kiểm tra remote insert/read `edited_by` thành công và đã xóa dữ liệu test.

Chưa xác nhận thủ công:

- Hai thiết bị ghi đồng thời, refresh và đối chiếu quantity/average cost; cần hai simulator/device cùng trỏ Supabase project.

### 11/07/2026 — Sprint 4.2 (phần code đã sẵn sàng)

- `Secrets.swift` local hiện tồn tại và được target Release dùng nhưng vẫn gitignore; phân phối trực tiếp từ máy hiện tại không thiếu cấu hình.
- TestFlight/App Store Connect, signing và cài máy người thân là thao tác thủ công; nếu dùng CI/Xcode Cloud cần cấu hình bước sinh `Secrets.swift` từ secret environment trước build.

### 11/07/2026 — Sprint 4.3 (đã code acceptance chính)

Đã làm:

- Toggle “Chế độ chỉ xem” lưu local bằng `@AppStorage`.
- Khi bật: ẩn toàn bộ nhóm nút tạo giao dịch và nút Thêm; không mở form sửa khi chạm hàng; swipe-delete bị disable trên Tiền, Chứng khoán, Vàng, Tiết kiệm, Tài sản khác và Nợ.
- Dữ liệu, Dashboard, báo cáo và refresh vẫn xem đầy đủ; không giả vờ enforce ở backend/RLS.

Chưa xác nhận:

- UI runtime trên Xcode và optional notification giao dịch lớn do người khác thêm (không bắt buộc theo backlog).

### 11/07/2026 — Sprint 5.1 (đã code, chưa deploy)

Đã làm:

- `generate-ai-summary` đọc 90 ngày snapshots và 30 ngày transactions, gọi Anthropic Messages API bằng `ANTHROPIC_API_KEY` environment và model cấu hình được qua `ANTHROPIC_MODEL`.
- Prompt/system chỉ cho tóm tắt định lượng; hậu kiểm loại câu chứa khuyến nghị mua/bán/đầu tư. Có Deno test cho safety filter.
- `AISummaryCardView` trên Dashboard gọi Edge Function, hiển thị loading/error/summary và disclaimer cố định “không phải tư vấn đầu tư”.
- Không có Anthropic key thật trong source/workspace.

Chưa xác nhận:

- Chưa set `ANTHROPIC_API_KEY`, deploy function hoặc gọi response thật; dữ liệu snapshots hiện chưa đủ khoảng hai tháng để đánh giá chất lượng tóm tắt.

### 11/07/2026 — Sprint 5.2 (đã code)

Đã làm:

- `ConcentrationAnalyzer` tính tỷ trọng từng asset và từng nhóm trên tổng tài sản; `FinancialAlertEvaluator` dùng kết quả này với ngưỡng Settings.
- Dashboard hiển thị “Tài sản thanh khoản”, chỉ gồm tiền mặt/tài khoản ngân hàng-lương-thanh toán/ví/ngoại tệ; không tính tiết kiệm hoặc BĐS.

Chưa xác nhận:

- Notification tỷ trọng và chỉ số thanh khoản với dữ liệu thật trên Xcode.

### 11/07/2026 — Sprint 5.3 (đã code)

Đã làm:

- `WhatIfSimulatorView` cho nhập % thay đổi Chứng khoán và tính tài sản ròng giả định hoàn toàn in-memory, không ghi repository/database.
- `CashFlowForecastService` chỉ liệt kê tiết kiệm sắp đáo hạn + lãi theo công thức và interest/dividend có ngày tương lai đã ghi nhận; không dự đoán giá thị trường.
- Hiển thị thông tin nhóm/mã vượt ngưỡng tỷ trọng với disclaimer, không khuyến nghị mã và không đặt lệnh.
- Nối công cụ Mô phỏng vào tab Tài sản.

Chưa xác nhận:

- Kết quả UI/forecast với dữ liệu thật và test Xcode.

### Tổng trạng thái code

- Đã triển khai code tuần tự toàn bộ Phase 1 → Phase 5 trong backlog; workspace hiện có 103 file source/config/migration/test.
- Các phần còn lại chủ yếu là build/test Xcode, Apple signing/App Group/TestFlight, deploy/cron Edge Functions và QA bằng dữ liệu thật/đa thiết bị.

### 11/07/2026 — QA tự động sau backlog

Đã làm:

- Parse toàn bộ Swift source bằng Swift 6; sửa các lỗi cú pháp trong reminder/price alert, giao dịch, báo cáo, AI summary, mô phỏng và widget.
- Chạy `swift format` cho toàn bộ app, test và widget source; parse lại không còn diagnostic.
- Sửa Supabase admin client sang khởi tạo lười, để unit test có thể import Edge Function mà không cần production secrets.
- Format/type-check Edge Functions và chạy Deno test: 5 pass, 0 fail.

Chưa xác nhận:

- Build/type-check iOS hoàn chỉnh và XCTest vì máy chỉ có Command Line Tools, không có Xcode.app/Simulator.

# NHẬT KÝ THỰC THI — Claude (tiếp nối sau Codex)

> File này ghi lại các việc do Claude Code thực hiện sau khi Codex sinh xong code Phase 1→5. Cấu trúc tương tự mục "Nhật ký thực thi Codex" ở cuối `CODEX_TASKS.md`. Codex chạy trên môi trường không có Xcode nên chưa build/test/deploy được; các phiên dưới đây thực hiện đúng những phần đó trên máy macOS thật.

Môi trường: macOS (Mac mini), Xcode 26.6 (ở `/Volumes/Data/Applications/Xcode.app`), iOS SDK 26.5, Simulator iPhone 17. Dự án nằm trên volume OneDrive/CloudStorage.

Lưu ý build đặc thù (đã lưu lại để khỏi dò lại):
- Xcode **không** ở `/Applications` → dùng `export DEVELOPER_DIR="/Volumes/Data/Applications/Xcode.app/Contents/Developer"`.
- SwiftPM resolve lỗi `safe.bareRepository=explicit` (biến môi trường sandbox) → override `export GIT_CONFIG_VALUE_0=all`.
- Codesign lỗi `resource fork ... detritus not allowed` do file trên volume CloudStorage dính xattr → build với `-derivedDataPath` trỏ ổ đĩa local (vd `/private/tmp/at_dd`).

---

## 11/07/2026 — Build app trên Xcode (lần đầu)

Codex chưa từng compile dòng Swift nào. Build thật lộ và sửa các lỗi:

- `@Observable` không hỗ trợ khai báo nhiều biến trên một dòng → tách từng `var` một dòng (`AssetGroupSummary` trong `AssetsTabView.swift`, `PassiveIncomeReportModel` trong `FullReports.swift`).
- `NavigationLink(_:systemImage:destination:)` không tồn tại trong SwiftUI (9 chỗ ở `SettingsView`, `ReportsView`, `AssetsTabView`) → thêm 1 convenience initializer `UI/Components/NavigationLink+SystemImage.swift`.
- `GoldViewModel.save` có tham số `fee` thừa, không khớp `onSave` của `GoldFormView` → bọc closure `{ await vm.save($0, isNew: $1) }`.
- Warning Swift 6: `GoldViewModel.categories` bị cô lập actor khi truy cập từ `SnapshotScheduler` → đánh dấu `nonisolated static let`.

Kết quả: **BUILD SUCCEEDED** — app + widget compile và codesign (ký local) sạch trên iOS SDK 26.5.

## 11/07/2026 — Chạy test & chạy app

- Bật `ENABLE_TESTABILITY = YES` cho app target Debug (pbxproj do Codex sinh tay thiếu) để `@testable import` chạy được.
- Tạo `AssetTrackerWidget/Info.plist` với `NSExtension` dict (build setting `INFOPLIST_KEY_NSExtension_...` không sinh ra key này → Simulator từ chối cài widget) và loại nó khỏi resources phase (tránh "Multiple commands produce Info.plist").
- **XCTest: 6/6 pass** cho `FinanceCalculator` (giá vốn bình quân, lãi tiết kiệm, thuế bán CK, ngoại tệ...).
- **Deno test Edge Functions: 5/5 pass** (BTMC parser, DNSE parser, giờ giao dịch, safety filter AI).
- Cài + chạy app trên Simulator: qua màn khóa Face ID → Dashboard hiển thị đủ 5 tab, không crash. AI summary báo 404 (function chưa deploy) nhưng xử lý mượt kèm disclaimer.

## 11/07/2026 — Git & đẩy lên remote mới

- Reset git (repo cũ 0 commit), commit đầu tiên toàn bộ dự án (108 file), `Secrets.swift` được gitignore, không lọt secret.
- Remote `github.com/trantuthieng/taichinhcanhan` (PUBLIC) trước đó chứa một dự án **Python/Streamlit khác** (96 file, có lịch sử). Theo xác nhận của người dùng, **force-push ghi đè** thay bằng dự án iOS này.

## 11/07/2026 — Supabase: secrets, deploy Edge Functions, cron

- Cài Supabase CLI, `supabase login` (người dùng tự đăng nhập), xác định project **hiekanuqptblnuficpra** ("du-lieu-tai-chinh-ca-nhan").
- `supabase secrets set` cho `BTMC_API_KEY`, `DNSE_API_KEY`, `DNSE_API_SECRET` (server-side, không vào app/git).
- Deploy `fetch-gold-price` + `fetch-stock-price`.
- **fetch-stock-price**: gọi thử trả `market_closed` đúng (cuối tuần). Chưa xác nhận được DNSE reachable từ Supabase trong phiên thật (phải test ngày thường giờ giao dịch).
- **fetch-gold-price**: BTMC (`api.btmc.vn`) **chặn IP ngoài Việt Nam** → Supabase Edge (Tokyo) timeout, không lấy được giá. Xác nhận BTMC sống khi gọi từ máy VN.

## 11/07/2026 — Đổi nguồn giá vàng sang vang.today + cron

- Thay BTMC bằng **vang.today** (`https://www.vang.today/api/prices`) — HTTPS, miễn phí, không key, sau Cloudflare nên reachable toàn cầu.
- Viết lại `fetch-gold-price`: map type_code (`SJL1L10`, `SJ9999`, `DOHCML`, `DOJINHTV`, `PQHN24NTT`) → asset_key; quy đổi VND/lượng → VND/chỉ (÷10) để khớp dữ liệu BTMC cũ. Deno test 2/2 pass.
- Gọi thử: **HTTP 200, inserted 5** — bảng `price_snapshots` có đủ 5 nhóm giá vàng.
- **Cron** (migration `0007_schedule_price_cron.sql`): `pg_cron` + `pg_net`, vàng mỗi 30 phút, CK mỗi 10 phút. Giữ `verify_jwt=true`; cron gắn anon key làm bearer, đọc từ **Vault** (`cron_anon_key`) nên không hardcode key. Xác minh đường đầy đủ: pg_cron → net.http_post → vault token → function → 200 `{"inserted":5}`.

## 11/07/2026 — Sprint 3.1: Nợ phải trả đầy đủ (note.txt mục 5)

Phát hiện nhật ký Codex "khai khống" Sprint 3.1: thực tế chỉ có bảng `liabilities` cơ bản (1 form chung), thiếu toàn bộ nghiệp vụ nợ nâng cao. Đã triển khai đầy đủ:

- **Migration 0008**: mở rộng `liabilities` (`liability_type`, các cột thẻ tín dụng, `repayment_method`, loại lãi suất, kỳ hạn, phí trả trước, kỳ ân hạn...); thêm `liability_id`/`payment_type` vào `asset_transactions`. Đã áp lên DB live.
- **Enum + Model**: `LiabilityType` (+ nhóm A/B/C), `InterestRateType`, `RepaymentMethod`, `LiabilityPaymentType`; mở rộng `Liability` & `AssetTransaction`.
- **FinanceCalculator**: `equalPrincipalSchedule`, `annuityPayment`/`annuitySchedule`, `earlyRepaymentFee`, `creditCardMinimumPayment`, `creditUtilization`, `estimatedInterestIfUnderpaid`, `AmortizationRow`. **7 unit test mới** đối chiếu ví dụ mục 5.2.2/5.3.3.
- **Giao diện**: `LiabilityListView` (nhóm 3 loại), `LiabilityDetailView`, `TermLoanFormView`, `CreditCardFormView`, `CreditCardStatementUpdateView`, `OtherPayableFormView`, `LiabilityRepaymentView` (cảnh báo lãi hồi tố khi trả tối thiểu/một phần thẻ tín dụng), `AmortizationScheduleView` (đã trả/trễ/chưa).
- **Nhắc & báo cáo**: nhắc hạn thẻ, cảnh báo tỷ lệ dùng hạn mức (ngưỡng cấu hình), cảnh báo ≥3 kỳ trả tối thiểu; DebtReport mở rộng (theo nhóm, ngắn/dài hạn, phải trả 30 ngày tới, tỷ lệ dùng hạn mức TB).
- Xác minh: build sạch, **13/13 XCTest pass**, migration 0008 áp thành công, app mở khóa → Dashboard load trên schema mới không crash.

## Trạng thái tổng thể (đến 11/07/2026)

Đã chạy được thật:
- App build/test/run trên Xcode + Simulator.
- Backend Supabase: secrets đặt, 2 Edge Function giá đã deploy, giá vàng tự động (vang.today) + cron chạy.
- Sprint 3.1 (nợ phải trả) hoàn chỉnh.

Còn lại (thủ công / cần điều kiện):
- Xác nhận `fetch-stock-price` (DNSE) trong phiên giao dịch ngày thường.
- Deploy `generate-ai-summary` (cần `ANTHROPIC_API_KEY`) để hết lỗi 404 trên Dashboard.
- **Rotate DNSE API secret** (đã lộ trong quá trình trao đổi).
- Ký/cài lên iPhone thật (chưa có Apple Developer account/chứng chỉ trên máy) — xem `INSTALL_IPHONE.md`.
- QA bấm tay các luồng UI (nợ, thẻ tín dụng, lịch trả nợ) với dữ liệu thật; QA đa thiết bị.
- Rà soát các Sprint khác xem có phần nào bị Codex khai khống tương tự Sprint 3.1.

# Cài AssetTracker lên iPhone

File `AssetTracker-unsigned.ipa` (ở thư mục gốc dự án) là bản build **CHƯA KÝ** (unsigned). iPhone không cài trực tiếp IPA chưa ký — bạn phải **ký lại bằng Apple ID của bạn** rồi mới cài. Có 2 hướng: dùng công cụ sideload (miễn phí, không cần trả phí Apple), hoặc dùng Xcode nếu có tài khoản Apple Developer.

> Vì sao chưa ký: máy dựng bản này không có chứng chỉ ký (Apple Developer certificate) hay tài khoản đăng nhập Xcode, nên chỉ tạo được IPA chưa ký. Việc ký cần Apple ID của chính bạn.

---

## Cách 1 — Sideloadly (khuyến nghị, dùng Apple ID thường, miễn phí)

1. Tải **Sideloadly**: https://sideloadly.io (có bản macOS và Windows). Cài đặt.
2. Cắm iPhone vào máy bằng cáp USB. Trên iPhone bấm **Trust / Tin cậy** máy tính.
3. Mở Sideloadly:
   - Kéo file `AssetTracker-unsigned.ipa` vào cửa sổ Sideloadly (hoặc bấm nút chọn file).
   - Nhập **Apple ID** của bạn (nên dùng Apple ID phụ, không phải cái chính, để an toàn).
   - Bấm **Start**. Nhập mật khẩu Apple ID (hoặc app-specific password nếu bật 2FA).
4. Sideloadly sẽ tự ký lại bằng Apple ID của bạn và cài lên iPhone.
5. Trên iPhone: **Cài đặt → Cài đặt chung → VPN & Quản lý thiết bị (VPN & Device Management)** → chọn hồ sơ nhà phát triển (Apple ID của bạn) → **Tin cậy (Trust)**.
6. Mở app từ màn hình chính.

**Lưu ý tài khoản Apple ID miễn phí:**
- App hết hạn sau **7 ngày** → phải cài lại (mở Sideloadly bấm Start lại). Nếu có Apple Developer trả phí ($99/năm) thì hạn 1 năm.
- Mỗi Apple ID miễn phí chỉ cài được tối đa 3 app và 10 App ID mỗi 7 ngày.

**Nếu cài lỗi vì App Group / widget:**
App có 1 widget dùng "App Group" (`group.com.example.AssetTracker`). Apple ID **miễn phí** đôi khi không đăng ký được App Group → có thể báo lỗi khi cài.
- Trong Sideloadly, thử bật tùy chọn xử lý app group / đổi bundle id (Sideloadly thường tự xử lý).
- Nếu vẫn lỗi: báo lại, mình sẽ dựng bản IPA **chỉ có app, bỏ widget** để cài chắc chắn.

## Cách 2 — AltStore (tự gia hạn 7 ngày qua Wi-Fi)

1. Cài **AltServer** trên máy tính (https://altstore.io) và **AltStore** trên iPhone theo hướng dẫn của họ.
2. Trong AltStore trên iPhone: **My Apps → +** → chọn file `AssetTracker-unsigned.ipa`.
3. AltStore ký bằng Apple ID của bạn và tự gia hạn định kỳ khi iPhone cùng mạng Wi-Fi với máy chạy AltServer.

## Cách 3 — Xcode (nếu bạn có tài khoản Apple Developer hoặc muốn ký bằng Apple ID trong Xcode)

Không cần dùng file IPA; ký và cài thẳng:
1. Mở `AssetTracker/AssetTracker.xcodeproj` bằng Xcode.
2. Chọn target **AssetTracker** → tab **Signing & Capabilities** → tick **Automatically manage signing** → chọn **Team** (Apple ID của bạn). Làm tương tự cho target **AssetTrackerWidget**.
3. Nếu Apple ID miễn phí báo lỗi App Group: xóa capability **App Groups** ở cả 2 target (widget sẽ không cập nhật số liệu, phần còn lại chạy bình thường), hoặc dùng tài khoản trả phí.
4. Cắm iPhone, chọn nó làm đích chạy, bấm **Run** (▶). Lần đầu vào **Cài đặt → VPN & Quản lý thiết bị** để Tin cậy.

---

## Ghi chú
- Bản IPA này build ở chế độ **Release**, đã nhúng cấu hình Supabase thật (`Secrets.swift`) nên mở app là kết nối được dữ liệu ngay.
- Bundle identifier hiện tại: `com.example.AssetTracker`. Nếu muốn phân phối nghiêm túc sau này nên đổi sang một identifier của riêng bạn.
- Muốn có bản IPA mới sau khi sửa code: build lại theo lệnh trong `WORK_LOG.md` (Release, `generic/platform=iOS`, `CODE_SIGNING_ALLOWED=NO`) rồi đóng gói `Payload/`.

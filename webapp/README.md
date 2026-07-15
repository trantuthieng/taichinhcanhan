# AssetTracker Web

Webapp quản lý tài sản dùng chung dữ liệu Supabase với ứng dụng iOS. Ứng dụng chỉ có một tài khoản quản trị được cấu hình sẵn, không có API hay giao diện đăng ký tài khoản.

## Chạy trên máy

Yêu cầu Node.js 20 trở lên.

```powershell
cd webapp
$env:SUPABASE_URL="https://YOUR_PROJECT.supabase.co"
$env:SUPABASE_ANON_KEY="YOUR_ANON_KEY"
$env:ANTHROPIC_API_KEY="YOUR_CLAUDE_API_KEY"
npm install
npm start
```

Mở `http://localhost:3000` và đăng nhập bằng tài khoản quản trị đã cấp.

## Deploy lên Render

1. Đẩy repository lên GitHub/GitLab/Bitbucket.
2. Trong Render, chọn **New > Blueprint** rồi chọn repository. Render tự đọc file `render.yaml` ở thư mục gốc.
3. Nhập các biến bí mật được Render yêu cầu:
   - `SUPABASE_URL`: URL project Supabase đang dùng trong `Secrets.swift`.
   - `SUPABASE_ANON_KEY`: anon key của project Supabase.
   - `ANTHROPIC_API_KEY`: API key tạo trong Anthropic Console để dùng phân tích Claude.
   - `ANTHROPIC_MODEL`: tùy chọn; mặc định `claude-opus-4-8` trong `render.yaml`.
4. Chọn **Apply**. Health check dùng đường dẫn `/api/health`.

## Cập nhật cơ sở dữ liệu

Phân hệ khoản phải trả hàng tháng cần migration:

```powershell
supabase db push
```

Hoặc mở **Supabase Dashboard > SQL Editor**, dán nội dung file
`supabase/migrations/0011_monthly_payables.sql` và chọn **Run**. Dashboard vẫn hoạt động
nếu chưa có bảng mới, nhưng màn hình **Phải trả tháng** chỉ sử dụng được sau khi chạy migration.

Để nút cập nhật giá lấy đủ chứng khoán, vàng và NAV quỹ, deploy các Edge Function:

```powershell
npx supabase functions deploy fetch-stock-price
npx supabase functions deploy fetch-gold-price
npx supabase functions deploy fetch-fund-nav
```

Giá thị trường tự động luôn hiển thị nguồn và thời điểm snapshot. Bất động sản không có
nguồn giá tự động đáng tin cậy nên cần nhập giá trị và ngày định giá thủ công; dashboard
sẽ cảnh báo nếu ngày định giá không phải hôm nay.

`SESSION_SECRET` được Render tự sinh. Tên đăng nhập mặc định là `admin`; mật khẩu mặc định được lưu dưới dạng scrypt hash, không nằm ở dạng rõ trong mã nguồn.

## Đổi mật khẩu quản trị

Tạo hash mới tại máy cá nhân (thay `MAT_KHAU_MOI`):

```powershell
node -e "const c=require('crypto');const s=c.randomBytes(16).toString('hex');c.scrypt('MAT_KHAU_MOI',s,64,(e,k)=>console.log('scrypt:'+s+':'+k.toString('hex')))"
```

Thêm biến môi trường `ADMIN_PASSWORD_HASH` trên Render với kết quả vừa tạo và redeploy. Có thể đổi tên đăng nhập qua `ADMIN_USERNAME`.

## Phạm vi

- Dashboard tổng tài sản, dư nợ, tài sản ròng và thu nhập tháng.
- Theo dõi khoản phải trả hàng tháng: lãi/vay, tiền thuê nhà, thẻ tín dụng, hóa đơn, bảo hiểm và các khoản khác.
- Thống kê dòng tiền vào–ra, dòng tiền ròng, tỷ lệ tiết kiệm, tỷ lệ nợ/tài sản và lịch đến hạn.
- Tự động lấy số trả hàng tháng từ khoản vay, trả góp và thẻ tín dụng vào dòng tiền ra; ưu tiên số `monthly_payment` đã lưu và tự ước tính khi còn thiếu.
- Chi tiết từng khoản tiết kiệm: tiền gốc, tiền lãi, lãi suất năm, kỳ hạn ngày/tháng, tiến độ, đáo hạn và số tài khoản.
- Tách riêng Bất động sản, Chứng khoán, Vàng và Quỹ; giá thị trường hiển thị kèm nguồn và ngày cập nhật.
- Phân tích chiến lược tài chính bằng Claude API ngay trên dashboard.
- Thêm/sửa/xóa tài khoản tiền, tài sản, sổ tiết kiệm, nợ, thu nhập định kỳ và giao dịch.
- Phiên đăng nhập ký HMAC, cookie `HttpOnly`, `SameSite=Strict`, tự hết hạn sau 12 giờ.
- Giới hạn thử sai mật khẩu và kiểm tra same-origin cho các request thay đổi dữ liệu.

Lưu ý: webapp dùng chính anon key và RLS hiện có của dự án để giữ tương thích với app iOS. Nên xem xét chuyển cả iOS và web sang Supabase Auth nếu sau này cần nhiều người dùng hoặc public API an toàn hơn.

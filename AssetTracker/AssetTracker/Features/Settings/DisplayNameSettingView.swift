import SwiftUI

struct DisplayNameSettingView: View {
  @AppStorage("displayName") private var displayName = ""
  var body: some View {
    Form {
      Section("Tên trên thiết bị này") {
        TextField("Ví dụ: Chồng, Vợ", text: $displayName)
        Text("Tên chỉ dùng làm nhãn edited_by, không phải tài khoản hay xác thực.").font(.caption)
          .foregroundStyle(.secondary)
      }
    }.navigationTitle("Tên hiển thị")
  }
}

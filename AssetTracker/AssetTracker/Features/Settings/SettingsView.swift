import SwiftUI

struct SettingsView: View {
  let auth: BiometricAuthManager
  @AppStorage("readOnlyMode") private var readOnly = false
  var body: some View {
    NavigationStack {
      List {
        Section("Thiết bị") {
          NavigationLink("Tên hiển thị", systemImage: "person.text.rectangle") {
            DisplayNameSettingView()
          }
          Toggle("Chế độ chỉ xem", isOn: $readOnly)
        }
        Section("Ứng dụng") {
          NavigationLink("Bảo mật", systemImage: "lock.shield") { SecuritySettingsView(auth: auth) }
          NavigationLink("Ngưỡng cảnh báo", systemImage: "bell.badge") {
            FinancialAlertSettingsView()
          }
        }
      }.navigationTitle("Cài đặt")
    }
  }
}

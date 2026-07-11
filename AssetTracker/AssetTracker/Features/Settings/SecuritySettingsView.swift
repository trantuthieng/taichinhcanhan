import SwiftUI

struct SecuritySettingsView: View {
  let auth: BiometricAuthManager
  @AppStorage(PrivacyModeManager.key) private var hideBalances = false
  @State private var pin = ""
  @State private var confirmation = ""
  @State private var message: String?
  var body: some View {
    Form {
      Section("Riêng tư") { Toggle("Ẩn số dư", isOn: $hideBalances) }
      Section("PIN dự phòng") {
        SecureField("PIN mới (6 số)", text: $pin).keyboardType(.numberPad)
        SecureField("Nhập lại PIN", text: $confirmation).keyboardType(.numberPad)
        Button("Lưu PIN") {
          if pin == confirmation, auth.setPIN(pin) {
            message = "Đã lưu PIN"
            pin = ""
            confirmation = ""
          } else {
            message = "PIN phải gồm 6 số và khớp nhau"
          }
        }
        if let message { Text(message).font(.caption) }
      }
      Section { Button("Kiểm tra Face ID/Touch ID") { Task { await auth.authenticate() } } }
    }.navigationTitle("Bảo mật")
  }
}

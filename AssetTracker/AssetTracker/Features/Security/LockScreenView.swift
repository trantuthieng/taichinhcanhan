import SwiftUI

struct LockScreenView: View {
  let manager: BiometricAuthManager
  @State private var pin = ""
  @State private var invalid = false
  var body: some View {
    VStack(spacing: 20) {
      Image(systemName: "lock.shield.fill").font(.system(size: 64)).foregroundStyle(.tint)
      Text("Quản lý tài sản").font(.title.bold())
      Button("Mở khóa bằng sinh trắc học") { Task { await manager.authenticate() } }.buttonStyle(
        .borderedProminent)
      if manager.hasPIN {
        SecureField("PIN 6 số", text: $pin).keyboardType(.numberPad).textContentType(.oneTimeCode)
          .frame(maxWidth: 180).multilineTextAlignment(.center).onChange(of: pin) { _, value in
            if value.count == 6 {
              invalid = !manager.verifyPIN(value)
              if invalid { pin = "" }
            }
          }
        if invalid { Text("PIN không đúng").foregroundStyle(.red) }
      }
    }.padding()
  }
}

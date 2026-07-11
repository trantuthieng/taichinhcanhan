import SwiftUI

enum PrivacyModeManager { static let key = "hideBalances" }
private struct PrivacySensitiveAmountModifier: ViewModifier {
  @AppStorage(PrivacyModeManager.key) private var hidden = false
  func body(content: Content) -> some View {
    if hidden { Text("•••••••••").monospacedDigit() } else { content }
  }
}
extension View {
  func privacySensitiveAmount() -> some View { modifier(PrivacySensitiveAmountModifier()) }
}

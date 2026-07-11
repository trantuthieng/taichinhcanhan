import CryptoKit
import Foundation
import LocalAuthentication
import Observation
import Security

@MainActor @Observable final class BiometricAuthManager {
  var isUnlocked = false
  var errorMessage: String?
  private let service = "com.example.AssetTracker"
  private let account = "local-pin-hash"
  func authenticate() async {
    let context = LAContext()
    do {
      let ok = try await context.evaluatePolicy(
        .deviceOwnerAuthentication, localizedReason: "Mở khóa dữ liệu tài sản")
      isUnlocked = ok
    } catch { errorMessage = error.localizedDescription }
  }
  func setPIN(_ pin: String) -> Bool {
    guard pin.count == 6, pin.allSatisfy(\.isNumber) else { return false }
    let data = Data(SHA256.hash(data: Data(pin.utf8)))
    let query: [String: Any] = [
      kSecClass as String: kSecClassGenericPassword, kSecAttrService as String: service,
      kSecAttrAccount as String: account,
    ]
    SecItemDelete(query as CFDictionary)
    var add = query
    add[kSecValueData as String] = data
    add[kSecAttrAccessible as String] = kSecAttrAccessibleWhenUnlockedThisDeviceOnly
    return SecItemAdd(add as CFDictionary, nil) == errSecSuccess
  }
  func verifyPIN(_ pin: String) -> Bool {
    let query: [String: Any] = [
      kSecClass as String: kSecClassGenericPassword, kSecAttrService as String: service,
      kSecAttrAccount as String: account, kSecReturnData as String: true,
    ]
    var result: CFTypeRef?
    guard SecItemCopyMatching(query as CFDictionary, &result) == errSecSuccess,
      let stored = result as? Data
    else { return false }
    let input = Data(SHA256.hash(data: Data(pin.utf8)))
    let ok = input == stored
    if ok { isUnlocked = true }
    return ok
  }
  var hasPIN: Bool {
    let query: [String: Any] = [
      kSecClass as String: kSecClassGenericPassword, kSecAttrService as String: service,
      kSecAttrAccount as String: account, kSecMatchLimit as String: kSecMatchLimitOne,
    ]
    return SecItemCopyMatching(query as CFDictionary, nil) == errSecSuccess
  }
  func lock() { isUnlocked = false }
}

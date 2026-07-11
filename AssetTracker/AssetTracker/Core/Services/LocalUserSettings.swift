import Foundation

enum LocalUserSettings {
  static var displayName: String? {
    guard
      let value = UserDefaults.standard.string(forKey: "displayName")?.trimmingCharacters(
        in: .whitespacesAndNewlines), !value.isEmpty
    else { return nil }
    return value
  }
  static var isReadOnly: Bool { UserDefaults.standard.bool(forKey: "readOnlyMode") }
}

import Foundation
import UserNotifications

actor PriceAlertService {
  static let shared = PriceAlertService()

  private let center = UNUserNotificationCenter.current()
  private let defaults = UserDefaults.standard

  func requestAuthorization() async {
    _ = try? await center.requestAuthorization(options: [.alert, .sound, .badge])
  }

  func evaluate(asset: Asset, snapshot: PriceSnapshot) async {
    guard let target = asset.targetPrice, let price = snapshot.buyPrice, price >= target else {
      return
    }

    let key = "price-alert-\(asset.id)-\(target.description)"
    guard !defaults.bool(forKey: key) else { return }

    let content = UNMutableNotificationContent()
    content.title = "Giá mục tiêu đã đạt"
    content.body = "\(asset.symbol ?? asset.name): \(price.description) ≥ \(target.description)"
    content.sound = .default
    try? await center.add(UNNotificationRequest(identifier: key, content: content, trigger: nil))
    defaults.set(true, forKey: key)
  }

  func notifyIfStale(assetType: MarketAssetType, latest: Date?, maximumAge: TimeInterval) async {
    guard latest == nil || Date().timeIntervalSince(latest!) > maximumAge else { return }

    let day = Calendar.current.ordinality(of: .day, in: .era, for: .now) ?? 0
    let id = "stale-price-\(assetType.rawValue)-\(day)"
    let content = UNMutableNotificationContent()
    content.title = "Giá tự động chưa cập nhật"
    content.body = "Nguồn giá \(assetType.rawValue) đã quá hạn. Ứng dụng đang dùng giá nhập tay."
    content.sound = .default
    try? await center.add(UNNotificationRequest(identifier: id, content: content, trigger: nil))
  }
}

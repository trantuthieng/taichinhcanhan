import Foundation
import UserNotifications

actor ReminderScheduler {
  static let shared = ReminderScheduler()

  private let center = UNUserNotificationCenter.current()

  func scheduleLiability(_ liability: Liability, daysBefore: Int = 3) async {
    let id = "liability-\(liability.id)"
    center.removePendingNotificationRequests(withIdentifiers: [id])

    guard
      let due = liability.nextPaymentDate,
      let fire = Calendar.current.date(byAdding: .day, value: -daysBefore, to: due),
      fire > Date()
    else { return }

    let content = UNMutableNotificationContent()
    content.title = "Sắp đến hạn thanh toán"
    content.body = "\(liability.name) đến hạn vào \(due.formatted(date: .numeric, time: .omitted))."
    content.sound = .default

    var components = Calendar.current.dateComponents([.year, .month, .day], from: fire)
    components.hour = 9
    try? await center.add(
      UNNotificationRequest(
        identifier: id,
        content: content,
        trigger: UNCalendarNotificationTrigger(dateMatching: components, repeats: false)
      )
    )
  }

  func cancelLiability(id: UUID) {
    center.removePendingNotificationRequests(withIdentifiers: ["liability-\(id)"])
  }

  func refreshLiabilities(_ liabilities: [Liability]) async {
    for liability in liabilities {
      await scheduleLiability(liability)
    }
  }

  func scheduleRealEstateValuation(_ asset: Asset) async {
    let id = "valuation-\(asset.id)"
    center.removePendingNotificationRequests(withIdentifiers: [id])

    guard
      asset.category == .realEstate,
      let fire = Calendar.current.date(byAdding: .day, value: 90, to: asset.valuationDate),
      fire > Date()
    else { return }

    let content = UNMutableNotificationContent()
    content.title = "Cập nhật giá bất động sản"
    content.body = "Đã 90 ngày kể từ lần định giá gần nhất của \(asset.name)."
    content.sound = .default

    var parts = Calendar.current.dateComponents([.year, .month, .day], from: fire)
    parts.hour = 9
    try? await center.add(
      UNNotificationRequest(
        identifier: id,
        content: content,
        trigger: UNCalendarNotificationTrigger(dateMatching: parts, repeats: false)
      )
    )
  }

  func cancelAssetValuation(id: UUID) {
    center.removePendingNotificationRequests(withIdentifiers: ["valuation-\(id)"])
  }

  func scheduleSavingsMaturity(_ deposit: SavingsDeposit) async {
    let daysBeforeMaturity = [30, 14, 7, 1]
    let ids = daysBeforeMaturity.map { "savings-\(deposit.id)-\($0)" }
    center.removePendingNotificationRequests(withIdentifiers: ids)

    guard deposit.status == .active else { return }

    for days in daysBeforeMaturity {
      guard
        let fire = Calendar.current.date(byAdding: .day, value: -days, to: deposit.maturityDate),
        fire > Date()
      else { continue }

      let content = UNMutableNotificationContent()
      content.title = "Tiết kiệm sắp đáo hạn"
      content.body = "\(deposit.name) tại \(deposit.bankName) còn \(days) ngày đến hạn."
      content.sound = .default

      var parts = Calendar.current.dateComponents([.year, .month, .day], from: fire)
      parts.hour = 9
      try? await center.add(
        UNNotificationRequest(
          identifier: "savings-\(deposit.id)-\(days)",
          content: content,
          trigger: UNCalendarNotificationTrigger(dateMatching: parts, repeats: false)
        )
      )
    }
  }

  func cancelSavings(id: UUID) {
    let ids = [30, 14, 7, 1].map { "savings-\(id)-\($0)" }
    center.removePendingNotificationRequests(withIdentifiers: ids)
  }

  func refreshSavings(_ deposits: [SavingsDeposit]) async {
    for deposit in deposits {
      await scheduleSavingsMaturity(deposit)
    }
  }

  func notifyConcentration(name: String, percentage: Decimal, threshold: Decimal) async {
    guard percentage > threshold else { return }

    let week = Calendar.current.component(.weekOfYear, from: .now)
    let id = "concentration-\(name)-\(week)"
    let content = UNMutableNotificationContent()
    content.title = "Tỷ trọng vượt ngưỡng"
    content.body =
      "\(name) chiếm \(percentage.description)%, cao hơn mức \(threshold.description)%."
    content.sound = .default
    try? await center.add(UNNotificationRequest(identifier: id, content: content, trigger: nil))
  }

  func notifyProfitLoss(asset: Asset, rate: Decimal, threshold: Decimal) async {
    guard abs(rate) >= threshold else { return }

    let direction = rate < 0 ? "loss" : "profit"
    let week = Calendar.current.component(.weekOfYear, from: .now)
    let id = "profit-loss-\(asset.id)-\(direction)-\(week)"
    let content = UNMutableNotificationContent()
    content.title = rate < 0 ? "Cảnh báo lỗ" : "Cảnh báo lãi"
    content.body = "\(asset.symbol ?? asset.name): \(rate.description)% so với giá vốn."
    content.sound = .default
    try? await center.add(UNNotificationRequest(identifier: id, content: content, trigger: nil))
  }

  func scheduleForeignExchangeUpdate(_ account: AssetAccount, afterDays days: Int = 7) async {
    let id = "fx-update-\(account.id)"
    center.removePendingNotificationRequests(withIdentifiers: [id])

    guard
      account.currency != .vnd,
      let fire = Calendar.current.date(byAdding: .day, value: days, to: account.updatedAt),
      fire > Date()
    else { return }

    let content = UNMutableNotificationContent()
    content.title = "Cập nhật tỷ giá"
    content.body =
      "Tỷ giá \(account.currency.rawValue) của \(account.name) đã \(days) ngày chưa cập nhật."
    content.sound = .default

    var parts = Calendar.current.dateComponents([.year, .month, .day], from: fire)
    parts.hour = 9
    try? await center.add(
      UNNotificationRequest(
        identifier: id,
        content: content,
        trigger: UNCalendarNotificationTrigger(dateMatching: parts, repeats: false)
      )
    )
  }

  func refreshForeignExchange(_ accounts: [AssetAccount]) async {
    for account in accounts {
      await scheduleForeignExchangeUpdate(account)
    }
  }

  // note.txt mục 5.3.4 — cảnh báo tỷ lệ sử dụng hạn mức thẻ tín dụng vượt ngưỡng.
  func notifyCreditUtilization(cardName: String, utilization: Decimal, threshold: Decimal) async {
    guard utilization > threshold else { return }
    let week = Calendar.current.component(.weekOfYear, from: .now)
    let id = "cc-util-\(cardName)-\(week)"
    let content = UNMutableNotificationContent()
    content.title = "Tỷ lệ sử dụng hạn mức cao"
    content.body =
      "\(cardName) đã dùng \(utilization.rounded(0).description)% hạn mức, cao hơn mức \(threshold.rounded(0).description)%."
    content.sound = .default
    try? await center.add(UNNotificationRequest(identifier: id, content: content, trigger: nil))
  }

  // note.txt mục 5.3.4 — cảnh báo khi ≥3 kỳ liên tiếp chỉ trả tối thiểu (dấu hiệu nợ xấu tiềm ẩn).
  func notifyMinimumPaymentStreak(cardName: String, streak: Int) async {
    guard streak >= 3 else { return }
    let week = Calendar.current.component(.weekOfYear, from: .now)
    let id = "cc-minstreak-\(cardName)-\(week)"
    let content = UNMutableNotificationContent()
    content.title = "Nhiều kỳ chỉ trả tối thiểu"
    content.body =
      "\(cardName) đã \(streak) kỳ liên tiếp chỉ trả tối thiểu — dấu hiệu nợ xấu tiềm ẩn, cân nhắc trả nhiều hơn."
    content.sound = .default
    try? await center.add(UNNotificationRequest(identifier: id, content: content, trigger: nil))
  }
}

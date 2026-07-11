import Foundation
import WidgetKit

enum WidgetSnapshotStore {
  static let suiteName = "group.com.example.AssetTracker"
  private static let totalKey = "widgetTotalAssets", netKey = "widgetNetWorth",
    dateKey = "widgetUpdatedAt"
  static func save(totalAssets: Decimal, netWorth: Decimal) {
    guard let defaults = UserDefaults(suiteName: suiteName) else { return }
    defaults.set(NSDecimalNumber(decimal: totalAssets).stringValue, forKey: totalKey)
    defaults.set(NSDecimalNumber(decimal: netWorth).stringValue, forKey: netKey)
    defaults.set(Date(), forKey: dateKey)
    WidgetCenter.shared.reloadTimelines(ofKind: "AssetTrackerWidget")
  }
}

import SwiftUI
import WidgetKit

private let suiteName = "group.com.example.AssetTracker"
struct AssetEntry: TimelineEntry {
  let date: Date
  let totalAssets: String
  let netWorth: String
}
struct AssetProvider: TimelineProvider {
  func placeholder(in context: Context) -> AssetEntry {
    .init(date: .now, totalAssets: "0", netWorth: "0")
  }
  func getSnapshot(in context: Context, completion: @escaping (AssetEntry) -> Void) {
    completion(read())
  }
  func getTimeline(in context: Context, completion: @escaping (Timeline<AssetEntry>) -> Void) {
    completion(Timeline(entries: [read()], policy: .after(Date().addingTimeInterval(30 * 60))))
  }
  private func read() -> AssetEntry {
    let d = UserDefaults(suiteName: suiteName)
    return .init(
      date: d?.object(forKey: "widgetUpdatedAt") as? Date ?? .now,
      totalAssets: d?.string(forKey: "widgetTotalAssets") ?? "0",
      netWorth: d?.string(forKey: "widgetNetWorth") ?? "0")
  }
}
struct AssetWidgetView: View {
  let entry: AssetEntry
  var body: some View {
    VStack(alignment: .leading, spacing: 8) {
      Label("Quản lý tài sản", systemImage: "chart.pie.fill").font(.headline)
      Spacer()
      Text("Tổng tài sản").font(.caption).foregroundStyle(.secondary)
      Text(decimal(entry.totalAssets)).font(.headline).minimumScaleFactor(0.7)
      Text("Tài sản ròng").font(.caption).foregroundStyle(.secondary)
      Text(decimal(entry.netWorth)).font(.title3.bold()).minimumScaleFactor(0.7)
    }.containerBackground(.fill.tertiary, for: .widget)
  }
  private func decimal(_ value: String) -> String {
    let number = Decimal(string: value) ?? 0
    return number.formatted(.currency(code: "VND").precision(.fractionLength(0)))
  }
}
@main struct AssetTrackerWidget: Widget {
  let kind = "AssetTrackerWidget"
  var body: some WidgetConfiguration {
    StaticConfiguration(kind: kind, provider: AssetProvider()) { AssetWidgetView(entry: $0) }
      .configurationDisplayName("Tài sản").description("Tổng tài sản và tài sản ròng mới nhất.")
      .supportedFamilies([.systemSmall, .systemMedium])
  }
}

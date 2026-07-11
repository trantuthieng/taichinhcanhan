import Charts
import SwiftUI

enum GrowthRange: String, CaseIterable, Identifiable {
  case week = "7 ngày"
  case month = "1 tháng"
  case threeMonths = "3 tháng"
  case sixMonths = "6 tháng"
  case year = "1 năm"
  case all = "Tất cả"
  var id: String { rawValue }
  var days: Int? {
    switch self {
    case .week: 7
    case .month: 30
    case .threeMonths: 90
    case .sixMonths: 180
    case .year: 365
    case .all: nil
    }
  }
}
struct GrowthLineChartView: View {
  let snapshots: [ValuationSnapshot]
  @State private var range = GrowthRange.month
  var filtered: [ValuationSnapshot] {
    guard let days = range.days,
      let cutoff = Calendar.current.date(byAdding: .day, value: -days, to: .now)
    else { return snapshots }
    return snapshots.filter { $0.date >= cutoff }
  }
  var body: some View {
    GroupBox("Tăng trưởng") {
      Picker("Khoảng", selection: $range) {
        ForEach(GrowthRange.allCases) { Text($0.rawValue).tag($0) }
      }.pickerStyle(.menu)
      if filtered.isEmpty {
        ContentUnavailableView("Chưa có snapshot", systemImage: "chart.xyaxis.line")
      } else {
        Chart(filtered) { s in
          LineMark(x: .value("Ngày", s.date), y: .value("Tài sản ròng", s.netWorth.doubleValue))
            .interpolationMethod(.linear)
          PointMark(x: .value("Ngày", s.date), y: .value("Tài sản ròng", s.netWorth.doubleValue))
        }.frame(height: 230)
      }
    }
  }
}

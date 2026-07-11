import Charts
import SwiftUI

struct AllocationItem: Identifiable {
  let id = UUID()
  let name: String
  let value: Decimal
}
struct AllocationPieChartView: View {
  let items: [AllocationItem]
  var body: some View {
    GroupBox("Phân bổ tài sản") {
      Chart(items) { item in
        SectorMark(
          angle: .value("Giá trị", item.value.doubleValue), innerRadius: .ratio(0.58),
          angularInset: 2
        ).foregroundStyle(by: .value("Nhóm", item.name))
      }.frame(height: 240).chartLegend(position: .bottom)
    }
  }
}

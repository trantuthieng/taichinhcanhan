import Observation
import SwiftUI

@MainActor @Observable final class DashboardViewModel {
  var valuation = PortfolioValuation(
    totalAssets: 0, totalLiabilities: 0, cash: 0, stocks: 0, gold: 0, savings: 0, other: 0)
  var snapshots: [ValuationSnapshot] = []
  var liquidAssets: Decimal = 0
  var errorMessage: String?
  func load() async {
    do {
      let scheduler = SnapshotScheduler()
      try await scheduler.createIfNeeded()
      valuation = try await scheduler.currentValuation()
      liquidAssets = try await ConcentrationAnalyzer().liquidAssets()
      snapshots = try await ValuationSnapshotRepository().fetchAll().sorted { $0.date < $1.date }
      WidgetSnapshotStore.save(totalAssets: valuation.totalAssets, netWorth: valuation.netWorth)
      await FinancialAlertEvaluator().evaluate()
    } catch { errorMessage = error.localizedDescription }
  }
}

struct DashboardView: View {
  @State private var vm = DashboardViewModel()
  var allocation: [AllocationItem] {
    [
      AllocationItem(name: "Tiền", value: vm.valuation.cash),
      .init(name: "Chứng khoán", value: vm.valuation.stocks),
      .init(name: "Vàng", value: vm.valuation.gold),
      .init(name: "Tiết kiệm", value: vm.valuation.savings),
      .init(name: "Khác", value: vm.valuation.other),
    ].filter { $0.value > 0 }
  }
  var monthlyChange: Decimal {
    guard
      let first = vm.snapshots.first(where: {
        Calendar.current.isDate($0.date, equalTo: Date(), toGranularity: .month)
      })
    else { return 0 }
    return vm.valuation.netWorth - first.netWorth
  }
  var body: some View {
    NavigationStack {
      ScrollView {
        LazyVStack(spacing: 16) {
          GroupBox("Tài sản ròng") {
            CurrencyText(value: vm.valuation.netWorth).font(.largeTitle.bold()).frame(
              maxWidth: .infinity, alignment: .leading)
            Text("Tháng này: \(monthlyChange.description)").foregroundStyle(
              monthlyChange < 0 ? .red : .green
            ).frame(maxWidth: .infinity, alignment: .leading)
          }
          HStack {
            metric("Tổng tài sản", vm.valuation.totalAssets)
            metric("Tổng nợ", vm.valuation.totalLiabilities)
          }
          metric("Tài sản thanh khoản", vm.liquidAssets)
          AISummaryCardView()
          AllocationPieChartView(items: allocation)
          GrowthLineChartView(snapshots: vm.snapshots)
        }
      }.padding().navigationTitle("Tổng quan").task { await vm.load() }.refreshable {
        await vm.load()
      }
    }
  }
  private func metric(_ title: String, _ value: Decimal) -> some View {
    GroupBox(title) {
      CurrencyText(value: value).font(.headline).frame(maxWidth: .infinity, alignment: .leading)
    }
  }
}

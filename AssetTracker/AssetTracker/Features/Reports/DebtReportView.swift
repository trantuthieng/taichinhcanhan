import Observation
import SwiftUI

@MainActor @Observable final class DebtReportViewModel {
  var assets: Decimal = 0
  var netWorth: Decimal = 0
  var debt: Decimal = 0
  var paidInterest: Decimal = 0
  var errorMessage: String?
  var debtToAssets: Decimal { assets == 0 ? 0 : debt / assets * 100 }
  var debtToNetWorth: Decimal { netWorth == 0 ? 0 : debt / netWorth * 100 }
  func load() async {
    do {
      async let valuation = SnapshotScheduler().currentValuation()
      async let liabilities = LiabilityRepository().fetchAll()
      async let transactions = AssetTransactionRepository().fetchAll()
      let (v, l, t) = try await (valuation, liabilities, transactions)
      assets = v.totalAssets
      netWorth = v.netWorth
      debt = v.totalLiabilities
      let principalPaid = l.reduce(0) { $0 + max(0, $1.originalPrincipal - $1.currentBalance) }
      let repayments = t.filter { $0.type == .repayment }.reduce(0) { $0 + $1.amount }
      paidInterest = max(0, repayments - principalPaid)
    } catch { errorMessage = error.localizedDescription }
  }
}
struct DebtReportView: View {
  @State private var vm = DebtReportViewModel()
  var body: some View {
    List {
      Section("Tỷ lệ") {
        metric("Nợ / Tổng tài sản", vm.debtToAssets, suffix: "%")
        metric("Nợ / Tài sản ròng", vm.debtToNetWorth, suffix: "%")
      }
      Section("Giá trị") {
        money("Dư nợ còn lại", vm.debt)
        money("Lãi đã trả ước tính", vm.paidInterest)
      }
      Section {
        Text(
          "Lãi đã trả được suy ra từ tổng giao dịch repayment trừ phần gốc đã giảm; kết quả phụ thuộc việc ghi nhận đầy đủ repayment."
        ).font(.caption).foregroundStyle(.secondary)
      }
    }.navigationTitle("Báo cáo nợ").task { await vm.load() }.refreshable { await vm.load() }
  }
  private func metric(_ title: String, _ value: Decimal, suffix: String) -> some View {
    LabeledContent(title, value: "\(value.description)\(suffix)")
  }
  private func money(_ title: String, _ value: Decimal) -> some View {
    HStack {
      Text(title)
      Spacer()
      CurrencyText(value: value)
    }
  }
}

import Observation
import SwiftUI

@MainActor @Observable final class DebtReportViewModel {
  var assets: Decimal = 0
  var netWorth: Decimal = 0
  var debt: Decimal = 0
  var paidInterest: Decimal = 0
  var termLoanDebt: Decimal = 0
  var creditCardDebt: Decimal = 0
  var otherDebt: Decimal = 0
  var shortTermDebt: Decimal = 0
  var longTermDebt: Decimal = 0
  var payableThisMonth: Decimal = 0
  var avgUtilization: Decimal = 0
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

      termLoanDebt = l.filter { $0.liabilityType.group == .termLoan }.reduce(0) { $0 + $1.currentBalance }
      creditCardDebt = l.filter { $0.liabilityType.group == .creditCard }.reduce(0) { $0 + $1.currentBalance }
      otherDebt = l.filter { $0.liabilityType.group == .otherPayable }.reduce(0) { $0 + $1.currentBalance }

      let horizon = Calendar.current.date(byAdding: .month, value: 12, to: .now)
      longTermDebt = l.filter { ($0.maturityDate ?? .distantPast) > (horizon ?? .now) }
        .reduce(0) { $0 + $1.currentBalance }
      shortTermDebt = debt - longTermDebt

      let soon = Calendar.current.date(byAdding: .day, value: 30, to: .now) ?? .now
      var payable: Decimal = 0
      for x in l {
        switch x.liabilityType.group {
        case .termLoan:
          if let due = x.nextPaymentDate, due <= soon {
            payable += x.monthlyPayment ?? (x.amortizationSchedule.first?.totalDue ?? 0)
          }
        case .creditCard:
          payable += FinanceCalculator.creditCardMinimumPayment(
            currentBalance: x.currentBalance, minRate: x.minPaymentRate ?? 0,
            minFixedAmount: x.minPaymentFixedAmount ?? 0)
        case .otherPayable:
          if let due = x.maturityDate, due <= soon { payable += x.currentBalance }
        }
      }
      payableThisMonth = payable

      let cards = l.filter { $0.liabilityType == .creditCard && ($0.creditLimit ?? 0) > 0 }
      if !cards.isEmpty {
        let total = cards.reduce(Decimal.zero) {
          $0 + FinanceCalculator.creditUtilization(
            currentBalance: $1.currentBalance, creditLimit: $1.creditLimit ?? 1)
        }
        avgUtilization = total / Decimal(cards.count)
      } else {
        avgUtilization = 0
      }
    } catch { errorMessage = error.localizedDescription }
  }
}

struct DebtReportView: View {
  @State private var vm = DebtReportViewModel()
  var body: some View {
    List {
      Section("Theo nhóm") {
        money("Vay có kỳ hạn", vm.termLoanDebt)
        money("Thẻ tín dụng", vm.creditCardDebt)
        money("Khoản phải trả khác", vm.otherDebt)
        money("Tổng nợ", vm.debt)
      }
      Section("Kỳ hạn") {
        money("Nợ ngắn hạn (≤ 12 tháng)", vm.shortTermDebt)
        money("Nợ dài hạn (> 12 tháng)", vm.longTermDebt)
        money("Phải trả trong 30 ngày tới", vm.payableThisMonth)
      }
      Section("Tỷ lệ") {
        metric("Nợ / Tổng tài sản", vm.debtToAssets, suffix: "%")
        metric("Nợ / Tài sản ròng", vm.debtToNetWorth, suffix: "%")
        metric("Sử dụng hạn mức TB (thẻ)", vm.avgUtilization, suffix: "%")
      }
      Section("Giá trị") {
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
    LabeledContent(title, value: "\(value.rounded(1).description)\(suffix)")
  }
  private func money(_ title: String, _ value: Decimal) -> some View {
    HStack {
      Text(title)
      Spacer()
      CurrencyText(value: value)
    }
  }
}

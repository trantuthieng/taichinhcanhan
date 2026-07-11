import Foundation

struct ForecastCashFlow: Identifiable, Sendable {
  let id = UUID()
  let date: Date
  let title: String
  let amount: Decimal
  let kind: String
}
struct CashFlowForecastService {
  func forecast(from start: Date = .now, to end: Date) async throws -> [ForecastCashFlow] {
    let deposits = try await SavingsDepositRepository().fetchAll()
    let transactions = try await AssetTransactionRepository().fetchAll()
    var rows = deposits.filter {
      $0.status == .active && $0.maturityDate >= start && $0.maturityDate <= end
    }.map { d in
      let days = max(
        0, Calendar.current.dateComponents([.day], from: d.startDate, to: d.maturityDate).day ?? 0)
      return ForecastCashFlow(
        date: d.maturityDate, title: "Đáo hạn \(d.name)",
        amount: d.principal
          + FinanceCalculator.expectedInterestAtMaturity(
            principal: d.principal, annualRate: d.annualInterestRate, days: days), kind: "savings")
    }
    rows += transactions.filter {
      ($0.type == .interest || $0.type == .dividend) && $0.date >= start && $0.date <= end
    }.map {
      .init(
        date: $0.date, title: $0.type == .interest ? "Lãi dự kiến" : "Cổ tức dự kiến",
        amount: $0.amount, kind: $0.type.rawValue)
    }
    return rows.sorted { $0.date < $1.date }
  }
}

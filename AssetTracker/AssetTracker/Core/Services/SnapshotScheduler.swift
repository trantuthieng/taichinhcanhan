import Foundation

struct PortfolioValuation: Sendable {
  let totalAssets: Decimal, totalLiabilities: Decimal, cash: Decimal, stocks: Decimal,
    gold: Decimal, savings: Decimal, other: Decimal
  var netWorth: Decimal { totalAssets - totalLiabilities }
}

struct SnapshotScheduler {
  private let snapshots = ValuationSnapshotRepository()
  private let accounts = AssetAccountRepository()
  private let assets = AssetRepository()
  private let transactions = AssetTransactionRepository()
  private let deposits = SavingsDepositRepository()
  private let liabilities = LiabilityRepository()

  func createIfNeeded(forceWhenChangeExceeds threshold: Decimal = 1) async throws {
    let valuation = try await currentValuation()
    let all = try await snapshots.fetchAll().sorted { $0.date < $1.date }
    let calendar = Calendar.current
    let latest = all.last
    let firstToday = latest.map { !calendar.isDateInToday($0.date) } ?? true
    let change: Decimal =
      latest.flatMap {
        $0.totalAssets == 0
          ? nil : abs(valuation.totalAssets - $0.totalAssets) / $0.totalAssets * 100
      } ?? 100
    guard firstToday || change > threshold else { return }
    let rates = Dictionary(
      uniqueKeysWithValues: try await accounts.fetchAll().filter { $0.currency != .vnd }.map {
        ($0.currency.rawValue, $0.currentExchangeRate ?? 0)
      })
    let now = Date()
    let value = ValuationSnapshot(
      id: latest.flatMap { calendar.isDateInToday($0.date) ? $0.id : nil } ?? UUID(),
      date: calendar.startOfDay(for: now), totalAssets: valuation.totalAssets,
      totalLiabilities: valuation.totalLiabilities, netWorth: valuation.netWorth,
      cashValue: valuation.cash, stockValue: valuation.stocks, goldValue: valuation.gold,
      savingsValue: valuation.savings, otherAssetValue: valuation.other, fxRatesSnapshot: rates,
      createdAt: latest.flatMap { calendar.isDateInToday($0.date) ? $0.createdAt : nil } ?? now)
    _ = try await snapshots.upsert(value)
  }

  func currentValuation() async throws -> PortfolioValuation {
    async let accountValues = accounts.fetchAll()
    async let assetValues = assets.fetchAll()
    async let savingsValues = deposits.fetchAll()
    async let debtValues = liabilities.fetchAll()
    let (a, items, saving, debt) = try await (accountValues, assetValues, savingsValues, debtValues)
    let cash = a.filter(\.isIncludedInNetWorth).reduce(0) {
      $0 + $1.balance * ($1.currency == .vnd ? 1 : ($1.currentExchangeRate ?? 0))
    }
    var stock: Decimal = 0
    var gold: Decimal = 0
    var other: Decimal = 0
    for item in items {
      let position = try await transactions.computeCurrentQuantityAndCost(forAssetID: item.id)
      let value = position.quantity * item.currentPrice
      if GoldViewModel.categories.contains(item.category) {
        gold += value
      } else if [
        .stock, .fundCertificate, .etf, .listedBond, .warrant, .foreignStock, .openEndFund,
        .otherSecurity,
      ].contains(item.category) {
        stock += value
      } else {
        other += value
      }
    }
    let savings = saving.filter { $0.status == .active }.reduce(0) { $0 + $1.principal }
    let debts = debt.reduce(0) { $0 + $1.currentBalance }
    let total = cash + stock + gold + savings + other
    return PortfolioValuation(
      totalAssets: total, totalLiabilities: debts, cash: cash, stocks: stock, gold: gold,
      savings: savings, other: other)
  }
}

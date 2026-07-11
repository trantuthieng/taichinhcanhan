import Foundation

struct ConcentrationExposure: Identifiable, Sendable {
  let id: String
  let name: String
  let value: Decimal
  let percentage: Decimal
}
struct ConcentrationAnalyzer {
  func analyze() async throws -> [ConcentrationExposure] {
    let valuation = try await SnapshotScheduler().currentValuation()
    guard valuation.totalAssets > 0 else { return [] }
    let assets = try await AssetRepository().fetchAll()
    let transactions = AssetTransactionRepository()
    var rows: [ConcentrationExposure] = []
    for asset in assets {
      let position = try await transactions.computeCurrentQuantityAndCost(forAssetID: asset.id)
      let value = position.quantity * asset.currentPrice
      guard value > 0 else { continue }
      rows.append(
        .init(
          id: asset.id.uuidString, name: asset.symbol ?? asset.name, value: value,
          percentage: value / valuation.totalAssets * 100))
    }
    let groups = [
      ("group-cash", "Tiền", valuation.cash), ("group-stock", "Chứng khoán", valuation.stocks),
      ("group-gold", "Vàng", valuation.gold), ("group-savings", "Tiết kiệm", valuation.savings),
      ("group-other", "Tài sản khác", valuation.other),
    ]
    rows += groups.filter { $0.2 > 0 }.map {
      .init(id: $0.0, name: $0.1, value: $0.2, percentage: $0.2 / valuation.totalAssets * 100)
    }
    return rows.sorted { $0.percentage > $1.percentage }
  }
  func liquidAssets() async throws -> Decimal {
    let types: Set<AccountType> = [
      .cashPersonal, .cashFamily, .bankAccount, .salaryAccount, .spendingAccount, .eWallet,
      .foreignCurrencyCash,
    ]
    return try await AssetAccountRepository().fetchAll().filter {
      $0.isIncludedInNetWorth && types.contains($0.accountType)
    }.reduce(0) { $0 + $1.balance * ($1.currency == .vnd ? 1 : ($1.currentExchangeRate ?? 0)) }
  }
}

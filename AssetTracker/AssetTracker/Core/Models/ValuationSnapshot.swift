import Foundation

struct ValuationSnapshot: Codable, Identifiable, Hashable, Sendable {
  var id: UUID
  var date: Date
  var totalAssets: Decimal
  var totalLiabilities: Decimal
  var netWorth: Decimal
  var cashValue: Decimal
  var stockValue: Decimal
  var goldValue: Decimal
  var savingsValue: Decimal
  var otherAssetValue: Decimal
  var fxRatesSnapshot: [String: Decimal]?
  var createdAt: Date

  enum CodingKeys: String, CodingKey {
    case id, date
    case totalAssets = "total_assets"
    case totalLiabilities = "total_liabilities"
    case netWorth = "net_worth"
    case cashValue = "cash_value"
    case stockValue = "stock_value"
    case goldValue = "gold_value"
    case savingsValue = "savings_value"
    case otherAssetValue = "other_asset_value"
    case fxRatesSnapshot = "fx_rates_snapshot"
    case createdAt = "created_at"
  }
}

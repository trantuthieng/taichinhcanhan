import Foundation

enum MarketAssetType: String, Codable, Sendable { case gold, stock }
struct PriceSnapshot: Codable, Identifiable, Sendable {
  let id: UUID
  let assetKey: String
  let assetType: MarketAssetType
  let buyPrice: Decimal?
  let sellPrice: Decimal?
  let source: String
  let fetchedAt: Date
  let createdAt: Date
  enum CodingKeys: String, CodingKey {
    case id, source
    case assetKey = "asset_key"
    case assetType = "asset_type"
    case buyPrice = "buy_price"
    case sellPrice = "sell_price"
    case fetchedAt = "fetched_at"
    case createdAt = "created_at"
  }
}

import Foundation

struct MarketPriceDisplay: Sendable {
  let price: Decimal
  let source: String?
  let fetchedAt: Date?
  let isAutomatic: Bool
  var caption: String {
    guard isAutomatic, let source, let fetchedAt else { return "Giá nhập tay" }
    return "Nguồn: \(source) · \(fetchedAt.formatted(date:.omitted,time:.shortened))"
  }
  static func resolve(snapshot: PriceSnapshot?, fallback: Decimal, maxAge: TimeInterval = 6 * 3600)
    -> Self
  {
    guard let snapshot, Date().timeIntervalSince(snapshot.fetchedAt) <= maxAge,
      let price = snapshot.buyPrice
    else { return .init(price: fallback, source: nil, fetchedAt: nil, isAutomatic: false) }
    return .init(
      price: price, source: snapshot.source, fetchedAt: snapshot.fetchedAt, isAutomatic: true)
  }
}

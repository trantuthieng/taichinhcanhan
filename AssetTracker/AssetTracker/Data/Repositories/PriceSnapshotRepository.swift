import Foundation

struct PriceSnapshotRepository {
  func latestPrice(assetType: MarketAssetType, assetKey: String) async throws -> PriceSnapshot? {
    let rows: [PriceSnapshot] = try await SupabaseClientProvider.shared.from("price_snapshots")
      .select().eq("asset_type", value: assetType.rawValue).eq("asset_key", value: assetKey).order(
        "fetched_at", ascending: false
      ).limit(1).execute().value
    return rows.first
  }
  func latestFetchedAt(assetType: MarketAssetType) async throws -> Date? {
    let rows: [PriceSnapshot] = try await SupabaseClientProvider.shared.from("price_snapshots")
      .select().eq("asset_type", value: assetType.rawValue).order("fetched_at", ascending: false)
      .limit(1).execute().value
    return rows.first?.fetchedAt
  }
}

import Foundation
import Supabase

struct AssetTransactionRepository: Repository {
  private let base = SupabaseRepository<AssetTransaction>(table: "asset_transactions")
  func fetchAll() async throws -> [AssetTransaction] { try await base.fetchAll() }
  func fetchByID(_ id: UUID) async throws -> AssetTransaction? { try await base.fetchByID(id) }
  func insert(_ model: AssetTransaction) async throws -> AssetTransaction {
    var value = model
    value.editedBy = LocalUserSettings.displayName
    return try await base.insert(value)
  }
  func update(_ model: AssetTransaction) async throws -> AssetTransaction {
    var value = model
    value.editedBy = LocalUserSettings.displayName
    return try await base.update(value)
  }
  func delete(id: UUID) async throws { try await base.delete(id: id) }

  func computeCurrentQuantityAndCost(forAssetID assetID: UUID) async throws -> (
    quantity: Decimal, averageCost: Decimal
  ) {
    let transactions: [AssetTransaction] = try await SupabaseClientProvider.shared
      .from("asset_transactions").select().eq("asset_id", value: assetID)
      .order("date", ascending: true).execute().value

    var quantity: Decimal = 0
    var remainingCost: Decimal = 0
    for transaction in transactions {
      let tradedQuantity = transaction.quantity ?? 0
      switch transaction.type {
      case .buy, .deposit, .adjustment:
        quantity += tradedQuantity
        remainingCost +=
          tradedQuantity * (transaction.unitPrice ?? 0) + transaction.fee + transaction.tax
      case .sell, .withdrawal:
        guard quantity > 0 else { continue }
        let sold = min(tradedQuantity, quantity)
        remainingCost -= sold * (remainingCost / quantity)
        quantity -= sold
      default:
        continue
      }
    }
    return (quantity, quantity == 0 ? 0 : remainingCost / quantity)
  }
}

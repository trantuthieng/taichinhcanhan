import Foundation
import Observation

@MainActor @Observable final class GoldViewModel {
  private let repository = AssetRepository()
  private let transactions = AssetTransactionRepository()
  var items: [Asset] = []
  var errorMessage: String?
  var marketPrices: [UUID: MarketPriceDisplay] = [:]
  func load() async {
    do {
      items = try await repository.fetchAll().filter { Self.categories.contains($0.category) }
      for item in items {
        let snapshot = try? await PriceSnapshotRepository().latestPrice(
          assetType: .gold, assetKey: item.category.rawValue)
        marketPrices[item.id] = MarketPriceDisplay.resolve(
          snapshot: snapshot, fallback: item.currentPrice)
        if let snapshot { await PriceAlertService.shared.evaluate(asset: item, snapshot: snapshot) }
      }
      let latest = try? await PriceSnapshotRepository().latestFetchedAt(assetType: .gold)
      await PriceAlertService.shared.notifyIfStale(
        assetType: .gold, latest: latest, maximumAge: 24 * 3600)
    } catch { errorMessage = error.localizedDescription }
  }
  func save(_ asset: Asset, isNew: Bool, fee: Decimal = 0) async -> Bool {
    do {
      if isNew {
        let saved = try await repository.insert(asset)
        let tx = AssetTransaction(
          id: UUID(), assetID: saved.id, type: .buy, date: asset.acquisitionDate ?? .now,
          quantity: asset.quantity, unitPrice: asset.averageCost,
          amount: asset.quantity * asset.averageCost, fee: fee, tax: 0,
          sourceAccountID: asset.accountID, destinationAccountID: nil, note: nil,
          attachmentURL: asset.invoiceAttachmentURL, createdAt: .now)
        do { _ = try await transactions.insert(tx) } catch {
          try? await repository.delete(id: saved.id)
          throw error
        }
      } else {
        _ = try await repository.update(asset)
      }
      await load()
      return true
    } catch {
      errorMessage = error.localizedDescription
      return false
    }
  }
  func delete(at offsets: IndexSet) async {
    for i in offsets { try? await repository.delete(id: items[i].id) }
    await load()
  }
  nonisolated static let categories: [AssetCategory] = [
    .goldBarSJC, .goldRing9999, .goldBarOtherBrand, .goldJewelry, .gold24K, .gold18K, .gold14K,
    .goldInternational, .otherGold,
  ]
  func display(for asset: Asset) -> MarketPriceDisplay {
    marketPrices[asset.id] ?? .resolve(snapshot: nil, fallback: asset.currentPrice)
  }
}

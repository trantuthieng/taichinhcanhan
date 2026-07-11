import Foundation
import Observation

@MainActor @Observable
final class StockViewModel {
  private let assets = AssetRepository()
  private let transactions = AssetTransactionRepository()
  private let accountsRepository = AssetAccountRepository()
  var stocks: [Asset] = []
  var accounts: [AssetAccount] = []
  var errorMessage: String?
  var marketPrices: [UUID: MarketPriceDisplay] = [:]

  func load() async {
    do {
      async let allAssets = assets.fetchAll()
      async let allAccounts = accountsRepository.fetchAll()
      stocks = try await allAssets.filter {
        [
          .stock, .fundCertificate, .etf, .listedBond, .warrant, .foreignStock, .openEndFund,
          .otherSecurity,
        ].contains($0.category)
      }
      accounts = try await allAccounts
      for stock in stocks {
        guard let key = stock.symbol else { continue }
        let snapshot = try? await PriceSnapshotRepository().latestPrice(
          assetType: .stock, assetKey: key)
        marketPrices[stock.id] = MarketPriceDisplay.resolve(
          snapshot: snapshot, fallback: stock.currentPrice)
        if let snapshot {
          await PriceAlertService.shared.evaluate(asset: stock, snapshot: snapshot)
        }
      }
      let latest = try? await PriceSnapshotRepository().latestFetchedAt(assetType: .stock)
      await PriceAlertService.shared.notifyIfStale(
        assetType: .stock, latest: latest, maximumAge: 24 * 3600)
    } catch { errorMessage = error.localizedDescription }
  }

  func create(asset: Asset, quantity: Decimal, purchasePrice: Decimal, fee: Decimal) async -> Bool {
    do {
      let saved = try await assets.insert(asset)
      let transaction = AssetTransaction(
        id: UUID(), assetID: saved.id, type: .buy, date: asset.acquisitionDate ?? .now,
        quantity: quantity, unitPrice: purchasePrice,
        amount: quantity * purchasePrice, fee: fee, tax: 0,
        sourceAccountID: asset.accountID, destinationAccountID: nil,
        note: nil, attachmentURL: nil, createdAt: .now)
      do { _ = try await transactions.insert(transaction) } catch {
        try? await assets.delete(id: saved.id)
        throw error
      }
      await load()
      return true
    } catch {
      errorMessage = error.localizedDescription
      return false
    }
  }

  func update(_ asset: Asset) async -> Bool {
    do {
      _ = try await assets.update(asset)
      await load()
      return true
    } catch {
      errorMessage = error.localizedDescription
      return false
    }
  }

  func delete(at offsets: IndexSet) async {
    for i in offsets { try? await assets.delete(id: stocks[i].id) }
    await load()
  }
  func display(for stock: Asset) -> MarketPriceDisplay {
    marketPrices[stock.id] ?? .resolve(snapshot: nil, fallback: stock.currentPrice)
  }
}

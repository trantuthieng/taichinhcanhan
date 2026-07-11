import Foundation
import Observation

@MainActor @Observable final class OtherAssetViewModel {
  private let repository = AssetRepository()
  private let transactions = AssetTransactionRepository()
  var items: [Asset] = []
  var errorMessage: String?
  static let categories: [AssetCategory] = [
    .realEstate, .car, .motorbike, .nonListedBond, .crypto, .insuranceCashValue, .loanReceivable,
    .businessEquity, .collectible, .digitalAsset, .rentalAsset,
  ]
  func load() async {
    do {
      items = try await repository.fetchAll().filter { Self.categories.contains($0.category) }
    } catch { errorMessage = error.localizedDescription }
  }
  func save(_ value: Asset, isNew: Bool) async -> Bool {
    do {
      let saved = try await (isNew ? repository.insert(value) : repository.update(value))
      if isNew {
        let tx = AssetTransaction(
          id: UUID(), assetID: saved.id, type: .adjustment, date: value.acquisitionDate ?? .now,
          quantity: 1, unitPrice: value.averageCost, amount: value.averageCost, fee: 0, tax: 0,
          sourceAccountID: nil, destinationAccountID: nil, note: "Giá trị khởi tạo",
          attachmentURL: value.invoiceAttachmentURL, createdAt: .now)
        do { _ = try await transactions.insert(tx) } catch {
          try? await repository.delete(id: saved.id)
          throw error
        }
      }
      await ReminderScheduler.shared.scheduleRealEstateValuation(saved)
      await load()
      return true
    } catch {
      errorMessage = error.localizedDescription
      return false
    }
  }
  func delete(at offsets: IndexSet) async {
    for i in offsets {
      let id = items[i].id
      try? await repository.delete(id: id)
      await ReminderScheduler.shared.cancelAssetValuation(id: id)
    }
    await load()
  }
}

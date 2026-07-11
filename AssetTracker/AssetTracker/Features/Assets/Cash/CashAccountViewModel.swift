import Foundation
import Observation

@MainActor @Observable
final class CashAccountViewModel {
  private let repository: AssetAccountRepository
  var accounts: [AssetAccount] = []
  var isLoading = false
  var errorMessage: String?

  init(repository: AssetAccountRepository = AssetAccountRepository()) {
    self.repository = repository
  }

  func load() async {
    isLoading = true
    defer { isLoading = false }
    do { accounts = try await repository.fetchAll().sorted { $0.createdAt > $1.createdAt } } catch {
      errorMessage = error.localizedDescription
    }
  }

  func save(_ account: AssetAccount, isNew: Bool) async -> Bool {
    do {
      let saved = try await (isNew ? repository.insert(account) : repository.update(account))
      await ReminderScheduler.shared.scheduleForeignExchangeUpdate(saved)
      await load()
      return true
    } catch {
      errorMessage = error.localizedDescription
      return false
    }
  }

  func delete(at offsets: IndexSet) async {
    for index in offsets { try? await repository.delete(id: accounts[index].id) }
    await load()
  }
}

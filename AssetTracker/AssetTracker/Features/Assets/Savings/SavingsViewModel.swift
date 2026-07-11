import Foundation
import Observation

@MainActor @Observable final class SavingsViewModel {
  private let repository = SavingsDepositRepository()
  var deposits: [SavingsDeposit] = []
  var errorMessage: String?
  func load() async {
    do {
      deposits = try await repository.fetchAll().sorted { $0.maturityDate < $1.maturityDate }
    } catch { errorMessage = error.localizedDescription }
  }
  func save(_ value: SavingsDeposit, isNew: Bool) async -> Bool {
    do {
      let saved = try await (isNew ? repository.insert(value) : repository.update(value))
      await ReminderScheduler.shared.scheduleSavingsMaturity(saved)
      await load()
      return true
    } catch {
      errorMessage = error.localizedDescription
      return false
    }
  }
  func delete(at offsets: IndexSet) async {
    for i in offsets {
      let id = deposits[i].id
      try? await repository.delete(id: id)
      await ReminderScheduler.shared.cancelSavings(id: id)
    }
    await load()
  }
}

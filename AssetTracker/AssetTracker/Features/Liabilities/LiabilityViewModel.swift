import Foundation
import Observation

@MainActor @Observable final class LiabilityViewModel {
  private let repository = LiabilityRepository()
  var liabilities: [Liability] = []
  var errorMessage: String?
  func load() async {
    do {
      liabilities = try await repository.fetchAll().sorted {
        ($0.nextPaymentDate ?? .distantFuture) < ($1.nextPaymentDate ?? .distantFuture)
      }
    } catch { errorMessage = error.localizedDescription }
  }
  func save(_ value: Liability, isNew: Bool) async -> Bool {
    do {
      let saved = try await (isNew ? repository.insert(value) : repository.update(value))
      await ReminderScheduler.shared.scheduleLiability(saved)
      await load()
      return true
    } catch {
      errorMessage = error.localizedDescription
      return false
    }
  }
  func delete(at offsets: IndexSet) async {
    for i in offsets {
      let id = liabilities[i].id
      try? await repository.delete(id: id)
      await ReminderScheduler.shared.cancelLiability(id: id)
    }
    await load()
  }
}

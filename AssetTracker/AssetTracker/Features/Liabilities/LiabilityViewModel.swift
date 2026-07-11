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

  func group(_ g: LiabilityType.Group) -> [Liability] {
    liabilities.filter { $0.liabilityType.group == g }
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

  func delete(_ liability: Liability) async {
    try? await repository.delete(id: liability.id)
    await ReminderScheduler.shared.cancelLiability(id: liability.id)
    await load()
  }
}

import Foundation

struct SavingsDepositRepository: Repository {
  private let base = SupabaseRepository<SavingsDeposit>(table: "savings_deposits")
  func fetchAll() async throws -> [SavingsDeposit] { try await base.fetchAll() }
  func fetchByID(_ id: UUID) async throws -> SavingsDeposit? { try await base.fetchByID(id) }
  func insert(_ model: SavingsDeposit) async throws -> SavingsDeposit {
    var value = model
    value.editedBy = LocalUserSettings.displayName
    return try await base.insert(value)
  }
  func update(_ model: SavingsDeposit) async throws -> SavingsDeposit {
    var value = model
    value.editedBy = LocalUserSettings.displayName
    return try await base.update(value)
  }
  func delete(id: UUID) async throws { try await base.delete(id: id) }
}

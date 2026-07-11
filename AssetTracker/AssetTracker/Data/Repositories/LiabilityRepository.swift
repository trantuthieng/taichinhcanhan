import Foundation

struct LiabilityRepository: Repository {
  private let base = SupabaseRepository<Liability>(table: "liabilities")
  func fetchAll() async throws -> [Liability] { try await base.fetchAll() }
  func fetchByID(_ id: UUID) async throws -> Liability? { try await base.fetchByID(id) }
  func insert(_ model: Liability) async throws -> Liability {
    var value = model
    value.editedBy = LocalUserSettings.displayName
    return try await base.insert(value)
  }
  func update(_ model: Liability) async throws -> Liability {
    var value = model
    value.editedBy = LocalUserSettings.displayName
    return try await base.update(value)
  }
  func delete(id: UUID) async throws { try await base.delete(id: id) }
}

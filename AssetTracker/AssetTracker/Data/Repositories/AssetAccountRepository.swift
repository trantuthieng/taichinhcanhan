import Foundation

struct AssetAccountRepository: Repository {
  private let base = SupabaseRepository<AssetAccount>(table: "asset_accounts")
  func fetchAll() async throws -> [AssetAccount] { try await base.fetchAll() }
  func fetchByID(_ id: UUID) async throws -> AssetAccount? { try await base.fetchByID(id) }
  func insert(_ model: AssetAccount) async throws -> AssetAccount {
    var value = model
    value.editedBy = LocalUserSettings.displayName
    return try await base.insert(value)
  }
  func update(_ model: AssetAccount) async throws -> AssetAccount {
    var value = model
    value.editedBy = LocalUserSettings.displayName
    return try await base.update(value)
  }
  func delete(id: UUID) async throws { try await base.delete(id: id) }
}

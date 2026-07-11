import Foundation

struct AssetRepository: Repository {
  private let base = SupabaseRepository<Asset>(table: "assets")
  func fetchAll() async throws -> [Asset] { try await base.fetchAll() }
  func fetchByID(_ id: UUID) async throws -> Asset? { try await base.fetchByID(id) }
  func insert(_ model: Asset) async throws -> Asset { try await base.insert(model) }
  func update(_ model: Asset) async throws -> Asset { try await base.update(model) }
  func delete(id: UUID) async throws { try await base.delete(id: id) }
}

import Foundation

struct ValuationSnapshotRepository: Repository {
  private let base = SupabaseRepository<ValuationSnapshot>(table: "valuation_snapshots")
  func fetchAll() async throws -> [ValuationSnapshot] { try await base.fetchAll() }
  func fetchByID(_ id: UUID) async throws -> ValuationSnapshot? { try await base.fetchByID(id) }
  func insert(_ model: ValuationSnapshot) async throws -> ValuationSnapshot {
    try await base.insert(model)
  }
  func update(_ model: ValuationSnapshot) async throws -> ValuationSnapshot {
    try await base.update(model)
  }
  func delete(id: UUID) async throws { try await base.delete(id: id) }

  func upsert(_ model: ValuationSnapshot) async throws -> ValuationSnapshot {
    let saved: ValuationSnapshot = try await SupabaseClientProvider.shared.from(
      "valuation_snapshots"
    )
    .upsert(model, onConflict: "date").select().single().execute().value
    try await OfflineStore.shared.cache(entityType: "valuation_snapshots", model: saved)
    return saved
  }
}

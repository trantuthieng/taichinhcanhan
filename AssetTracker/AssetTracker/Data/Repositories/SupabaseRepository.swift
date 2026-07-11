import Foundation
import Supabase

struct SupabaseRepository<Model>: Repository
where Model: Codable & Identifiable & Sendable, Model.ID == UUID {
  let table: String
  private let client: SupabaseClient
  private let store: OfflineStore

  init(
    table: String, client: SupabaseClient = SupabaseClientProvider.shared,
    store: OfflineStore = .shared
  ) {
    self.table = table
    self.client = client
    self.store = store
  }

  func fetchAll() async throws -> [Model] {
    do {
      let models: [Model] = try await client.from(table).select().execute().value
      try await store.replaceCache(entityType: table, models: models)
      return models
    } catch  where Self.isNetworkError(error) {
      return try await store.cachedModels(entityType: table)
    }
  }

  func fetchByID(_ id: UUID) async throws -> Model? {
    do {
      let models: [Model] = try await client.from(table).select().eq("id", value: id).limit(1)
        .execute().value
      if let model = models.first { try await store.cache(entityType: table, model: model) }
      return models.first
    } catch  where Self.isNetworkError(error) {
      return try await store.cachedModel(entityType: table, id: id)
    }
  }

  func insert(_ model: Model) async throws -> Model {
    do {
      let saved: Model = try await client.from(table).insert(model).select().single().execute()
        .value
      try await store.cache(entityType: table, model: saved)
      return saved
    } catch  where Self.isNetworkError(error) {
      try await store.cache(entityType: table, model: model)
      try await store.enqueue(entityType: table, operation: .insert, model: model)
      return model
    }
  }

  func update(_ model: Model) async throws -> Model {
    do {
      let saved: Model = try await client.from(table).update(model).eq("id", value: model.id)
        .select().single().execute().value
      try await store.cache(entityType: table, model: saved)
      return saved
    } catch  where Self.isNetworkError(error) {
      try await store.cache(entityType: table, model: model)
      try await store.enqueue(entityType: table, operation: .update, model: model)
      return model
    }
  }

  func delete(id: UUID) async throws {
    do {
      try await client.from(table).delete().eq("id", value: id).execute()
      try await store.removeCached(entityType: table, id: id)
    } catch  where Self.isNetworkError(error) {
      try await store.removeCached(entityType: table, id: id)
      try await store.enqueueDelete(entityType: table, id: id)
    }
  }

  private static func isNetworkError(_ error: Error) -> Bool {
    if error is URLError { return true }
    let nsError = error as NSError
    return nsError.domain == NSURLErrorDomain
  }
}

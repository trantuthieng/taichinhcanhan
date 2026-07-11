import Foundation

protocol Repository: Sendable {
  associatedtype Model: Codable & Identifiable & Sendable where Model.ID == UUID
  func fetchAll() async throws -> [Model]
  func fetchByID(_ id: UUID) async throws -> Model?
  func insert(_ model: Model) async throws -> Model
  func update(_ model: Model) async throws -> Model
  func delete(id: UUID) async throws
}

enum RepositoryError: Error {
  case invalidResponse
}

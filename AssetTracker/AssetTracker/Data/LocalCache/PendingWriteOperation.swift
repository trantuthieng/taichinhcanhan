import Foundation
import SwiftData

enum PendingOperationType: String, Codable, Sendable { case insert, update, delete }

@Model final class PendingWriteOperation {
  @Attribute(.unique) var id: UUID
  var entityType: String
  var operationType: String
  var payloadJSON: Data
  var createdAt: Date

  init(
    id: UUID = UUID(), entityType: String, operationType: PendingOperationType, payloadJSON: Data,
    createdAt: Date = .now
  ) {
    self.id = id
    self.entityType = entityType
    self.operationType = operationType.rawValue
    self.payloadJSON = payloadJSON
    self.createdAt = createdAt
  }
}

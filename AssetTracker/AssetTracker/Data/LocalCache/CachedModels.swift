import Foundation
import SwiftData

protocol CachedPayloadModel: PersistentModel {
  var entityID: UUID { get set }
  var payloadJSON: Data { get set }
  var updatedAt: Date { get set }
  init(entityID: UUID, payloadJSON: Data, updatedAt: Date)
}

@Model final class CachedAssetAccount: CachedPayloadModel {
  @Attribute(.unique) var entityID: UUID
  var payloadJSON: Data
  var updatedAt: Date
  init(entityID: UUID, payloadJSON: Data, updatedAt: Date = .now) {
    self.entityID = entityID
    self.payloadJSON = payloadJSON
    self.updatedAt = updatedAt
  }
}
@Model final class CachedAsset: CachedPayloadModel {
  @Attribute(.unique) var entityID: UUID
  var payloadJSON: Data
  var updatedAt: Date
  init(entityID: UUID, payloadJSON: Data, updatedAt: Date = .now) {
    self.entityID = entityID
    self.payloadJSON = payloadJSON
    self.updatedAt = updatedAt
  }
}
@Model final class CachedAssetTransaction: CachedPayloadModel {
  @Attribute(.unique) var entityID: UUID
  var payloadJSON: Data
  var updatedAt: Date
  init(entityID: UUID, payloadJSON: Data, updatedAt: Date = .now) {
    self.entityID = entityID
    self.payloadJSON = payloadJSON
    self.updatedAt = updatedAt
  }
}
@Model final class CachedSavingsDeposit: CachedPayloadModel {
  @Attribute(.unique) var entityID: UUID
  var payloadJSON: Data
  var updatedAt: Date
  init(entityID: UUID, payloadJSON: Data, updatedAt: Date = .now) {
    self.entityID = entityID
    self.payloadJSON = payloadJSON
    self.updatedAt = updatedAt
  }
}
@Model final class CachedLiability: CachedPayloadModel {
  @Attribute(.unique) var entityID: UUID
  var payloadJSON: Data
  var updatedAt: Date
  init(entityID: UUID, payloadJSON: Data, updatedAt: Date = .now) {
    self.entityID = entityID
    self.payloadJSON = payloadJSON
    self.updatedAt = updatedAt
  }
}
@Model final class CachedValuationSnapshot: CachedPayloadModel {
  @Attribute(.unique) var entityID: UUID
  var payloadJSON: Data
  var updatedAt: Date
  init(entityID: UUID, payloadJSON: Data, updatedAt: Date = .now) {
    self.entityID = entityID
    self.payloadJSON = payloadJSON
    self.updatedAt = updatedAt
  }
}

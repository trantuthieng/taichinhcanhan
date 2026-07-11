import Foundation
import Network
import Supabase
import SwiftData

actor OfflineStore {
  static let shared = OfflineStore()
  private let container: ModelContainer
  private let context: ModelContext
  private let encoder = JSONEncoder()
  private let decoder = JSONDecoder()

  init() {
    do {
      container = try ModelContainer(
        for: CachedAssetAccount.self, CachedAsset.self, CachedAssetTransaction.self,
        CachedSavingsDeposit.self, CachedLiability.self, CachedValuationSnapshot.self,
        PendingWriteOperation.self)
      context = ModelContext(container)
    } catch { fatalError("Cannot create offline cache: \(error)") }
  }

  func cache<T: Codable & Identifiable>(entityType: String, model: T) throws where T.ID == UUID {
    let data = try encoder.encode(model)
    try upsert(entityType: entityType, id: model.id, payload: data)
    try context.save()
  }

  func replaceCache<T: Codable & Identifiable>(entityType: String, models: [T]) throws
  where T.ID == UUID {
    try clear(entityType: entityType)
    for model in models {
      try upsert(entityType: entityType, id: model.id, payload: encoder.encode(model))
    }
    try context.save()
  }

  func cachedModels<T: Decodable>(entityType: String) throws -> [T] {
    try payloads(entityType: entityType).map { try decoder.decode(T.self, from: $0) }
  }

  func cachedModel<T: Decodable>(entityType: String, id: UUID) throws -> T? {
    guard let payload = try payload(entityType: entityType, id: id) else { return nil }
    return try decoder.decode(T.self, from: payload)
  }

  func removeCached(entityType: String, id: UUID) throws {
    try deleteCached(entityType: entityType, id: id)
    try context.save()
  }

  func enqueue<T: Encodable>(entityType: String, operation: PendingOperationType, model: T) throws {
    context.insert(
      PendingWriteOperation(
        entityType: entityType, operationType: operation, payloadJSON: try encoder.encode(model)))
    try context.save()
  }

  func enqueueDelete(entityType: String, id: UUID) throws {
    context.insert(
      PendingWriteOperation(
        entityType: entityType, operationType: .delete, payloadJSON: try encoder.encode(id)))
    try context.save()
  }

  func pendingOperations() throws -> [PendingWriteOperation] {
    var descriptor = FetchDescriptor<PendingWriteOperation>()
    descriptor.sortBy = [SortDescriptor(\.createdAt)]
    return try context.fetch(descriptor)
  }

  func complete(_ operation: PendingWriteOperation) throws {
    context.delete(operation)
    try context.save()
  }

  private func upsert(entityType: String, id: UUID, payload: Data) throws {
    try deleteCached(entityType: entityType, id: id)
    switch entityType {
    case "asset_accounts": context.insert(CachedAssetAccount(entityID: id, payloadJSON: payload))
    case "assets": context.insert(CachedAsset(entityID: id, payloadJSON: payload))
    case "asset_transactions":
      context.insert(CachedAssetTransaction(entityID: id, payloadJSON: payload))
    case "savings_deposits":
      context.insert(CachedSavingsDeposit(entityID: id, payloadJSON: payload))
    case "liabilities": context.insert(CachedLiability(entityID: id, payloadJSON: payload))
    case "valuation_snapshots":
      context.insert(CachedValuationSnapshot(entityID: id, payloadJSON: payload))
    default: break
    }
  }

  private func payloads(entityType: String) throws -> [Data] {
    switch entityType {
    case "asset_accounts":
      return try context.fetch(FetchDescriptor<CachedAssetAccount>()).map(\.payloadJSON)
    case "assets": return try context.fetch(FetchDescriptor<CachedAsset>()).map(\.payloadJSON)
    case "asset_transactions":
      return try context.fetch(FetchDescriptor<CachedAssetTransaction>()).map(\.payloadJSON)
    case "savings_deposits":
      return try context.fetch(FetchDescriptor<CachedSavingsDeposit>()).map(\.payloadJSON)
    case "liabilities":
      return try context.fetch(FetchDescriptor<CachedLiability>()).map(\.payloadJSON)
    case "valuation_snapshots":
      return try context.fetch(FetchDescriptor<CachedValuationSnapshot>()).map(\.payloadJSON)
    default: return []
    }
  }

  private func payload(entityType: String, id: UUID) throws -> Data? {
    switch entityType {
    case "asset_accounts":
      return try context.fetch(
        FetchDescriptor<CachedAssetAccount>(predicate: #Predicate { $0.entityID == id })
      ).first?.payloadJSON
    case "assets":
      return try context.fetch(
        FetchDescriptor<CachedAsset>(predicate: #Predicate { $0.entityID == id })
      ).first?.payloadJSON
    case "asset_transactions":
      return try context.fetch(
        FetchDescriptor<CachedAssetTransaction>(predicate: #Predicate { $0.entityID == id })
      ).first?.payloadJSON
    case "savings_deposits":
      return try context.fetch(
        FetchDescriptor<CachedSavingsDeposit>(predicate: #Predicate { $0.entityID == id })
      ).first?.payloadJSON
    case "liabilities":
      return try context.fetch(
        FetchDescriptor<CachedLiability>(predicate: #Predicate { $0.entityID == id })
      ).first?.payloadJSON
    case "valuation_snapshots":
      return try context.fetch(
        FetchDescriptor<CachedValuationSnapshot>(predicate: #Predicate { $0.entityID == id })
      ).first?.payloadJSON
    default: return nil
    }
  }

  private func deleteCached(entityType: String, id: UUID) throws {
    switch entityType {
    case "asset_accounts":
      try context.fetch(
        FetchDescriptor<CachedAssetAccount>(predicate: #Predicate { $0.entityID == id })
      ).forEach(context.delete)
    case "assets":
      try context.fetch(FetchDescriptor<CachedAsset>(predicate: #Predicate { $0.entityID == id }))
        .forEach(context.delete)
    case "asset_transactions":
      try context.fetch(
        FetchDescriptor<CachedAssetTransaction>(predicate: #Predicate { $0.entityID == id })
      ).forEach(context.delete)
    case "savings_deposits":
      try context.fetch(
        FetchDescriptor<CachedSavingsDeposit>(predicate: #Predicate { $0.entityID == id })
      ).forEach(context.delete)
    case "liabilities":
      try context.fetch(
        FetchDescriptor<CachedLiability>(predicate: #Predicate { $0.entityID == id })
      ).forEach(context.delete)
    case "valuation_snapshots":
      try context.fetch(
        FetchDescriptor<CachedValuationSnapshot>(predicate: #Predicate { $0.entityID == id })
      ).forEach(context.delete)
    default: break
    }
  }

  private func clear(entityType: String) throws {
    switch entityType {
    case "asset_accounts": try context.delete(model: CachedAssetAccount.self)
    case "assets": try context.delete(model: CachedAsset.self)
    case "asset_transactions": try context.delete(model: CachedAssetTransaction.self)
    case "savings_deposits": try context.delete(model: CachedSavingsDeposit.self)
    case "liabilities": try context.delete(model: CachedLiability.self)
    case "valuation_snapshots": try context.delete(model: CachedValuationSnapshot.self)
    default: break
    }
  }
}

actor OfflineSyncManager {
  static let shared = OfflineSyncManager()
  private let monitor = NWPathMonitor()
  private let queue = DispatchQueue(label: "AssetTracker.OfflineSync")
  private let store = OfflineStore.shared
  private let decoder = JSONDecoder()

  func start() {
    monitor.pathUpdateHandler = { path in
      guard path.status == .satisfied else { return }
      Task { try? await OfflineSyncManager.shared.flushPendingWrites() }
    }
    monitor.start(queue: queue)
  }

  func flushPendingWrites() async throws {
    for operation in try await store.pendingOperations() {
      do {
        try await replay(operation)
        try await store.complete(operation)
      } catch { break }
    }
  }

  private func replay(_ operation: PendingWriteOperation) async throws {
    let table = SupabaseClientProvider.shared.from(operation.entityType)
    guard let type = PendingOperationType(rawValue: operation.operationType) else { return }
    if type == .delete {
      let id = try decoder.decode(UUID.self, from: operation.payloadJSON)
      try await table.delete().eq("id", value: id).execute()
      return
    }
    switch operation.entityType {
    case "asset_accounts":
      try await replayModel(
        try decoder.decode(AssetAccount.self, from: operation.payloadJSON), type: type, table: table
      )
    case "assets":
      try await replayModel(
        try decoder.decode(Asset.self, from: operation.payloadJSON), type: type, table: table)
    case "asset_transactions":
      try await replayModel(
        try decoder.decode(AssetTransaction.self, from: operation.payloadJSON), type: type,
        table: table)
    case "savings_deposits":
      try await replayModel(
        try decoder.decode(SavingsDeposit.self, from: operation.payloadJSON), type: type,
        table: table)
    case "liabilities":
      try await replayModel(
        try decoder.decode(Liability.self, from: operation.payloadJSON), type: type, table: table)
    case "valuation_snapshots":
      try await replayModel(
        try decoder.decode(ValuationSnapshot.self, from: operation.payloadJSON), type: type,
        table: table)
    default: throw RepositoryError.invalidResponse
    }
  }

  private func replayModel<T: Encodable & Identifiable>(
    _ model: T, type: PendingOperationType, table: PostgrestQueryBuilder
  ) async throws where T.ID == UUID {
    if type == .insert {
      try await table.insert(model).execute()
    } else {
      try await table.update(model).eq("id", value: model.id).execute()
    }
  }
}

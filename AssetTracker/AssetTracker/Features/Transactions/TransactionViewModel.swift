import Foundation
import Observation

@MainActor @Observable
final class TransactionViewModel {
  private let transactionRepository = AssetTransactionRepository()
  private let accountRepository = AssetAccountRepository()
  private let assetRepository = AssetRepository()
  private let savingsRepository = SavingsDepositRepository()
  var transactions: [AssetTransaction] = []
  var accounts: [AssetAccount] = []
  var assets: [Asset] = []
  var deposits: [SavingsDeposit] = []
  var errorMessage: String?

  func load() async {
    do {
      async let t = transactionRepository.fetchAll()
      async let a = accountRepository.fetchAll()
      async let i = assetRepository.fetchAll()
      async let s = savingsRepository.fetchAll()
      (transactions, accounts, assets, deposits) = try await (t, a, i, s)
      transactions.sort { $0.date > $1.date }
    } catch { errorMessage = error.localizedDescription }
  }

  func add(_ value: AssetTransaction) async -> Bool {
    do {
      _ = try await transactionRepository.insert(value)
      await load()
      return true
    } catch {
      errorMessage = error.localizedDescription
      return false
    }
  }
  func delete(at offsets: IndexSet) async {
    for i in offsets { try? await transactionRepository.delete(id: transactions[i].id) }
    await load()
  }
  func holding(for assetID: UUID) async throws -> (quantity: Decimal, averageCost: Decimal) {
    try await transactionRepository.computeCurrentQuantityAndCost(forAssetID: assetID)
  }
  func mature(_ deposit: SavingsDeposit, early: Bool, rate: Decimal) async -> Bool {
    do {
      let days = max(
        0,
        Calendar.current.dateComponents(
          [.day], from: deposit.startDate, to: early ? Date() : deposit.maturityDate
        ).day ?? 0)
      let interest =
        early
        ? FinanceCalculator.earlyWithdrawalInterest(
          principal: deposit.principal, noTermRate: rate, actualDays: days)
        : FinanceCalculator.expectedInterestAtMaturity(
          principal: deposit.principal, annualRate: deposit.annualInterestRate, days: days)
      var updated = deposit
      updated.status = early ? .withdrawnEarly : .matured
      updated.updatedAt = .now
      _ = try await savingsRepository.update(updated)
      let tx = AssetTransaction(
        id: UUID(), assetID: nil, type: .maturity, date: .now, quantity: nil, unitPrice: nil,
        amount: deposit.principal + interest, fee: 0, tax: 0, sourceAccountID: nil,
        destinationAccountID: deposit.accountID,
        note: early ? "Tất toán trước hạn" : "Tất toán đúng hạn", attachmentURL: nil,
        createdAt: .now)
      do { _ = try await transactionRepository.insert(tx) } catch {
        var rollback = deposit
        rollback.updatedAt = .now
        _ = try? await savingsRepository.update(rollback)
        throw error
      }
      await load()
      return true
    } catch {
      errorMessage = error.localizedDescription
      return false
    }
  }
}

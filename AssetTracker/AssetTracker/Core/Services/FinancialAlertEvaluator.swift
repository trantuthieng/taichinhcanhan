import Foundation

struct FinancialAlertEvaluator {
  func evaluate() async {
    do {
      let threshold = Decimal(
        UserDefaults.standard.double(forKey: "concentrationThreshold") == 0
          ? 30 : UserDefaults.standard.double(forKey: "concentrationThreshold"))
      for exposure in try await ConcentrationAnalyzer().analyze() {
        await ReminderScheduler.shared.notifyConcentration(
          name: exposure.name, percentage: exposure.percentage, threshold: threshold)
      }
      let pnlThreshold = Decimal(
        UserDefaults.standard.double(forKey: "profitLossThreshold") == 0
          ? 20 : UserDefaults.standard.double(forKey: "profitLossThreshold"))
      let assets = try await AssetRepository().fetchAll()
      let repo = AssetTransactionRepository()
      for asset in assets {
        let position = try await repo.computeCurrentQuantityAndCost(forAssetID: asset.id)
        guard position.quantity > 0, position.averageCost > 0 else { continue }
        let rate = FinanceCalculator.profitRate(
          profitLoss: (asset.currentPrice - position.averageCost) * position.quantity,
          cost: position.averageCost * position.quantity)
        await ReminderScheduler.shared.notifyProfitLoss(
          asset: asset, rate: rate, threshold: pnlThreshold)
      }
      await evaluateCreditCards(transactions: try await repo.fetchAll())
    } catch {}
  }

  // note.txt mục 5.3.4 — tỷ lệ sử dụng hạn mức + chuỗi trả tối thiểu của thẻ tín dụng.
  private func evaluateCreditCards(transactions: [AssetTransaction]) async {
    let utilThreshold = Decimal(
      UserDefaults.standard.double(forKey: "creditUtilizationThreshold") == 0
        ? 80 : UserDefaults.standard.double(forKey: "creditUtilizationThreshold"))
    guard let cards = try? await LiabilityRepository().fetchAll() else { return }
    for card in cards where card.liabilityType == .creditCard {
      if let limit = card.creditLimit, limit > 0 {
        let utilization = FinanceCalculator.creditUtilization(
          currentBalance: card.currentBalance, creditLimit: limit)
        await ReminderScheduler.shared.notifyCreditUtilization(
          cardName: card.name, utilization: utilization, threshold: utilThreshold)
      }
      let recent =
        transactions
        .filter { $0.type == .repayment && $0.liabilityID == card.id }
        .sorted { $0.date > $1.date }
      var streak = 0
      for tx in recent {
        if tx.paymentType == .minimum { streak += 1 } else { break }
      }
      await ReminderScheduler.shared.notifyMinimumPaymentStreak(cardName: card.name, streak: streak)
    }
  }
}

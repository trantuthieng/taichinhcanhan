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
    } catch {}
  }
}

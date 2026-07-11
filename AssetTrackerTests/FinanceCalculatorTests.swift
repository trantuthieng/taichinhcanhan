import XCTest

@testable import AssetTracker

final class FinanceCalculatorTests: XCTestCase {
  func testAverageCost() {
    let result = FinanceCalculator.averageCost(lots: [(1000, 24_000, 0), (500, 26_000, 0)])
    XCTAssertEqual(result.rounded(scale: 2), Decimal(string: "24666.67"))
  }

  func testAverageCostIncludesFeesAndHandlesEmptyLots() {
    XCTAssertEqual(FinanceCalculator.averageCost(lots: []), 0)
    XCTAssertEqual(FinanceCalculator.averageCost(lots: [(10, 100, 100)]), 110)
  }

  func testProfitLossAndRate() {
    XCTAssertEqual(FinanceCalculator.profitLoss(currentValue: 120, remainingCost: 100), 20)
    XCTAssertEqual(FinanceCalculator.profitRate(profitLoss: 20, cost: 100), 20)
    XCTAssertEqual(FinanceCalculator.profitRate(profitLoss: 20, cost: 0), 0)
  }

  func testSavingsInterest() {
    XCTAssertEqual(
      FinanceCalculator.expectedInterestAtMaturity(
        principal: 100_000_000, annualRate: 6, days: 365), 6_000_000)
    XCTAssertEqual(
      FinanceCalculator.monthlyInterest(principal: 100_000_000, annualRate: 6), 500_000)
    XCTAssertEqual(
      FinanceCalculator.earlyWithdrawalInterest(
        principal: 100_000_000, noTermRate: 0.2, actualDays: 365), 200_000)
  }

  func testStockSellTax() {
    XCTAssertEqual(FinanceCalculator.stockSellTax(sellValue: 100_000_000), 100_000)
  }

  func testForeignExchange() {
    XCTAssertEqual(FinanceCalculator.fxConvertedValue(amount: 100, exchangeRate: 25_000), 2_500_000)
    XCTAssertEqual(
      FinanceCalculator.fxGainLoss(currentRate: 25_000, rateAtReceipt: 24_000, amount: 100), 100_000
    )
  }
}

extension Decimal {
  fileprivate func rounded(scale: Int) -> Decimal {
    var source = self
    var result = Decimal()
    NSDecimalRound(&result, &source, scale, .plain)
    return result
  }
}

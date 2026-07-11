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

  // MARK: - Nợ phải trả (mục 5)

  func testEqualPrincipalSchedule() {
    let rows = FinanceCalculator.equalPrincipalSchedule(
      principal: 120_000_000, annualRate: 12, termInMonths: 12, startDate: Date())
    XCTAssertEqual(rows.count, 12)
    XCTAssertEqual(rows[0].principalDue, 10_000_000)
    XCTAssertEqual(rows[0].interestDue, 1_200_000)
    XCTAssertEqual(rows[0].totalDue, 11_200_000)
    XCTAssertEqual(rows[0].remainingBalance, 110_000_000)
    XCTAssertEqual(rows[11].remainingBalance, 0)
    let totalPrincipal = rows.reduce(Decimal.zero) { $0 + $1.principalDue }
    XCTAssertEqual(totalPrincipal, 120_000_000)
  }

  func testAnnuityPayment() {
    XCTAssertEqual(
      FinanceCalculator.annuityPayment(remainingBalance: 12_000_000, annualRate: 0, remainingPeriods: 12),
      1_000_000)
    let pmt = FinanceCalculator.annuityPayment(
      remainingBalance: 100_000_000, annualRate: 12, remainingPeriods: 12)
    XCTAssertEqual(pmt.rounded(scale: 0), 8_884_879)
  }

  func testAnnuityScheduleClearsBalance() {
    let rows = FinanceCalculator.annuitySchedule(
      principal: 100_000_000, annualRate: 12, termInMonths: 12, startDate: Date())
    XCTAssertEqual(rows.count, 12)
    XCTAssertEqual(rows[11].remainingBalance, 0)
    // Annuity payments are repeating decimals; the telescoped principal sums back to the
    // original within a sub-cent rounding epsilon, so compare at whole-dong precision.
    let totalPrincipal = rows.reduce(Decimal.zero) { $0 + $1.principalDue }
    XCTAssertEqual(totalPrincipal.rounded(0), 100_000_000)
  }

  func testEarlyRepaymentFee() {
    XCTAssertEqual(
      FinanceCalculator.earlyRepaymentFee(prepaidAmount: 100_000_000, feeRate: 2), 2_000_000)
  }

  func testCreditCardMinimumPayment() {
    XCTAssertEqual(
      FinanceCalculator.creditCardMinimumPayment(
        currentBalance: 15_000_000, minRate: 5, minFixedAmount: 100_000), 750_000)
    XCTAssertEqual(
      FinanceCalculator.creditCardMinimumPayment(
        currentBalance: 1_000_000, minRate: 5, minFixedAmount: 100_000), 100_000)
  }

  func testCreditUtilization() {
    XCTAssertEqual(
      FinanceCalculator.creditUtilization(currentBalance: 15_000_000, creditLimit: 100_000_000), 15)
    XCTAssertEqual(
      FinanceCalculator.creditUtilization(currentBalance: 15_000_000, creditLimit: 0), 0)
  }

  func testEstimatedInterestIfUnderpaid() {
    XCTAssertEqual(
      FinanceCalculator.estimatedInterestIfUnderpaid(balance: 15_000_000, annualRate: 28, days: 30)
        .rounded(scale: 2),
      Decimal(string: "345205.48"))
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

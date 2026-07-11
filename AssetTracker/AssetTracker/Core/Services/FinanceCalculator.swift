import Foundation

enum FinanceCalculator {
  static func averageCost(lots: [(quantity: Decimal, unitPrice: Decimal, fee: Decimal)]) -> Decimal
  {
    let quantity = lots.reduce(Decimal.zero) { $0 + $1.quantity }
    guard quantity != 0 else { return 0 }
    let cost = lots.reduce(Decimal.zero) { $0 + $1.quantity * $1.unitPrice + $1.fee }
    return cost / quantity
  }

  static func profitLoss(currentValue: Decimal, remainingCost: Decimal) -> Decimal {
    currentValue - remainingCost
  }
  static func profitRate(profitLoss: Decimal, cost: Decimal) -> Decimal {
    cost == 0 ? 0 : profitLoss / cost * 100
  }

  static func expectedInterestAtMaturity(principal: Decimal, annualRate: Decimal, days: Int)
    -> Decimal
  {
    principal * annualRate / 100 * Decimal(days) / 365
  }

  static func monthlyInterest(principal: Decimal, annualRate: Decimal) -> Decimal {
    principal * annualRate / 100 / 12
  }

  static func earlyWithdrawalInterest(principal: Decimal, noTermRate: Decimal, actualDays: Int)
    -> Decimal
  {
    principal * noTermRate / 100 * Decimal(actualDays) / 365
  }

  static func stockSellTax(sellValue: Decimal) -> Decimal { sellValue * Decimal(string: "0.001")! }
  static func fxConvertedValue(amount: Decimal, exchangeRate: Decimal) -> Decimal {
    amount * exchangeRate
  }
  static func fxGainLoss(currentRate: Decimal, rateAtReceipt: Decimal, amount: Decimal) -> Decimal {
    (currentRate - rateAtReceipt) * amount
  }
}

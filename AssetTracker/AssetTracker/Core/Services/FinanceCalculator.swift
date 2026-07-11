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

// note.txt mục 5 — nợ phải trả
extension FinanceCalculator {
  struct AmortizationRow: Hashable, Sendable {
    let periodIndex: Int
    let dueDate: Date
    let principalDue: Decimal
    let interestDue: Decimal
    let totalDue: Decimal
    let remainingBalance: Decimal
  }

  private static func power(_ base: Decimal, _ exponent: Int) -> Decimal {
    var result: Decimal = 1
    for _ in 0..<max(0, exponent) { result *= base }
    return result
  }

  private static func dueDate(_ startDate: Date, monthsAfter months: Int) -> Date {
    Calendar.current.date(byAdding: .month, value: months, to: startDate) ?? startDate
  }

  // Nhóm A — Gốc đều (mục 5.2.2): gốc mỗi kỳ bằng nhau, lãi giảm dần theo dư nợ.
  static func equalPrincipalSchedule(
    principal: Decimal, annualRate: Decimal, termInMonths: Int, startDate: Date
  ) -> [AmortizationRow] {
    guard termInMonths > 0, principal > 0 else { return [] }
    let monthlyRate = annualRate / 100 / 12
    let principalPerPeriod = principal / Decimal(termInMonths)
    var remaining = principal
    var rows: [AmortizationRow] = []
    for period in 1...termInMonths {
      let interest = remaining * monthlyRate
      let principalDue = period == termInMonths ? remaining : principalPerPeriod
      remaining = period == termInMonths ? 0 : remaining - principalDue
      rows.append(
        AmortizationRow(
          periodIndex: period, dueDate: dueDate(startDate, monthsAfter: period),
          principalDue: principalDue, interestDue: interest,
          totalDue: principalDue + interest, remainingBalance: max(0, remaining)))
    }
    return rows
  }

  // Nhóm A — Trả đều/annuity (mục 5.2.2): mỗi kỳ trả số cố định PMT.
  static func annuityPayment(
    remainingBalance: Decimal, annualRate: Decimal, remainingPeriods: Int
  ) -> Decimal {
    guard remainingPeriods > 0 else { return 0 }
    let monthlyRate = annualRate / 100 / 12
    if monthlyRate == 0 { return remainingBalance / Decimal(remainingPeriods) }
    let growth = power(1 + monthlyRate, remainingPeriods)
    return remainingBalance * monthlyRate * growth / (growth - 1)
  }

  static func annuitySchedule(
    principal: Decimal, annualRate: Decimal, termInMonths: Int, startDate: Date
  ) -> [AmortizationRow] {
    guard termInMonths > 0, principal > 0 else { return [] }
    let monthlyRate = annualRate / 100 / 12
    let payment = annuityPayment(
      remainingBalance: principal, annualRate: annualRate, remainingPeriods: termInMonths)
    var remaining = principal
    var rows: [AmortizationRow] = []
    for period in 1...termInMonths {
      let interest = remaining * monthlyRate
      let principalDue = period == termInMonths ? remaining : payment - interest
      remaining = period == termInMonths ? 0 : remaining - principalDue
      rows.append(
        AmortizationRow(
          periodIndex: period, dueDate: dueDate(startDate, monthsAfter: period),
          principalDue: principalDue, interestDue: interest,
          totalDue: principalDue + interest, remainingBalance: max(0, remaining)))
    }
    return rows
  }

  static func earlyRepaymentFee(prepaidAmount: Decimal, feeRate: Decimal) -> Decimal {
    prepaidAmount * feeRate / 100
  }

  // Nhóm B — thẻ tín dụng (mục 5.3.3)
  static func creditCardMinimumPayment(
    currentBalance: Decimal, minRate: Decimal, minFixedAmount: Decimal
  ) -> Decimal {
    guard currentBalance > 0 else { return 0 }
    return max(currentBalance * minRate / 100, minFixedAmount)
  }

  static func creditUtilization(currentBalance: Decimal, creditLimit: Decimal) -> Decimal {
    creditLimit == 0 ? 0 : currentBalance / creditLimit * 100
  }

  static func estimatedInterestIfUnderpaid(balance: Decimal, annualRate: Decimal, days: Int)
    -> Decimal
  {
    balance * annualRate / 100 / 365 * Decimal(days)
  }
}

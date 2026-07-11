import Foundation

struct Liability: Codable, Identifiable, Hashable, Sendable {
  var id: UUID
  var name: String
  var lender: String? = nil
  var liabilityType: LiabilityType = .otherPayable
  var currency: CurrencyCode = .vnd
  var originalPrincipal: Decimal
  var currentBalance: Decimal
  var annualInterestRate: Decimal
  var interestRateType: InterestRateType? = nil
  var fixedRateEndDate: Date? = nil
  var repaymentMethod: RepaymentMethod? = nil
  var termInMonths: Int? = nil
  var earlyRepaymentFeeRate: Decimal? = nil
  var gracePeriodMonths: Int? = nil
  var startDate: Date
  var maturityDate: Date? = nil
  var paymentFrequency: PaymentFrequency? = nil
  var nextPaymentDate: Date? = nil
  var monthlyPayment: Decimal? = nil
  // Nhóm B — thẻ tín dụng
  var creditLimit: Decimal? = nil
  var statementDay: Int? = nil
  var paymentDueDay: Int? = nil
  var interestFreeDays: Int? = nil
  var minPaymentRate: Decimal? = nil
  var minPaymentFixedAmount: Decimal? = nil
  var annualFee: Decimal? = nil
  var lateFee: Decimal? = nil
  var lastStatementBalance: Decimal? = nil
  var lastStatementDate: Date? = nil
  var collateral: String? = nil
  var note: String? = nil
  var createdAt: Date
  var updatedAt: Date
  var editedBy: String? = nil

  enum CodingKeys: String, CodingKey {
    case id, name, lender, currency, collateral, note
    case liabilityType = "liability_type"
    case originalPrincipal = "original_principal"
    case currentBalance = "current_balance"
    case annualInterestRate = "annual_interest_rate"
    case interestRateType = "interest_rate_type"
    case fixedRateEndDate = "fixed_rate_end_date"
    case repaymentMethod = "repayment_method"
    case termInMonths = "term_in_months"
    case earlyRepaymentFeeRate = "early_repayment_fee_rate"
    case gracePeriodMonths = "grace_period_months"
    case startDate = "start_date"
    case maturityDate = "maturity_date"
    case paymentFrequency = "payment_frequency"
    case nextPaymentDate = "next_payment_date"
    case monthlyPayment = "monthly_payment"
    case creditLimit = "credit_limit"
    case statementDay = "statement_day"
    case paymentDueDay = "payment_due_day"
    case interestFreeDays = "interest_free_days"
    case minPaymentRate = "min_payment_rate"
    case minPaymentFixedAmount = "min_payment_fixed_amount"
    case annualFee = "annual_fee"
    case lateFee = "late_fee"
    case lastStatementBalance = "last_statement_balance"
    case lastStatementDate = "last_statement_date"
    case createdAt = "created_at"
    case updatedAt = "updated_at"
    case editedBy = "edited_by"
  }
}

extension Liability {
  /// Lịch trả nợ dự kiến cho nợ Nhóm A (vay có kỳ hạn), sinh từ FinanceCalculator.
  var amortizationSchedule: [FinanceCalculator.AmortizationRow] {
    guard liabilityType.group == .termLoan, let term = termInMonths, term > 0 else { return [] }
    switch repaymentMethod ?? .annuity {
    case .equalPrincipal:
      return FinanceCalculator.equalPrincipalSchedule(
        principal: originalPrincipal, annualRate: annualInterestRate, termInMonths: term,
        startDate: startDate)
    case .annuity:
      return FinanceCalculator.annuitySchedule(
        principal: originalPrincipal, annualRate: annualInterestRate, termInMonths: term,
        startDate: startDate)
    }
  }
}

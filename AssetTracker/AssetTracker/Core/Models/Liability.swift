import Foundation

struct Liability: Codable, Identifiable, Hashable, Sendable {
  var id: UUID
  var name: String
  var lender: String?
  var originalPrincipal: Decimal
  var currentBalance: Decimal
  var annualInterestRate: Decimal
  var startDate: Date
  var maturityDate: Date?
  var paymentFrequency: PaymentFrequency?
  var nextPaymentDate: Date?
  var monthlyPayment: Decimal?
  var collateral: String?
  var note: String?
  var createdAt: Date
  var updatedAt: Date
  var editedBy: String? = nil

  enum CodingKeys: String, CodingKey {
    case id, name, lender, collateral, note
    case originalPrincipal = "original_principal"
    case currentBalance = "current_balance"
    case annualInterestRate = "annual_interest_rate"
    case startDate = "start_date"
    case maturityDate = "maturity_date"
    case paymentFrequency = "payment_frequency"
    case nextPaymentDate = "next_payment_date"
    case monthlyPayment = "monthly_payment"
    case createdAt = "created_at"
    case updatedAt = "updated_at"
    case editedBy = "edited_by"
  }
}

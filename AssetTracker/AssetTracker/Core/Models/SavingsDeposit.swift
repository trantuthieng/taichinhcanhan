import Foundation

struct SavingsDeposit: Codable, Identifiable, Hashable, Sendable {
  var id: UUID
  var name: String
  var bankName: String
  var principal: Decimal
  var currency: CurrencyCode
  var annualInterestRate: Decimal
  var startDate: Date
  var maturityDate: Date
  var termInMonths: Int
  var interestPaymentType: InterestPaymentType
  var autoRenewalType: AutoRenewalType?
  var earlyWithdrawalRate: Decimal?
  var status: DepositStatus
  var contractNumber: String?
  var attachmentURL: String?
  var accountID: UUID?
  var createdAt: Date
  var updatedAt: Date
  var editedBy: String? = nil

  enum CodingKeys: String, CodingKey {
    case id, name, principal, currency, status
    case bankName = "bank_name"
    case annualInterestRate = "annual_interest_rate"
    case startDate = "start_date"
    case maturityDate = "maturity_date"
    case termInMonths = "term_in_months"
    case interestPaymentType = "interest_payment_type"
    case autoRenewalType = "auto_renewal_type"
    case earlyWithdrawalRate = "early_withdrawal_rate"
    case contractNumber = "contract_number"
    case attachmentURL = "attachment_url"
    case accountID = "account_id"
    case createdAt = "created_at"
    case updatedAt = "updated_at"
    case editedBy = "edited_by"
  }
}

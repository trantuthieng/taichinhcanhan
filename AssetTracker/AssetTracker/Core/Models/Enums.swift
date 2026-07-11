import Foundation

enum AccountType: String, Codable, CaseIterable, Sendable {
  case cashPersonal = "cash_personal"
  case cashFamily = "cash_family"
  case bankAccount = "bank_account"
  case salaryAccount = "salary_account"
  case spendingAccount = "spending_account"
  case eWallet = "e_wallet"
  case emergencyFund = "emergency_fund"
  case travelFund = "travel_fund"
  case investmentFund = "investment_fund"
  case foreignCurrencyCash = "foreign_currency_cash"
}

enum AssetCategory: String, Codable, CaseIterable, Sendable {
  case stock
  case fundCertificate = "fund_certificate"
  case etf
  case listedBond = "listed_bond"
  case warrant
  case foreignStock = "foreign_stock"
  case openEndFund = "open_end_fund"
  case otherSecurity = "other_security"
  case goldBarSJC = "gold_bar_sjc"
  case goldRing9999 = "gold_ring_9999"
  case goldBarOtherBrand = "gold_bar_other_brand"
  case goldJewelry = "gold_jewelry"
  case gold24K = "gold_24k"
  case gold18K = "gold_18k"
  case gold14K = "gold_14k"
  case goldInternational = "gold_international"
  case otherGold = "other_gold"
  case realEstate = "real_estate"
  case car, motorbike
  case nonListedBond = "non_listed_bond"
  case crypto
  case insuranceCashValue = "insurance_cash_value"
  case loanReceivable = "loan_receivable"
  case businessEquity = "business_equity"
  case collectible
  case digitalAsset = "digital_asset"
  case rentalAsset = "rental_asset"
}

enum AssetUnit: String, Codable, CaseIterable, Sendable {
  case share, luong, cay, chi, phan, gram, ounce, item
}
enum CurrencyCode: String, Codable, CaseIterable, Sendable {
  case vnd = "VND"
  case usd = "USD"
  case eur = "EUR"
  case jpy = "JPY"
  case aud = "AUD"
  case cad = "CAD"
  case sgd = "SGD"
  case cny = "CNY"
  case krw = "KRW"
  case other = "OTHER"
}
enum TransactionType: String, Codable, CaseIterable, Sendable {
  case deposit, withdrawal, transfer, buy, sell, interest, dividend, maturity, repayment, fee, tax,
    adjustment
}
enum InterestPaymentType: String, Codable, CaseIterable, Sendable {
  case endOfTerm = "end_of_term"
  case monthly, upfront
}
enum AutoRenewalType: String, Codable, CaseIterable, Sendable {
  case none
  case principalOnly = "principal_only"
  case principalAndInterest = "principal_and_interest"
}
enum DepositStatus: String, Codable, CaseIterable, Sendable {
  case active, matured, closed
  case withdrawnEarly = "withdrawn_early"
}
enum PaymentFrequency: String, Codable, CaseIterable, Sendable {
  case monthly, quarterly
  case semiAnnual = "semi_annual"
  case annual
  case oneTime = "one_time"
}

// note.txt mục 5 — nợ phải trả
enum LiabilityType: String, Codable, CaseIterable, Sendable {
  case mortgageLoan = "mortgage_loan"
  case carLoan = "car_loan"
  case consumerLoan = "consumer_loan"
  case unsecuredLoan = "unsecured_loan"
  case familyLoan = "family_loan"
  case installmentPlan = "installment_plan"
  case creditCard = "credit_card"
  case otherPayable = "other_payable"

  enum Group: String, Sendable { case termLoan, creditCard, otherPayable }

  var group: Group {
    switch self {
    case .creditCard: return .creditCard
    case .otherPayable: return .otherPayable
    default: return .termLoan
    }
  }

  var label: String {
    switch self {
    case .mortgageLoan: return "Vay mua nhà"
    case .carLoan: return "Vay mua xe"
    case .consumerLoan: return "Vay tiêu dùng"
    case .unsecuredLoan: return "Vay tín chấp"
    case .familyLoan: return "Vay người thân"
    case .installmentPlan: return "Trả góp"
    case .creditCard: return "Thẻ tín dụng"
    case .otherPayable: return "Khoản phải trả khác"
    }
  }
}

enum InterestRateType: String, Codable, CaseIterable, Sendable {
  case fixed, floating
  var label: String { self == .fixed ? "Cố định" : "Thả nổi" }
}

enum RepaymentMethod: String, Codable, CaseIterable, Sendable {
  case equalPrincipal = "equal_principal"
  case annuity
  var label: String { self == .equalPrincipal ? "Gốc đều" : "Trả đều (annuity)" }
}

enum LiabilityPaymentType: String, Codable, CaseIterable, Sendable {
  case full, minimum, partial
  var label: String {
    switch self {
    case .full: return "Trả toàn bộ"
    case .minimum: return "Trả tối thiểu"
    case .partial: return "Trả số khác"
    }
  }
}

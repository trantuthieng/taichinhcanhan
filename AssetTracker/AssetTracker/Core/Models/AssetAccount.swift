import Foundation

struct AssetAccount: Codable, Identifiable, Hashable, Sendable {
  var id: UUID
  var name: String
  var institution: String?
  var accountType: AccountType
  var currency: CurrencyCode
  var balance: Decimal
  var exchangeRateAtOpening: Decimal?
  var currentExchangeRate: Decimal?
  var isIncludedInNetWorth: Bool
  var targetGroup: String?
  var note: String?
  var createdAt: Date
  var updatedAt: Date
  var editedBy: String? = nil

  enum CodingKeys: String, CodingKey {
    case id, name, institution, currency, balance, note
    case accountType = "account_type"
    case exchangeRateAtOpening = "exchange_rate_at_opening"
    case currentExchangeRate = "current_exchange_rate"
    case isIncludedInNetWorth = "is_included_in_net_worth"
    case targetGroup = "target_group"
    case createdAt = "created_at"
    case updatedAt = "updated_at"
    case editedBy = "edited_by"
  }
}

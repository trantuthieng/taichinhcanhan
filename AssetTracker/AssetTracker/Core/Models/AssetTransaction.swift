import Foundation

struct AssetTransaction: Codable, Identifiable, Hashable, Sendable {
  var id: UUID
  var assetID: UUID?
  var type: TransactionType
  var date: Date
  var quantity: Decimal?
  var unitPrice: Decimal?
  var amount: Decimal
  var fee: Decimal
  var tax: Decimal
  var sourceAccountID: UUID?
  var destinationAccountID: UUID?
  var note: String?
  var attachmentURL: String?
  var liabilityID: UUID? = nil
  var paymentType: LiabilityPaymentType? = nil
  var createdAt: Date
  var editedBy: String? = nil

  enum CodingKeys: String, CodingKey {
    case id, type, date, quantity, amount, fee, tax, note
    case assetID = "asset_id"
    case unitPrice = "unit_price"
    case sourceAccountID = "source_account_id"
    case destinationAccountID = "destination_account_id"
    case attachmentURL = "attachment_url"
    case liabilityID = "liability_id"
    case paymentType = "payment_type"
    case createdAt = "created_at"
    case editedBy = "edited_by"
  }
}

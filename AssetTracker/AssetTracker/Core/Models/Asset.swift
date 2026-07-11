import Foundation

struct Asset: Codable, Identifiable, Hashable, Sendable {
  var id: UUID
  var name: String
  var category: AssetCategory
  var accountID: UUID?
  var symbol: String?
  var brand: String?
  var unit: AssetUnit
  var quantity: Decimal
  var averageCost: Decimal
  var currentPrice: Decimal
  var currency: CurrencyCode
  var acquisitionDate: Date?
  var valuationDate: Date
  var purchaseLocation: String?
  var storageLocation: String?
  var invoiceNumber: String?
  var invoiceAttachmentURL: String?
  var grossWeight: Decimal?
  var pureGoldWeight: Decimal?
  var goldPurity: Decimal?
  var laborCost: Decimal?
  var gemstoneValue: Decimal?
  var depreciationRate: Decimal?
  var expectedBuybackPrice: Decimal?
  var note: String?
  var targetPrice: Decimal? = nil
  var valuationSource: String? = nil
  var generatedIncome: Decimal? = nil
  var relatedCost: Decimal? = nil
  var createdAt: Date
  var updatedAt: Date

  enum CodingKeys: String, CodingKey {
    case id, name, category, symbol, brand, unit, quantity, currency, note
    case accountID = "account_id"
    case averageCost = "average_cost"
    case currentPrice = "current_price"
    case acquisitionDate = "acquisition_date"
    case valuationDate = "valuation_date"
    case purchaseLocation = "purchase_location"
    case storageLocation = "storage_location"
    case invoiceNumber = "invoice_number"
    case invoiceAttachmentURL = "invoice_attachment_url"
    case grossWeight = "gross_weight"
    case pureGoldWeight = "pure_gold_weight"
    case goldPurity = "gold_purity"
    case laborCost = "labor_cost"
    case gemstoneValue = "gemstone_value"
    case depreciationRate = "depreciation_rate"
    case expectedBuybackPrice = "expected_buyback_price"
    case targetPrice = "target_price"
    case valuationSource = "valuation_source"
    case generatedIncome = "generated_income"
    case relatedCost = "related_cost"
    case createdAt = "created_at"
    case updatedAt = "updated_at"
  }
}

import Foundation

struct CSVExportService {
  func export(assets: [Asset], transactions: [AssetTransaction]) throws -> URL {
    var rows = [
      "record_type,id,name_or_type,category_or_asset_id,date,quantity,unit_price,amount,fee,tax,currency,note"
    ]
    rows += assets.map { asset in
      csv([
        "asset", asset.id.uuidString, asset.name, asset.category.rawValue,
        asset.acquisitionDate.map(Self.iso.string) ?? "", asset.quantity.description,
        asset.averageCost.description, asset.currentPrice.description, "", "",
        asset.currency.rawValue, asset.note ?? "",
      ])
    }
    rows += transactions.map { tx in
      csv([
        "transaction", tx.id.uuidString, tx.type.rawValue, tx.assetID?.uuidString ?? "",
        Self.iso.string(from: tx.date), tx.quantity?.description ?? "",
        tx.unitPrice?.description ?? "", tx.amount.description, tx.fee.description,
        tx.tax.description, "", tx.note ?? "",
      ])
    }
    let bom = "\u{FEFF}"
    let data = Data((bom + rows.joined(separator: "\r\n")).utf8)
    let url = FileManager.default.temporaryDirectory.appendingPathComponent(
      "AssetTracker-\(Self.fileDate.string(from:.now)).csv")
    try data.write(to: url, options: .atomic)
    return url
  }
  private func csv(_ fields: [String]) -> String {
    fields.map { field in "\"\(field.replacingOccurrences(of:"\"",with:"\"\""))\"" }.joined(
      separator: ",")
  }
  private static let iso: ISO8601DateFormatter = {
    let f = ISO8601DateFormatter()
    f.formatOptions = [.withInternetDateTime]
    return f
  }()
  private static let fileDate: DateFormatter = {
    let f = DateFormatter()
    f.dateFormat = "yyyy-MM-dd"
    return f
  }()
}

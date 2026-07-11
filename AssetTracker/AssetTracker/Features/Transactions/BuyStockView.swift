import SwiftUI

struct BuyStockView: View {
  @Environment(\.dismiss) private var dismiss
  let stocks: [Asset]
  let onSave: (AssetTransaction) async -> Bool
  @State private var assetID: UUID?
  @State private var quantity: Decimal = 0
  @State private var price: Decimal = 0
  @State private var fee: Decimal = 0
  @State private var date = Date()
  var body: some View {
    NavigationStack {
      Form {
        Picker("Mã", selection: $assetID) {
          Text("Chọn mã").tag(UUID?.none)
          ForEach(stocks) { Text($0.symbol ?? $0.name).tag(Optional($0.id)) }
        }
        TextField("Số lượng", value: $quantity, format: .number).keyboardType(.decimalPad)
        TextField("Giá mua", value: $price, format: .number).keyboardType(.decimalPad)
        TextField("Phí", value: $fee, format: .number).keyboardType(.decimalPad)
        DatePicker("Ngày mua", selection: $date)
      }.navigationTitle("Mua chứng khoán").toolbar {
        ToolbarItem(placement: .cancellationAction) { Button("Hủy") { dismiss() } }
        ToolbarItem(placement: .confirmationAction) {
          Button("Lưu") { Task { await save() } }.disabled(
            assetID == nil || quantity <= 0 || price <= 0)
        }
      }
    }
  }
  private func save() async {
    guard let id = assetID, let asset = stocks.first(where: { $0.id == id }) else { return }
    let tx = AssetTransaction(
      id: UUID(), assetID: id, type: .buy, date: date, quantity: quantity, unitPrice: price,
      amount: quantity * price, fee: fee, tax: 0, sourceAccountID: asset.accountID,
      destinationAccountID: nil, note: nil, attachmentURL: nil, createdAt: .now)
    if await onSave(tx) { dismiss() }
  }
}

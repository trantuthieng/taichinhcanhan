import SwiftUI

struct SellStockView: View {
  @Environment(\.dismiss) private var dismiss
  let stocks: [Asset]
  let holding: (UUID) async throws -> (quantity: Decimal, averageCost: Decimal)
  let onSave: (AssetTransaction) async -> Bool
  @State private var assetID: UUID?
  @State private var quantity: Decimal = 0
  @State private var price: Decimal = 0
  @State private var fee: Decimal = 0
  @State private var tax: Decimal = 0
  @State private var available: Decimal = 0
  @State private var error: String?
  var body: some View {
    NavigationStack {
      Form {
        Picker("Mã", selection: $assetID) {
          Text("Chọn mã").tag(UUID?.none)
          ForEach(stocks) { Text($0.symbol ?? $0.name).tag(Optional($0.id)) }
        }.onChange(of: assetID) { _, id in Task { await loadHolding(id) } }
        LabeledContent("Đang sở hữu", value: available.description)
        TextField("Số lượng bán", value: $quantity, format: .number).keyboardType(.decimalPad)
        TextField("Giá bán", value: $price, format: .number).keyboardType(.decimalPad).onChange(
          of: price
        ) { _, _ in updateTax() }
        TextField("Phí", value: $fee, format: .number).keyboardType(.decimalPad)
        TextField("Thuế", value: $tax, format: .number).keyboardType(.decimalPad)
        if let error { Text(error).foregroundStyle(.red) }
      }.navigationTitle("Bán chứng khoán").toolbar {
        ToolbarItem(placement: .cancellationAction) { Button("Hủy") { dismiss() } }
        ToolbarItem(placement: .confirmationAction) {
          Button("Lưu") { Task { await save() } }.disabled(
            assetID == nil || quantity <= 0 || quantity > available || price <= 0)
        }
      }
    }
  }
  private func updateTax() { tax = FinanceCalculator.stockSellTax(sellValue: quantity * price) }
  private func loadHolding(_ id: UUID?) async {
    guard let id else {
      available = 0
      return
    }
    do { available = try await holding(id).quantity } catch {
      self.error = error.localizedDescription
    }
  }
  private func save() async {
    guard let id = assetID else { return }
    updateTax()
    let tx = AssetTransaction(
      id: UUID(), assetID: id, type: .sell, date: .now, quantity: quantity, unitPrice: price,
      amount: quantity * price, fee: fee, tax: tax, sourceAccountID: nil,
      destinationAccountID: stocks.first { $0.id == id }?.accountID, note: nil, attachmentURL: nil,
      createdAt: .now)
    if await onSave(tx) { dismiss() }
  }
}

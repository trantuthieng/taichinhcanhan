import SwiftUI

struct TransferFundsView: View {
  @Environment(\.dismiss) private var dismiss
  let accounts: [AssetAccount]
  let onSave: (AssetTransaction) async -> Bool
  @State private var source: UUID?
  @State private var destination: UUID?
  @State private var amount: Decimal = 0
  @State private var fee: Decimal = 0
  @State private var date = Date()
  @State private var note = ""
  var body: some View {
    NavigationStack {
      Form {
        Picker("Từ tài khoản", selection: $source) {
          Text("Chọn").tag(UUID?.none)
          ForEach(accounts) { Text($0.name).tag(Optional($0.id)) }
        }
        Picker("Đến tài khoản", selection: $destination) {
          Text("Chọn").tag(UUID?.none)
          ForEach(accounts) { Text($0.name).tag(Optional($0.id)) }
        }
        TextField("Số tiền", value: $amount, format: .number).keyboardType(.decimalPad)
        TextField("Phí", value: $fee, format: .number).keyboardType(.decimalPad)
        DatePicker("Ngày", selection: $date)
        TextField("Ghi chú", text: $note)
      }.navigationTitle("Chuyển tiền").toolbar {
        ToolbarItem(placement: .cancellationAction) { Button("Hủy") { dismiss() } }
        ToolbarItem(placement: .confirmationAction) {
          Button("Chuyển") { Task { await save() } }.disabled(
            source == nil || destination == nil || source == destination || amount <= 0)
        }
      }
    }
  }
  private func save() async {
    let tx = AssetTransaction(
      id: UUID(), assetID: nil, type: .transfer, date: date, quantity: nil, unitPrice: nil,
      amount: amount, fee: fee, tax: 0, sourceAccountID: source, destinationAccountID: destination,
      note: note.nilIfEmpty, attachmentURL: nil, createdAt: .now)
    if await onSave(tx) { dismiss() }
  }
}

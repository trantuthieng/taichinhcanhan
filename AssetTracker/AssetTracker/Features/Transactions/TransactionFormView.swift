import SwiftUI

struct TransactionFormView: View {
  @Environment(\.dismiss) private var dismiss
  let accounts: [AssetAccount]
  let onSave: (AssetTransaction) async -> Bool
  @State private var type = TransactionType.deposit
  @State private var amount: Decimal = 0
  @State private var date = Date()
  @State private var accountID: UUID?
  @State private var note = ""
  var body: some View {
    NavigationStack {
      Form {
        Picker("Loại", selection: $type) {
          ForEach([TransactionType.deposit, .withdrawal, .adjustment], id: \.self) {
            Text($0.rawValue).tag($0)
          }
        }
        TextField("Số tiền", value: $amount, format: .number).keyboardType(.decimalPad)
        Picker("Tài khoản", selection: $accountID) {
          Text("Chọn tài khoản").tag(UUID?.none)
          ForEach(accounts) { Text($0.name).tag(Optional($0.id)) }
        }
        DatePicker("Ngày", selection: $date)
        TextField("Ghi chú", text: $note)
      }.navigationTitle("Giao dịch").toolbar {
        ToolbarItem(placement: .cancellationAction) { Button("Hủy") { dismiss() } }
        ToolbarItem(placement: .confirmationAction) {
          Button("Lưu") { Task { await save() } }.disabled(amount <= 0 || accountID == nil)
        }
      }
    }
  }
  private func save() async {
    let source = type == .withdrawal ? accountID : nil
    let destination = type == .deposit ? accountID : nil
    let tx = AssetTransaction(
      id: UUID(), assetID: nil, type: type, date: date, quantity: nil, unitPrice: nil,
      amount: amount, fee: 0, tax: 0, sourceAccountID: source, destinationAccountID: destination,
      note: note.nilIfEmpty, attachmentURL: nil, createdAt: .now)
    if await onSave(tx) { dismiss() }
  }
}

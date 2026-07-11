import SwiftUI

struct OtherPayableFormView: View {
  @Environment(\.dismiss) private var dismiss
  let liability: Liability?
  let onSave: (Liability, Bool) async -> Bool

  @State private var name = ""
  @State private var lender = ""
  @State private var amount: Decimal = 0
  @State private var start = Date()
  @State private var hasDue = false
  @State private var due = Date()
  @State private var note = ""

  var body: some View {
    NavigationStack {
      Form {
        Section("Khoản phải trả") {
          TextField("Tên", text: $name)
          TextField("Chủ nợ", text: $lender)
          TextField("Số tiền", value: $amount, format: .number).keyboardType(.decimalPad)
          DatePicker("Ngày phát sinh", selection: $start, displayedComponents: .date)
          Toggle("Có hạn trả dự kiến", isOn: $hasDue)
          if hasDue {
            DatePicker("Hạn trả", selection: $due, displayedComponents: .date)
          }
          TextField("Ghi chú", text: $note, axis: .vertical)
        }
      }
      .navigationTitle(liability == nil ? "Thêm khoản phải trả" : "Sửa khoản phải trả")
      .toolbar {
        ToolbarItem(placement: .cancellationAction) { Button("Hủy") { dismiss() } }
        ToolbarItem(placement: .confirmationAction) {
          Button("Lưu") { Task { await save() } }.disabled(name.isEmpty || amount <= 0)
        }
      }
      .onAppear { prefill() }
    }
  }

  private func prefill() {
    guard let x = liability else { return }
    name = x.name
    lender = x.lender ?? ""
    amount = x.currentBalance
    start = x.startDate
    if let d = x.maturityDate {
      hasDue = true
      due = d
    }
    note = x.note ?? ""
  }

  private func save() async {
    let now = Date()
    let isNew = liability == nil
    let x = Liability(
      id: liability?.id ?? UUID(), name: name, lender: lender.nilIfEmpty,
      liabilityType: .otherPayable, currency: .vnd,
      originalPrincipal: isNew ? amount : liability?.originalPrincipal ?? amount,
      currentBalance: amount, annualInterestRate: 0, startDate: start,
      maturityDate: hasDue ? due : nil, nextPaymentDate: hasDue ? due : nil,
      note: note.nilIfEmpty, createdAt: liability?.createdAt ?? now, updatedAt: now)
    if await onSave(x, isNew) { dismiss() }
  }
}

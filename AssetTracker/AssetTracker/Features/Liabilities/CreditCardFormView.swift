import SwiftUI

struct CreditCardFormView: View {
  @Environment(\.dismiss) private var dismiss
  let liability: Liability?
  let onSave: (Liability, Bool) async -> Bool

  @State private var name = ""
  @State private var bank = ""
  @State private var creditLimit: Decimal = 0
  @State private var balance: Decimal = 0
  @State private var statementDay = 15
  @State private var dueDay = 5
  @State private var interestFreeDays = 45
  @State private var rate: Decimal = 0
  @State private var minRate: Decimal = 5
  @State private var minFixed: Decimal = 0
  @State private var annualFee: Decimal = 0
  @State private var lateFee: Decimal = 0
  @State private var note = ""

  var body: some View {
    NavigationStack {
      Form {
        Section("Thẻ") {
          TextField("Tên thẻ", text: $name)
          TextField("Ngân hàng phát hành", text: $bank)
          TextField("Hạn mức tín dụng", value: $creditLimit, format: .number)
            .keyboardType(.decimalPad)
          TextField("Dư nợ hiện tại", value: $balance, format: .number).keyboardType(.decimalPad)
        }
        Section("Kỳ sao kê") {
          Stepper("Ngày sao kê: \(statementDay)", value: $statementDay, in: 1...31)
          Stepper("Ngày đến hạn: \(dueDay)", value: $dueDay, in: 1...31)
          Stepper("Số ngày miễn lãi: \(interestFreeDays)", value: $interestFreeDays, in: 0...60)
        }
        Section("Lãi & phí") {
          TextField("Lãi suất %/năm", value: $rate, format: .number).keyboardType(.decimalPad)
          TextField("Tỷ lệ thanh toán tối thiểu %", value: $minRate, format: .number)
            .keyboardType(.decimalPad)
          TextField("Số tiền tối thiểu cố định", value: $minFixed, format: .number)
            .keyboardType(.decimalPad)
          TextField("Phí thường niên", value: $annualFee, format: .number).keyboardType(.decimalPad)
          TextField("Phí trả chậm", value: $lateFee, format: .number).keyboardType(.decimalPad)
        }
        Section("Khác") {
          TextField("Ghi chú", text: $note, axis: .vertical)
        }
      }
      .navigationTitle(liability == nil ? "Thêm thẻ tín dụng" : "Sửa thẻ tín dụng")
      .toolbar {
        ToolbarItem(placement: .cancellationAction) { Button("Hủy") { dismiss() } }
        ToolbarItem(placement: .confirmationAction) {
          Button("Lưu") { Task { await save() } }.disabled(name.isEmpty || creditLimit <= 0)
        }
      }
      .onAppear { prefill() }
    }
  }

  private func prefill() {
    guard let x = liability else { return }
    name = x.name
    bank = x.lender ?? ""
    creditLimit = x.creditLimit ?? 0
    balance = x.currentBalance
    statementDay = x.statementDay ?? 15
    dueDay = x.paymentDueDay ?? 5
    interestFreeDays = x.interestFreeDays ?? 45
    rate = x.annualInterestRate
    minRate = x.minPaymentRate ?? 5
    minFixed = x.minPaymentFixedAmount ?? 0
    annualFee = x.annualFee ?? 0
    lateFee = x.lateFee ?? 0
    note = x.note ?? ""
  }

  private func nextDueDate() -> Date? {
    let cal = Calendar.current
    let now = Date()
    var comps = cal.dateComponents([.year, .month], from: now)
    comps.day = min(dueDay, 28)
    guard let thisMonth = cal.date(from: comps) else { return nil }
    return thisMonth > now ? thisMonth : cal.date(byAdding: .month, value: 1, to: thisMonth)
  }

  private func save() async {
    let now = Date()
    let isNew = liability == nil
    let x = Liability(
      id: liability?.id ?? UUID(), name: name, lender: bank.nilIfEmpty,
      liabilityType: .creditCard, currency: .vnd, originalPrincipal: creditLimit,
      currentBalance: balance, annualInterestRate: rate, startDate: liability?.startDate ?? now,
      nextPaymentDate: nextDueDate(), creditLimit: creditLimit, statementDay: statementDay,
      paymentDueDay: dueDay, interestFreeDays: interestFreeDays,
      minPaymentRate: minRate > 0 ? minRate : nil, minPaymentFixedAmount: minFixed > 0 ? minFixed : nil,
      annualFee: annualFee > 0 ? annualFee : nil, lateFee: lateFee > 0 ? lateFee : nil,
      lastStatementBalance: liability?.lastStatementBalance, lastStatementDate: liability?.lastStatementDate,
      note: note.nilIfEmpty, createdAt: liability?.createdAt ?? now, updatedAt: now)
    if await onSave(x, isNew) { dismiss() }
  }
}

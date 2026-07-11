import SwiftUI

struct LiabilityFormView: View {
  @Environment(\.dismiss) private var dismiss
  let liability: Liability?
  let onSave: (Liability, Bool) async -> Bool
  @State private var name = ""
  @State private var lender = ""
  @State private var original: Decimal = 0
  @State private var balance: Decimal = 0
  @State private var rate: Decimal = 0
  @State private var start = Date()
  @State private var hasMaturity = false
  @State private var maturity = Date()
  @State private var frequency = PaymentFrequency.monthly
  @State private var hasNextPayment = false
  @State private var nextPayment = Date()
  @State private var monthlyPayment: Decimal = 0
  @State private var collateral = ""
  @State private var note = ""
  var body: some View {
    NavigationStack {
      Form {
        Section("Khoản nợ") {
          TextField("Tên", text: $name)
          TextField("Bên cho vay", text: $lender)
          TextField("Gốc ban đầu", value: $original, format: .number).keyboardType(.decimalPad)
          TextField("Dư nợ hiện tại", value: $balance, format: .number).keyboardType(.decimalPad)
          TextField("Lãi suất %/năm", value: $rate, format: .number).keyboardType(.decimalPad)
          DatePicker("Ngày bắt đầu", selection: $start, displayedComponents: .date)
        }
        Section("Thanh toán") {
          Picker("Tần suất", selection: $frequency) {
            ForEach(PaymentFrequency.allCases, id: \.self) { Text($0.rawValue).tag($0) }
          }
          TextField("Khoản trả hàng tháng", value: $monthlyPayment, format: .number).keyboardType(
            .decimalPad)
          Toggle("Có ngày thanh toán kế tiếp", isOn: $hasNextPayment)
          if hasNextPayment {
            DatePicker("Ngày thanh toán", selection: $nextPayment, displayedComponents: .date)
          }
          Toggle("Có ngày đáo hạn", isOn: $hasMaturity)
          if hasMaturity {
            DatePicker("Ngày đáo hạn", selection: $maturity, displayedComponents: .date)
          }
        }
        Section("Khác") {
          TextField("Tài sản đảm bảo", text: $collateral)
          TextField("Ghi chú", text: $note, axis: .vertical)
        }
      }.navigationTitle(liability == nil ? "Thêm khoản nợ" : "Sửa khoản nợ").toolbar {
        ToolbarItem(placement: .cancellationAction) { Button("Hủy") { dismiss() } }
        ToolbarItem(placement: .confirmationAction) {
          Button("Lưu") { Task { await save() } }.disabled(
            name.isEmpty || original <= 0 || balance < 0)
        }
      }.onAppear { prefill() }
    }
  }
  private func prefill() {
    guard let x = liability else { return }
    name = x.name
    lender = x.lender ?? ""
    original = x.originalPrincipal
    balance = x.currentBalance
    rate = x.annualInterestRate
    start = x.startDate
    if let d = x.maturityDate {
      hasMaturity = true
      maturity = d
    }
    frequency = x.paymentFrequency ?? .monthly
    if let d = x.nextPaymentDate {
      hasNextPayment = true
      nextPayment = d
    }
    monthlyPayment = x.monthlyPayment ?? 0
    collateral = x.collateral ?? ""
    note = x.note ?? ""
  }
  private func save() async {
    let now = Date()
    let x = Liability(
      id: liability?.id ?? UUID(), name: name, lender: lender.nilIfEmpty,
      originalPrincipal: original, currentBalance: balance, annualInterestRate: rate,
      startDate: start, maturityDate: hasMaturity ? maturity : nil, paymentFrequency: frequency,
      nextPaymentDate: hasNextPayment ? nextPayment : nil,
      monthlyPayment: monthlyPayment > 0 ? monthlyPayment : nil, collateral: collateral.nilIfEmpty,
      note: note.nilIfEmpty, createdAt: liability?.createdAt ?? now, updatedAt: now)
    if await onSave(x, liability == nil) { dismiss() }
  }
}

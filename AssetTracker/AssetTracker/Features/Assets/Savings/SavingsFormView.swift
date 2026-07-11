import SwiftUI

struct SavingsFormView: View {
  @Environment(\.dismiss) private var dismiss
  let deposit: SavingsDeposit?
  let onSave: (SavingsDeposit, Bool) async -> Bool
  @State private var name = ""
  @State private var bank = ""
  @State private var principal: Decimal = 0
  @State private var currency = CurrencyCode.vnd
  @State private var rate: Decimal = 0
  @State private var start = Date()
  @State private var months = 1
  @State private var payment = InterestPaymentType.endOfTerm
  @State private var renewal = AutoRenewalType.none
  var maturity: Date { Calendar.current.date(byAdding: .month, value: months, to: start) ?? start }
  var body: some View {
    NavigationStack {
      Form {
        TextField("Tên khoản gửi", text: $name)
        TextField("Ngân hàng", text: $bank)
        TextField("Số tiền", value: $principal, format: .number).keyboardType(.decimalPad)
        Picker("Tiền tệ", selection: $currency) {
          ForEach(CurrencyCode.allCases, id: \.self) { Text($0.rawValue).tag($0) }
        }
        TextField("Lãi suất %/năm", value: $rate, format: .number).keyboardType(.decimalPad)
        DatePicker("Ngày gửi", selection: $start, displayedComponents: .date)
        Stepper("Kỳ hạn: \(months) tháng", value: $months, in: 1...600)
        LabeledContent("Ngày đáo hạn", value: maturity.formatted(date: .numeric, time: .omitted))
        Picker("Nhận lãi", selection: $payment) {
          ForEach(InterestPaymentType.allCases, id: \.self) { Text($0.rawValue).tag($0) }
        }
        Picker("Tái tục", selection: $renewal) {
          ForEach(AutoRenewalType.allCases, id: \.self) { Text($0.rawValue).tag($0) }
        }
      }.navigationTitle(deposit == nil ? "Thêm tiết kiệm" : "Sửa tiết kiệm").toolbar {
        ToolbarItem(placement: .cancellationAction) { Button("Hủy") { dismiss() } }
        ToolbarItem(placement: .confirmationAction) {
          Button("Lưu") { Task { await save() } }.disabled(bank.isEmpty || principal <= 0)
        }
      }.onAppear { prefill() }
    }
  }
  private func prefill() {
    guard let d = deposit else { return }
    name = d.name
    bank = d.bankName
    principal = d.principal
    currency = d.currency
    rate = d.annualInterestRate
    start = d.startDate
    months = d.termInMonths
    payment = d.interestPaymentType
    renewal = d.autoRenewalType ?? .none
  }
  private func save() async {
    let now = Date()
    let d = SavingsDeposit(
      id: deposit?.id ?? UUID(), name: name.nilIfEmpty ?? "Tiết kiệm \(bank)", bankName: bank,
      principal: principal, currency: currency, annualInterestRate: rate, startDate: start,
      maturityDate: maturity, termInMonths: months, interestPaymentType: payment,
      autoRenewalType: renewal, earlyWithdrawalRate: deposit?.earlyWithdrawalRate,
      status: deposit?.status ?? .active, contractNumber: deposit?.contractNumber,
      attachmentURL: deposit?.attachmentURL, accountID: deposit?.accountID,
      createdAt: deposit?.createdAt ?? now, updatedAt: now)
    if await onSave(d, deposit == nil) { dismiss() }
  }
}

import SwiftUI

struct TermLoanFormView: View {
  @Environment(\.dismiss) private var dismiss
  let liability: Liability?
  let onSave: (Liability, Bool) async -> Bool

  @State private var name = ""
  @State private var lender = ""
  @State private var type: LiabilityType = .mortgageLoan
  @State private var original: Decimal = 0
  @State private var balance: Decimal = 0
  @State private var rate: Decimal = 0
  @State private var rateType: InterestRateType = .fixed
  @State private var hasFixedEnd = false
  @State private var fixedEnd = Date()
  @State private var method: RepaymentMethod = .annuity
  @State private var termMonths = 12
  @State private var start = Date()
  @State private var frequency: PaymentFrequency = .monthly
  @State private var earlyFeeRate: Decimal = 0
  @State private var graceMonths = 0
  @State private var collateral = ""
  @State private var note = ""

  private var termTypes: [LiabilityType] { LiabilityType.allCases.filter { $0.group == .termLoan } }

  var body: some View {
    NavigationStack {
      Form {
        Section("Khoản vay") {
          TextField("Tên", text: $name)
          TextField("Chủ nợ", text: $lender)
          Picker("Loại", selection: $type) {
            ForEach(termTypes, id: \.self) { Text($0.label).tag($0) }
          }
          TextField("Số tiền vay ban đầu", value: $original, format: .number)
            .keyboardType(.decimalPad)
          if liability != nil {
            TextField("Dư nợ hiện tại", value: $balance, format: .number).keyboardType(.decimalPad)
          }
        }
        Section("Lãi & kỳ hạn") {
          TextField("Lãi suất %/năm", value: $rate, format: .number).keyboardType(.decimalPad)
          Picker("Loại lãi suất", selection: $rateType) {
            ForEach(InterestRateType.allCases, id: \.self) { Text($0.label).tag($0) }
          }
          if rateType == .floating {
            Toggle("Có ngày hết ưu đãi cố định", isOn: $hasFixedEnd)
            if hasFixedEnd {
              DatePicker("Ngày hết ưu đãi", selection: $fixedEnd, displayedComponents: .date)
            }
          }
          Picker("Phương thức trả", selection: $method) {
            ForEach(RepaymentMethod.allCases, id: \.self) { Text($0.label).tag($0) }
          }
          Stepper("Kỳ hạn: \(termMonths) tháng", value: $termMonths, in: 1...600)
          DatePicker("Ngày vay", selection: $start, displayedComponents: .date)
          Picker("Kỳ thanh toán", selection: $frequency) {
            ForEach(PaymentFrequency.allCases, id: \.self) { Text($0.rawValue).tag($0) }
          }
        }
        Section("Khác") {
          TextField("Phí trả nợ trước hạn %", value: $earlyFeeRate, format: .number)
            .keyboardType(.decimalPad)
          Stepper("Kỳ ân hạn gốc: \(graceMonths) tháng", value: $graceMonths, in: 0...60)
          TextField("Tài sản bảo đảm", text: $collateral)
          TextField("Ghi chú", text: $note, axis: .vertical)
        }
      }
      .navigationTitle(liability == nil ? "Thêm khoản vay" : "Sửa khoản vay")
      .toolbar {
        ToolbarItem(placement: .cancellationAction) { Button("Hủy") { dismiss() } }
        ToolbarItem(placement: .confirmationAction) {
          Button("Lưu") { Task { await save() } }
            .disabled(name.isEmpty || original <= 0 || termMonths < 1)
        }
      }
      .onAppear { prefill() }
    }
  }

  private func prefill() {
    guard let x = liability else { return }
    name = x.name
    lender = x.lender ?? ""
    type = x.liabilityType
    original = x.originalPrincipal
    balance = x.currentBalance
    rate = x.annualInterestRate
    rateType = x.interestRateType ?? .fixed
    if let d = x.fixedRateEndDate {
      hasFixedEnd = true
      fixedEnd = d
    }
    method = x.repaymentMethod ?? .annuity
    termMonths = x.termInMonths ?? 12
    start = x.startDate
    frequency = x.paymentFrequency ?? .monthly
    earlyFeeRate = x.earlyRepaymentFeeRate ?? 0
    graceMonths = x.gracePeriodMonths ?? 0
    collateral = x.collateral ?? ""
    note = x.note ?? ""
  }

  private func save() async {
    let now = Date()
    let isNew = liability == nil
    let maturity = Calendar.current.date(byAdding: .month, value: termMonths, to: start)
    let nextDue =
      liability?.nextPaymentDate ?? Calendar.current.date(byAdding: .month, value: 1, to: start)
    let x = Liability(
      id: liability?.id ?? UUID(), name: name, lender: lender.nilIfEmpty, liabilityType: type,
      currency: .vnd, originalPrincipal: original, currentBalance: isNew ? original : balance,
      annualInterestRate: rate, interestRateType: rateType,
      fixedRateEndDate: (rateType == .floating && hasFixedEnd) ? fixedEnd : nil,
      repaymentMethod: method, termInMonths: termMonths,
      earlyRepaymentFeeRate: earlyFeeRate > 0 ? earlyFeeRate : nil,
      gracePeriodMonths: graceMonths > 0 ? graceMonths : nil, startDate: start,
      maturityDate: maturity, paymentFrequency: frequency, nextPaymentDate: nextDue,
      collateral: collateral.nilIfEmpty, note: note.nilIfEmpty,
      createdAt: liability?.createdAt ?? now, updatedAt: now)
    if await onSave(x, isNew) { dismiss() }
  }
}

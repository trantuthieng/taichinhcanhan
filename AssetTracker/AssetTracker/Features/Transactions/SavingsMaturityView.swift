import SwiftUI

struct SavingsMaturityView: View {
  @Environment(\.dismiss) private var dismiss
  let deposits: [SavingsDeposit]
  let onMature: (SavingsDeposit, Bool, Decimal) async -> Bool
  @State private var id: UUID?
  @State private var early = false
  @State private var earlyRate: Decimal = 0.2
  var selected: SavingsDeposit? { deposits.first { $0.id == id } }
  var interest: Decimal {
    guard let d = selected else { return 0 }
    let end = early ? Date() : d.maturityDate
    let days = max(0, Calendar.current.dateComponents([.day], from: d.startDate, to: end).day ?? 0)
    return early
      ? FinanceCalculator.earlyWithdrawalInterest(
        principal: d.principal, noTermRate: earlyRate, actualDays: days)
      : FinanceCalculator.expectedInterestAtMaturity(
        principal: d.principal, annualRate: d.annualInterestRate, days: days)
  }
  var body: some View {
    NavigationStack {
      Form {
        Picker("Khoản gửi", selection: $id) {
          Text("Chọn").tag(UUID?.none)
          ForEach(deposits.filter { $0.status == .active }) {
            Text("\($0.bankName) · \($0.principal.description)").tag(Optional($0.id))
          }
        }
        Toggle("Tất toán trước hạn", isOn: $early)
        if early {
          TextField("Lãi suất không kỳ hạn", value: $earlyRate, format: .number).keyboardType(
            .decimalPad)
        }
        LabeledContent("Tiền lãi", value: interest.description)
        if let d = selected {
          LabeledContent("Tổng nhận", value: (d.principal + interest).description)
        }
      }.navigationTitle("Tất toán tiết kiệm").toolbar {
        ToolbarItem(placement: .cancellationAction) { Button("Hủy") { dismiss() } }
        ToolbarItem(placement: .confirmationAction) {
          Button("Xác nhận") { Task { await save() } }.disabled(selected == nil)
        }
      }
    }
  }
  private func save() async {
    guard let d = selected else { return }
    if await onMature(d, early, earlyRate) { dismiss() }
  }
}

import SwiftUI

struct LiabilityDetailView: View {
  let liability: Liability
  var onChange: () -> Void
  @State private var editing = false
  @State private var repaying = false
  @State private var updatingStatement = false
  @AppStorage("readOnlyMode") private var readOnly = false

  private var group: LiabilityType.Group { liability.liabilityType.group }

  var body: some View {
    List {
      Section("Tổng quan") {
        row("Loại", liability.liabilityType.label)
        moneyRow("Dư nợ hiện tại", liability.currentBalance)
        moneyRow("Gốc ban đầu", liability.originalPrincipal)
        row("Lãi suất", "\(liability.annualInterestRate.description)%/năm")
        if let lender = liability.lender { row("Chủ nợ", lender) }
        if let due = liability.nextPaymentDate {
          row("Kỳ thanh toán tới", due.formatted(date: .numeric, time: .omitted))
        }
      }

      if group == .creditCard { creditCardSection }

      if !readOnly {
        Section {
          if group == .creditCard {
            Button { updatingStatement = true } label: {
              Label("Cập nhật sao kê", systemImage: "doc.text")
            }
          }
          Button { repaying = true } label: {
            Label("Ghi nhận thanh toán", systemImage: "checkmark.circle")
          }
          Button { editing = true } label: { Label("Sửa", systemImage: "pencil") }
        }
      }

      if group == .termLoan {
        Section("Lịch trả nợ") {
          NavigationLink {
            AmortizationScheduleView(liability: liability)
          } label: {
            Label("Xem lịch trả nợ dự kiến", systemImage: "calendar")
          }
        }
      }
    }
    .navigationTitle(liability.name)
    .sheet(isPresented: $editing) { editForm }
    .sheet(isPresented: $repaying) {
      LiabilityRepaymentView(liability: liability, onDone: onChange)
    }
    .sheet(isPresented: $updatingStatement) {
      CreditCardStatementUpdateView(liability: liability, onDone: onChange)
    }
  }

  @ViewBuilder private var creditCardSection: some View {
    Section("Thẻ tín dụng") {
      if let limit = liability.creditLimit, limit > 0 {
        moneyRow("Hạn mức", limit)
        moneyRow("Còn dùng được", max(0, limit - liability.currentBalance))
        row(
          "Tỷ lệ sử dụng",
          "\(FinanceCalculator.creditUtilization(currentBalance: liability.currentBalance, creditLimit: limit).rounded(1).description)%"
        )
      }
      moneyRow(
        "Thanh toán tối thiểu",
        FinanceCalculator.creditCardMinimumPayment(
          currentBalance: liability.currentBalance, minRate: liability.minPaymentRate ?? 0,
          minFixedAmount: liability.minPaymentFixedAmount ?? 0))
      if let day = liability.statementDay { row("Ngày sao kê", "Ngày \(day) hàng tháng") }
      if let day = liability.paymentDueDay { row("Ngày đến hạn", "Ngày \(day) hàng tháng") }
    }
  }

  @ViewBuilder private var editForm: some View {
    switch group {
    case .termLoan: TermLoanFormView(liability: liability, onSave: saveEdit)
    case .creditCard: CreditCardFormView(liability: liability, onSave: saveEdit)
    case .otherPayable: OtherPayableFormView(liability: liability, onSave: saveEdit)
    }
  }

  private func saveEdit(_ value: Liability, _ isNew: Bool) async -> Bool {
    do {
      let saved = try await LiabilityRepository().update(value)
      await ReminderScheduler.shared.scheduleLiability(saved)
      onChange()
      return true
    } catch { return false }
  }

  private func row(_ title: String, _ value: String) -> some View {
    LabeledContent(title, value: value)
  }
  private func moneyRow(_ title: String, _ value: Decimal) -> some View {
    HStack {
      Text(title)
      Spacer()
      CurrencyText(value: value)
    }
  }
}

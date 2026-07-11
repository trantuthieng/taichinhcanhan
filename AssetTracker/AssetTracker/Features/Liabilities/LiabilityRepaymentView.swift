import SwiftUI

struct LiabilityRepaymentView: View {
  @Environment(\.dismiss) private var dismiss
  let liability: Liability
  var onDone: () -> Void

  @State private var amount: Decimal = 0
  @State private var date = Date()
  @State private var paymentType: LiabilityPaymentType = .full
  @State private var priorRepayments = 0
  @State private var errorMessage: String?
  @State private var saving = false

  private var isCreditCard: Bool { liability.liabilityType.group == .creditCard }
  private var showRetroWarning: Bool { isCreditCard && paymentType != .full }

  var body: some View {
    NavigationStack {
      Form {
        Section("Khoản nợ") {
          LabeledContent("Tên", value: liability.name)
          HStack {
            Text("Dư nợ hiện tại")
            Spacer()
            CurrencyText(value: liability.currentBalance)
          }
        }
        if isCreditCard {
          Section("Hình thức thanh toán") {
            Picker("Kiểu", selection: $paymentType) {
              ForEach(LiabilityPaymentType.allCases, id: \.self) { Text($0.label).tag($0) }
            }
            .onChange(of: paymentType) { _, _ in applyDefaultAmount() }
          }
        }
        Section("Thanh toán") {
          TextField("Số tiền", value: $amount, format: .number).keyboardType(.decimalPad)
          DatePicker("Ngày", selection: $date, displayedComponents: .date)
        }
        if showRetroWarning {
          Section {
            Label(
              "Trả dưới 100% dư nợ sao kê: toàn bộ dư nợ (kể cả phần đã trả) sẽ bị tính lãi hồi tố kể từ ngày phát sinh giao dịch, không chỉ phần chưa trả.",
              systemImage: "exclamationmark.triangle.fill"
            )
            .foregroundStyle(.orange)
          }
        }
        if let errorMessage {
          Section { Text(errorMessage).foregroundStyle(.red) }
        }
      }
      .navigationTitle("Ghi nhận thanh toán")
      .toolbar {
        ToolbarItem(placement: .cancellationAction) { Button("Hủy") { dismiss() } }
        ToolbarItem(placement: .confirmationAction) {
          Button("Lưu") { Task { await save() } }.disabled(amount <= 0 || saving)
        }
      }
      .task { await prepare() }
    }
  }

  private func prepare() async {
    let txs = (try? await AssetTransactionRepository().fetchAll()) ?? []
    priorRepayments = txs.filter { $0.type == .repayment && $0.liabilityID == liability.id }.count
    applyDefaultAmount()
  }

  private func applyDefaultAmount() {
    switch liability.liabilityType.group {
    case .creditCard:
      switch paymentType {
      case .full: amount = liability.currentBalance
      case .minimum:
        amount = FinanceCalculator.creditCardMinimumPayment(
          currentBalance: liability.currentBalance, minRate: liability.minPaymentRate ?? 0,
          minFixedAmount: liability.minPaymentFixedAmount ?? 0)
      case .partial: break
      }
    case .termLoan:
      let schedule = liability.amortizationSchedule
      if priorRepayments < schedule.count { amount = schedule[priorRepayments].totalDue }
    case .otherPayable:
      amount = liability.currentBalance
    }
  }

  private func save() async {
    saving = true
    defer { saving = false }
    var updated = liability
    let type: LiabilityPaymentType? = isCreditCard ? paymentType : nil

    switch liability.liabilityType.group {
    case .termLoan:
      let schedule = liability.amortizationSchedule
      if priorRepayments < schedule.count {
        updated.currentBalance = schedule[priorRepayments].remainingBalance
        updated.nextPaymentDate =
          priorRepayments + 1 < schedule.count ? schedule[priorRepayments + 1].dueDate : nil
      } else {
        updated.currentBalance = max(0, liability.currentBalance - amount)
      }
    case .creditCard:
      updated.currentBalance = paymentType == .full ? 0 : max(0, liability.currentBalance - amount)
    case .otherPayable:
      updated.currentBalance = max(0, liability.currentBalance - amount)
    }
    updated.updatedAt = Date()

    let tx = AssetTransaction(
      id: UUID(), assetID: nil, type: .repayment, date: date, quantity: nil, unitPrice: nil,
      amount: amount, fee: 0, tax: 0, sourceAccountID: nil, destinationAccountID: nil,
      note: nil, attachmentURL: nil, liabilityID: liability.id, paymentType: type, createdAt: Date())
    do {
      _ = try await AssetTransactionRepository().insert(tx)
      let saved = try await LiabilityRepository().update(updated)
      await ReminderScheduler.shared.scheduleLiability(saved)
      onDone()
      dismiss()
    } catch { errorMessage = error.localizedDescription }
  }
}

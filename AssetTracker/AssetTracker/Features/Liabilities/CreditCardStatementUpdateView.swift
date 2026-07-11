import SwiftUI

/// Nhóm B (mục 5.3.1): dư nợ thẻ tín dụng cập nhật trực tiếp mỗi kỳ sao kê,
/// KHÔNG suy ra từ transaction log (ngoại lệ có chủ đích so với mục 26.4).
struct CreditCardStatementUpdateView: View {
  @Environment(\.dismiss) private var dismiss
  let liability: Liability
  var onDone: () -> Void

  @State private var statementBalance: Decimal = 0
  @State private var statementDate = Date()
  @State private var errorMessage: String?
  @State private var saving = false

  var body: some View {
    NavigationStack {
      Form {
        Section("Sao kê mới") {
          LabeledContent("Thẻ", value: liability.name)
          TextField("Dư nợ kỳ sao kê", value: $statementBalance, format: .number)
            .keyboardType(.decimalPad)
          DatePicker("Ngày sao kê", selection: $statementDate, displayedComponents: .date)
        }
        Section {
          Text(
            "Dư nợ thẻ tín dụng nhập tay theo sao kê ngân hàng gửi, không tính lại từ giao dịch trong app."
          ).font(.caption).foregroundStyle(.secondary)
        }
        if let errorMessage {
          Section { Text(errorMessage).foregroundStyle(.red) }
        }
      }
      .navigationTitle("Cập nhật sao kê")
      .toolbar {
        ToolbarItem(placement: .cancellationAction) { Button("Hủy") { dismiss() } }
        ToolbarItem(placement: .confirmationAction) {
          Button("Lưu") { Task { await save() } }.disabled(saving)
        }
      }
      .onAppear { statementBalance = liability.currentBalance }
    }
  }

  private func save() async {
    saving = true
    defer { saving = false }
    var updated = liability
    updated.currentBalance = statementBalance
    updated.lastStatementBalance = statementBalance
    updated.lastStatementDate = statementDate
    updated.updatedAt = Date()
    do {
      let saved = try await LiabilityRepository().update(updated)
      await ReminderScheduler.shared.scheduleLiability(saved)
      onDone()
      dismiss()
    } catch { errorMessage = error.localizedDescription }
  }
}

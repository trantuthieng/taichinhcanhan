import SwiftUI

struct CashAccountFormView: View {
  @Environment(\.dismiss) private var dismiss
  let account: AssetAccount?
  let onSave: (AssetAccount, Bool) async -> Bool

  @State private var name = ""
  @State private var accountType = AccountType.cashPersonal
  @State private var currency = CurrencyCode.vnd
  @State private var balance: Decimal = 0
  @State private var openingRate: Decimal = 1
  @State private var currentRate: Decimal = 1
  @State private var institution = ""
  @State private var targetGroup = ""
  @State private var note = ""
  @State private var isSaving = false

  var body: some View {
    NavigationStack {
      Form {
        Section("Tài khoản") {
          TextField("Tên tài khoản", text: $name)
          Picker("Loại", selection: $accountType) {
            ForEach(AccountType.allCases, id: \.self) { Text($0.rawValue).tag($0) }
          }
          TextField("Tổ chức quản lý", text: $institution)
          TextField("Nhóm mục tiêu", text: $targetGroup)
        }
        Section("Số dư") {
          TextField("Số dư", value: $balance, format: .number).keyboardType(.decimalPad)
          Picker("Tiền tệ", selection: $currency) {
            ForEach(CurrencyCode.allCases, id: \.self) { Text($0.rawValue).tag($0) }
          }
          if currency != .vnd {
            TextField("Tỷ giá lúc nhận/mua", value: $openingRate, format: .number).keyboardType(
              .decimalPad)
            TextField("Tỷ giá hiện tại", value: $currentRate, format: .number).keyboardType(
              .decimalPad)
            LabeledContent("Quy đổi VND") { CurrencyText(value: balance * currentRate) }
          }
        }
        Section("Ghi chú") { TextField("Ghi chú", text: $note, axis: .vertical) }
      }
      .navigationTitle(account == nil ? "Thêm tài khoản" : "Sửa tài khoản")
      .toolbar {
        ToolbarItem(placement: .cancellationAction) { Button("Hủy") { dismiss() } }
        ToolbarItem(placement: .confirmationAction) {
          Button("Lưu") { Task { await save() } }.disabled(
            name.trimmingCharacters(in: .whitespaces).isEmpty || isSaving)
        }
      }
      .onAppear { prefill() }
    }
  }

  private func prefill() {
    guard let account else { return }
    name = account.name
    accountType = account.accountType
    currency = account.currency
    balance = account.balance
    openingRate = account.exchangeRateAtOpening ?? 1
    currentRate = account.currentExchangeRate ?? 1
    institution = account.institution ?? ""
    targetGroup = account.targetGroup ?? ""
    note = account.note ?? ""
  }

  private func save() async {
    isSaving = true
    defer { isSaving = false }
    let now = Date()
    let value = AssetAccount(
      id: account?.id ?? UUID(), name: name, institution: institution.nilIfEmpty,
      accountType: accountType, currency: currency, balance: balance,
      exchangeRateAtOpening: currency == .vnd ? nil : openingRate,
      currentExchangeRate: currency == .vnd ? nil : currentRate,
      isIncludedInNetWorth: account?.isIncludedInNetWorth ?? true,
      targetGroup: targetGroup.nilIfEmpty, note: note.nilIfEmpty,
      createdAt: account?.createdAt ?? now, updatedAt: now)
    if await onSave(value, account == nil) { dismiss() }
  }
}

extension String {
  var nilIfEmpty: String? { trimmingCharacters(in: .whitespacesAndNewlines).isEmpty ? nil : self }
}

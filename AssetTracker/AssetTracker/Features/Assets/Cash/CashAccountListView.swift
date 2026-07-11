import SwiftUI

struct CashAccountListView: View {
  @State private var viewModel = CashAccountViewModel()
  @State private var editingAccount: AssetAccount?
  @State private var showsNewAccount = false
  @AppStorage("readOnlyMode") private var readOnly = false

  var body: some View {
    List {
      ForEach(viewModel.accounts) { account in
        Button {
          if !readOnly { editingAccount = account }
        } label: {
          HStack {
            VStack(alignment: .leading) {
              Text(account.name).font(.headline).foregroundStyle(.primary)
              Text(
                [account.institution, account.currency.rawValue].compactMap { $0 }.joined(
                  separator: " · ")
              )
              .font(.caption).foregroundStyle(.secondary)
            }
            Spacer()
            VStack(alignment: .trailing) {
              CurrencyText(value: account.balance, code: account.currency.rawValue)
              if account.currency != .vnd {
                CurrencyText(value: account.balance * (account.currentExchangeRate ?? 0))
                  .font(.caption).foregroundStyle(.secondary)
              }
            }
          }
        }
      }
      .onDelete { offsets in Task { await viewModel.delete(at: offsets) } }
      .deleteDisabled(readOnly)
    }
    .overlay {
      if viewModel.accounts.isEmpty && !viewModel.isLoading {
        ContentUnavailableView("Chưa có tài khoản", systemImage: "banknote")
      }
    }
    .navigationTitle("Tiền mặt")
    .toolbar { if !readOnly { Button("Thêm", systemImage: "plus") { showsNewAccount = true } } }
    .refreshable { await viewModel.load() }
    .task { await viewModel.load() }
    .sheet(isPresented: $showsNewAccount) { form(nil) }
    .sheet(item: $editingAccount) { form($0) }
    .alert("Không thể tải dữ liệu", isPresented: .constant(viewModel.errorMessage != nil)) {
      Button("OK") { viewModel.errorMessage = nil }
    } message: {
      Text(viewModel.errorMessage ?? "")
    }
  }

  private func form(_ account: AssetAccount?) -> some View {
    CashAccountFormView(account: account) { value, isNew in
      await viewModel.save(value, isNew: isNew)
    }
  }
}

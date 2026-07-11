import SwiftUI

struct TransactionsView: View {
  @State private var vm = TransactionViewModel()
  @State private var sheet: Sheet?
  @AppStorage("readOnlyMode") private var readOnly = false
  enum Sheet: String, Identifiable {
    case general, buy, sell, transfer, maturity
    var id: String { rawValue }
  }
  var stocks: [Asset] {
    vm.assets.filter {
      [
        .stock, .fundCertificate, .etf, .listedBond, .warrant, .foreignStock, .openEndFund,
        .otherSecurity,
      ].contains($0.category)
    }
  }
  var body: some View {
    NavigationStack {
      List {
        if !readOnly {
          Section {
            Button("Nạp, rút hoặc điều chỉnh", systemImage: "plusminus") { sheet = .general }
            Button("Mua chứng khoán", systemImage: "cart.badge.plus") { sheet = .buy }
            Button("Bán chứng khoán", systemImage: "cart.badge.minus") { sheet = .sell }
            Button("Chuyển tiền", systemImage: "arrow.left.arrow.right") { sheet = .transfer }
            Button("Tất toán tiết kiệm", systemImage: "building.columns") { sheet = .maturity }
          }
        }
        Section("Lịch sử (chỉ đọc)") {
          ForEach(vm.transactions) { tx in
            HStack {
              VStack(alignment: .leading) {
                Text(tx.type.rawValue).font(.headline)
                Text([tx.date.formatted(), tx.editedBy].compactMap { $0 }.joined(separator: " · "))
                  .font(.caption).foregroundStyle(.secondary)
              }
              Spacer()
              CurrencyText(value: tx.amount)
            }
          }
        }
      }.navigationTitle("Giao dịch").task { await vm.load() }.refreshable { await vm.load() }.sheet(
        item: $sheet
      ) { item in
        switch item {
        case .general: TransactionFormView(accounts: vm.accounts, onSave: vm.add)
        case .buy: BuyStockView(stocks: stocks, onSave: vm.add)
        case .sell: SellStockView(stocks: stocks, holding: vm.holding, onSave: vm.add)
        case .transfer: TransferFundsView(accounts: vm.accounts, onSave: vm.add)
        case .maturity: SavingsMaturityView(deposits: vm.deposits, onMature: vm.mature)
        }
      }
    }
  }
}

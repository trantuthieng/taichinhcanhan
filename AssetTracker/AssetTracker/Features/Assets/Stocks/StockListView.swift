import SwiftUI

struct StockListView: View {
  @State private var vm = StockViewModel()
  @State private var adding = false
  @State private var editing: Asset?
  @AppStorage("readOnlyMode") private var readOnly = false
  var body: some View {
    List {
      Section {
        Label(
          StockMarketHours.isOpen() ? "Thị trường đang mở" : "Thị trường đã đóng cửa",
          systemImage: StockMarketHours.isOpen() ? "circle.fill" : "moon.fill"
        ).foregroundStyle(StockMarketHours.isOpen() ? .green : .secondary)
      }
      ForEach(vm.stocks) { stock in
        Button {
          if !readOnly { editing = stock }
        } label: {
          HStack {
            VStack(alignment: .leading) {
              Text(stock.symbol ?? stock.name).font(.headline)
              Text(stock.category.rawValue).font(.caption).foregroundStyle(.secondary)
              Text(vm.display(for: stock).caption).font(.caption2).foregroundStyle(.secondary)
            }
            Spacer()
            VStack(alignment: .trailing) {
              CurrencyText(value: vm.display(for: stock).price * stock.quantity)
              Text("SL: \(stock.quantity.description)").font(.caption)
            }
          }.foregroundStyle(.primary)
        }
      }.onDelete { x in Task { await vm.delete(at: x) } }.deleteDisabled(readOnly)
    }.navigationTitle("Chứng khoán").toolbar {
      if !readOnly { Button("Thêm", systemImage: "plus") { adding = true } }
    }.task { await vm.load() }.refreshable { await vm.load() }
      .sheet(isPresented: $adding) {
        StockFormView(stock: nil, accounts: vm.accounts, onCreate: vm.create, onUpdate: vm.update)
      }
      .sheet(item: $editing) {
        StockFormView(stock: $0, accounts: vm.accounts, onCreate: vm.create, onUpdate: vm.update)
      }
  }
}

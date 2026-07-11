import SwiftUI

struct GoldListView: View {
  @State private var vm = GoldViewModel()
  @State private var adding = false
  @State private var editing: Asset?
  @AppStorage("readOnlyMode") private var readOnly = false
  var body: some View {
    List {
      ForEach(vm.items) { a in
        Button {
          if !readOnly { editing = a }
        } label: {
          HStack {
            VStack(alignment: .leading) {
              Text(a.name).font(.headline)
              Text([a.brand, a.unit.rawValue].compactMap { $0 }.joined(separator: " · ")).font(
                .caption)
              Text(vm.display(for: a).caption).font(.caption2).foregroundStyle(.secondary)
            }
            Spacer()
            CurrencyText(value: a.quantity * vm.display(for: a).price)
          }.foregroundStyle(.primary)
        }
      }.onDelete { x in Task { await vm.delete(at: x) } }.deleteDisabled(readOnly)
    }.navigationTitle("Vàng").toolbar {
      if !readOnly { Button("Thêm", systemImage: "plus") { adding = true } }
    }.task { await vm.load() }.refreshable { await vm.load() }.sheet(isPresented: $adding) {
      GoldFormView(asset: nil, onSave: { await vm.save($0, isNew: $1) })
    }.sheet(item: $editing) {
      GoldFormView(asset: $0, onSave: { await vm.save($0, isNew: $1) })
    }
  }
}

import SwiftUI

struct OtherAssetListView: View {
  @State private var vm = OtherAssetViewModel()
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
              Text(a.category.rawValue).font(.caption).foregroundStyle(.secondary)
            }
            Spacer()
            CurrencyText(value: a.currentPrice)
          }
        }.foregroundStyle(.primary)
      }.onDelete { x in Task { await vm.delete(at: x) } }.deleteDisabled(readOnly)
    }.navigationTitle("Tài sản khác").toolbar {
      if !readOnly { Button("Thêm", systemImage: "plus") { adding = true } }
    }.task { await vm.load() }.refreshable { await vm.load() }.sheet(isPresented: $adding) {
      OtherAssetFormView(asset: nil, onSave: vm.save)
    }.sheet(item: $editing) { OtherAssetFormView(asset: $0, onSave: vm.save) }
  }
}

import SwiftUI

struct LiabilityListView: View {
  @State private var vm = LiabilityViewModel()
  @State private var adding = false
  @State private var editing: Liability?
  @AppStorage("readOnlyMode") private var readOnly = false
  var body: some View {
    List {
      ForEach(vm.liabilities) { x in
        Button {
          if !readOnly { editing = x }
        } label: {
          VStack(alignment: .leading, spacing: 5) {
            HStack {
              Text(x.name).font(.headline)
              Spacer()
              CurrencyText(value: x.currentBalance)
            }
            HStack {
              Text(x.lender ?? "")
              Spacer()
              if let due = x.nextPaymentDate {
                Text("Kỳ tới: \(due.formatted(date:.numeric,time:.omitted))")
              }
            }.font(.caption).foregroundStyle(.secondary)
          }
        }.foregroundStyle(.primary)
      }.onDelete { x in Task { await vm.delete(at: x) } }.deleteDisabled(readOnly)
    }.navigationTitle("Nợ phải trả").toolbar {
      if !readOnly { Button("Thêm", systemImage: "plus") { adding = true } }
    }.task { await vm.load() }.refreshable { await vm.load() }.sheet(isPresented: $adding) {
      LiabilityFormView(liability: nil, onSave: vm.save)
    }.sheet(item: $editing) { LiabilityFormView(liability: $0, onSave: vm.save) }
  }
}

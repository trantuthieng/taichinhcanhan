import SwiftUI

struct SavingsListView: View {
  @State private var vm = SavingsViewModel()
  @State private var adding = false
  @State private var editing: SavingsDeposit?
  @AppStorage("readOnlyMode") private var readOnly = false
  var body: some View {
    List {
      ForEach(vm.deposits) { d in
        Button {
          if !readOnly { editing = d }
        } label: {
          VStack(alignment: .leading, spacing: 6) {
            HStack {
              Text(d.bankName).font(.headline)
              Spacer()
              CurrencyText(value: d.principal, code: d.currency.rawValue)
            }
            HStack {
              Text("Đáo hạn \(d.maturityDate.formatted(date:.numeric,time:.omitted))")
              Spacer()
              Text("\(d.annualInterestRate.description)%/năm")
            }.font(.caption).foregroundStyle(.secondary)
            let days = max(
              0,
              Calendar.current.dateComponents([.day], from: d.startDate, to: d.maturityDate).day
                ?? 0)
            CurrencyText(
              value: FinanceCalculator.expectedInterestAtMaturity(
                principal: d.principal, annualRate: d.annualInterestRate, days: days),
              code: d.currency.rawValue
            ).font(.caption)
          }
        }.foregroundStyle(.primary)
      }.onDelete { x in Task { await vm.delete(at: x) } }.deleteDisabled(readOnly)
    }.navigationTitle("Tiết kiệm").toolbar {
      if !readOnly { Button("Thêm", systemImage: "plus") { adding = true } }
    }.task { await vm.load() }.refreshable { await vm.load() }.sheet(isPresented: $adding) {
      SavingsFormView(deposit: nil, onSave: vm.save)
    }.sheet(item: $editing) { SavingsFormView(deposit: $0, onSave: vm.save) }
  }
}

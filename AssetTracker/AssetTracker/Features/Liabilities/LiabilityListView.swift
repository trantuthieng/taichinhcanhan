import SwiftUI

struct LiabilityListView: View {
  @State private var vm = LiabilityViewModel()
  @State private var addingTermLoan = false
  @State private var addingCreditCard = false
  @State private var addingOther = false
  @AppStorage("readOnlyMode") private var readOnly = false

  var body: some View {
    List {
      section("Vay có kỳ hạn", vm.group(.termLoan))
      section("Thẻ tín dụng", vm.group(.creditCard))
      section("Khoản phải trả khác", vm.group(.otherPayable))
    }
    .navigationTitle("Nợ phải trả")
    .toolbar {
      if !readOnly {
        Menu {
          Button("Vay có kỳ hạn") { addingTermLoan = true }
          Button("Thẻ tín dụng") { addingCreditCard = true }
          Button("Khoản phải trả khác") { addingOther = true }
        } label: {
          Label("Thêm", systemImage: "plus")
        }
      }
    }
    .task { await vm.load() }
    .refreshable { await vm.load() }
    .sheet(isPresented: $addingTermLoan) { TermLoanFormView(liability: nil, onSave: vm.save) }
    .sheet(isPresented: $addingCreditCard) { CreditCardFormView(liability: nil, onSave: vm.save) }
    .sheet(isPresented: $addingOther) { OtherPayableFormView(liability: nil, onSave: vm.save) }
  }

  @ViewBuilder private func section(_ title: String, _ items: [Liability]) -> some View {
    if !items.isEmpty {
      Section(title) {
        ForEach(items) { x in
          NavigationLink {
            LiabilityDetailView(liability: x) { Task { await vm.load() } }
          } label: {
            VStack(alignment: .leading, spacing: 5) {
              HStack {
                Text(x.name).font(.headline)
                Spacer()
                CurrencyText(value: x.currentBalance)
              }
              HStack {
                Text(x.liabilityType.label)
                Spacer()
                if x.liabilityType.group == .creditCard, let limit = x.creditLimit, limit > 0 {
                  Text(
                    "Dùng \(FinanceCalculator.creditUtilization(currentBalance: x.currentBalance, creditLimit: limit).rounded(0).description)%"
                  )
                } else if let due = x.nextPaymentDate {
                  Text("Kỳ tới: \(due.formatted(date: .numeric, time: .omitted))")
                }
              }.font(.caption).foregroundStyle(.secondary)
            }
          }
        }
        .onDelete { idx in Task { for i in idx { await vm.delete(items[i]) } } }
        .deleteDisabled(readOnly)
      }
    }
  }
}

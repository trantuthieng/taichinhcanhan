import SwiftUI

struct AmortizationScheduleView: View {
  let liability: Liability
  @State private var paidCount = 0

  var body: some View {
    List {
      ForEach(liability.amortizationSchedule, id: \.periodIndex) { row in
        VStack(alignment: .leading, spacing: 4) {
          HStack {
            Text("Kỳ \(row.periodIndex)").font(.headline)
            Spacer()
            status(row)
          }
          HStack {
            Text(row.dueDate.formatted(date: .numeric, time: .omitted))
            Spacer()
            CurrencyText(value: row.totalDue)
          }.font(.subheadline)
          HStack {
            Text("Gốc: \(row.principalDue.rounded(0).description)")
            Spacer()
            Text("Lãi: \(row.interestDue.rounded(0).description)")
          }.font(.caption).foregroundStyle(.secondary)
          Text("Dư nợ còn lại: \(row.remainingBalance.rounded(0).description)")
            .font(.caption).foregroundStyle(.secondary)
        }
      }
    }
    .navigationTitle("Lịch trả nợ")
    .task { await loadPaid() }
  }

  private func status(_ row: FinanceCalculator.AmortizationRow) -> some View {
    let text: String
    let color: Color
    if row.periodIndex <= paidCount {
      (text, color) = ("Đã trả", .green)
    } else if row.dueDate < Date() {
      (text, color) = ("Trễ hạn", .red)
    } else {
      (text, color) = ("Chưa trả", .secondary)
    }
    return Text(text).font(.caption.bold()).foregroundStyle(color)
  }

  private func loadPaid() async {
    let txs = (try? await AssetTransactionRepository().fetchAll()) ?? []
    paidCount = txs.filter { $0.type == .repayment && $0.liabilityID == liability.id }.count
  }
}

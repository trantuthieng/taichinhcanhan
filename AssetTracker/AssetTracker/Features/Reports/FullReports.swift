import Observation
import SwiftUI

struct NetWorthReportView: View {
  @State private var snapshots: [ValuationSnapshot] = []
  var body: some View {
    List {
      if let latest = snapshots.last {
        Section("Hiện tại") {
          row("Tổng tài sản", latest.totalAssets)
          row("Tổng nợ", latest.totalLiabilities)
          row("Tài sản ròng", latest.netWorth)
        }
      }
      Section("Tăng trưởng") { GrowthLineChartView(snapshots: snapshots) }
    }.navigationTitle("Tài sản ròng").task {
      snapshots =
        (try? await ValuationSnapshotRepository().fetchAll().sorted { $0.date < $1.date }) ?? []
    }
  }
  private func row(_ name: String, _ value: Decimal) -> some View {
    HStack {
      Text(name)
      Spacer()
      CurrencyText(value: value)
    }
  }
}

struct ProfitLossRow: Identifiable {
  let id: UUID
  let name: String
  let value: Decimal
  let cost: Decimal
  var profit: Decimal { value - cost }
  var rate: Decimal { FinanceCalculator.profitRate(profitLoss: profit, cost: cost) }
}
@MainActor @Observable final class ProfitLossReportModel {
  var rows: [ProfitLossRow] = []
  func load() async {
    do {
      let assets = try await AssetRepository().fetchAll()
      let repo = AssetTransactionRepository()
      var result: [ProfitLossRow] = []
      for asset in assets {
        let p = try await repo.computeCurrentQuantityAndCost(forAssetID: asset.id)
        guard p.quantity > 0 else { continue }
        result.append(
          .init(
            id: asset.id, name: asset.symbol ?? asset.name, value: p.quantity * asset.currentPrice,
            cost: p.quantity * p.averageCost))
      }
      rows = result.sorted { $0.profit > $1.profit }
    } catch {}
  }
}
struct ProfitLossReportView: View {
  @State private var model = ProfitLossReportModel()
  var body: some View {
    List(model.rows) { x in
      VStack(alignment: .leading) {
        HStack {
          Text(x.name).font(.headline)
          Spacer()
          CurrencyText(value: x.profit)
        }
        HStack {
          Text("Giá trị: \(x.value.description)")
          Spacer()
          Text("\(x.rate.description)%")
        }.font(.caption).foregroundStyle(x.profit < 0 ? .red : .green)
      }
    }.navigationTitle("Lãi/lỗ").task { await model.load() }.refreshable { await model.load() }
  }
}

struct AllocationReportView: View {
  @State private var valuation = PortfolioValuation(
    totalAssets: 0, totalLiabilities: 0, cash: 0, stocks: 0, gold: 0, savings: 0, other: 0)
  var items: [AllocationItem] {
    [
      .init(name: "Tiền", value: valuation.cash),
      .init(name: "Chứng khoán", value: valuation.stocks),
      .init(name: "Vàng", value: valuation.gold),
      .init(name: "Tiết kiệm", value: valuation.savings),
      .init(name: "Khác", value: valuation.other),
    ].filter { $0.value > 0 }
  }
  var body: some View {
    ScrollView {
      VStack {
        AllocationPieChartView(items: items)
        ForEach(items) { item in
          HStack {
            Text(item.name)
            Spacer()
            Text(
              valuation.totalAssets == 0
                ? "0%" : "\((item.value/valuation.totalAssets*100).description)%")
            CurrencyText(value: item.value)
          }.padding(.horizontal)
        }
      }.padding(.vertical)
    }.navigationTitle("Phân bổ").task {
      valuation = (try? await SnapshotScheduler().currentValuation()) ?? valuation
    }
  }
}

struct MaturityReportView: View {
  @State private var deposits: [SavingsDeposit] = []
  var body: some View {
    List(deposits) { d in
      VStack(alignment: .leading) {
        HStack {
          Text(d.name).font(.headline)
          Spacer()
          CurrencyText(value: d.principal, code: d.currency.rawValue)
        }
        Text("\(d.bankName) · \(d.maturityDate.formatted(date:.numeric,time:.omitted))").font(
          .caption
        ).foregroundStyle(.secondary)
      }
    }.navigationTitle("Lịch đáo hạn").task {
      deposits =
        (try? await SavingsDepositRepository().fetchAll().filter { $0.status == .active }.sorted {
          $0.maturityDate < $1.maturityDate
        }) ?? []
    }
  }
}

@MainActor @Observable final class PassiveIncomeReportModel {
  var interest: Decimal = 0
  var dividend: Decimal = 0
  var generated: Decimal = 0
  var total: Decimal { interest + dividend + generated }
  func load() async {
    do {
      async let tx = AssetTransactionRepository().fetchAll()
      async let assets = AssetRepository().fetchAll()
      let (t, a) = try await (tx, assets)
      interest = t.filter { $0.type == .interest }.reduce(0) { $0 + $1.amount }
      dividend = t.filter { $0.type == .dividend }.reduce(0) { $0 + $1.amount }
      generated = a.reduce(0) { $0 + ($1.generatedIncome ?? 0) }
    } catch {}
  }
}
struct PassiveIncomeReportView: View {
  @State private var model = PassiveIncomeReportModel()
  var body: some View {
    List {
      Section("Tổng") {
        HStack {
          Text("Thu nhập thụ động")
          Spacer()
          CurrencyText(value: model.total)
        }
      }
      Section("Nguồn") {
        money("Lãi", model.interest)
        money("Cổ tức", model.dividend)
        money("Tài sản tạo thu nhập", model.generated)
      }
    }.navigationTitle("Thu nhập thụ động").task { await model.load() }
  }
  private func money(_ name: String, _ value: Decimal) -> some View {
    HStack {
      Text(name)
      Spacer()
      CurrencyText(value: value)
    }
  }
}

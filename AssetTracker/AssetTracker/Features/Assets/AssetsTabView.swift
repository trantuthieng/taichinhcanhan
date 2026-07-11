import Observation
import SwiftUI

struct AssetsTabView: View {
  @State private var summary = AssetGroupSummary()
  var body: some View {
    NavigationStack {
      List {
        groupLink(
          "Tiền mặt", icon: "banknote.fill", value: summary.cashValue, cost: summary.cashValue,
          count: summary.cashCount
        ) { CashAccountListView() }
        groupLink(
          "Chứng khoán", icon: "chart.line.uptrend.xyaxis", value: summary.stockValue,
          cost: summary.stockCost, count: summary.stockCount
        ) { StockListView() }
        groupLink(
          "Vàng", icon: "seal.fill", value: summary.goldValue, cost: summary.goldCost,
          count: summary.goldCount
        ) { GoldListView() }
        groupLink(
          "Tiết kiệm", icon: "building.columns.fill", value: summary.savingsValue,
          cost: summary.savingsValue, count: summary.savingsCount
        ) { SavingsListView() }
        NavigationLink {
          OtherAssetListView()
        } label: {
          Label("Bất động sản & tài sản khác", systemImage: "house.fill")
        }
        Section("Nghĩa vụ") {
          NavigationLink {
            LiabilityListView()
          } label: {
            Label("Nợ phải trả", systemImage: "creditcard.fill")
          }
        }
        Section("Công cụ") {
          NavigationLink {
            WhatIfSimulatorView()
          } label: {
            Label("Mô phỏng tài chính", systemImage: "slider.horizontal.3")
          }
        }
      }
      .navigationTitle("Tài sản")
      .task { await summary.load() }
      .refreshable { await summary.load() }
    }
  }

  private func groupLink<Destination: View>(
    _ title: String, icon: String, value: Decimal, cost: Decimal, count: Int,
    @ViewBuilder destination: () -> Destination
  ) -> some View {
    NavigationLink(destination: destination()) {
      VStack(alignment: .leading, spacing: 6) {
        Label(title, systemImage: icon).font(.headline)
        HStack {
          CurrencyText(value: value)
          Spacer()
          Text("\(count) khoản mục")
        }.font(.subheadline)
        let pnl = FinanceCalculator.profitLoss(currentValue: value, remainingCost: cost)
        HStack {
          Text("Lãi/lỗ: \(pnl.description)")
          Spacer()
          Text("Tỷ trọng: \(summary.total == 0 ? "0" : (value/summary.total*100).description)%")
        }.font(.caption).foregroundStyle(.secondary)
      }
    }
  }
}

@MainActor @Observable final class AssetGroupSummary {
  var cashValue: Decimal = 0
  var stockValue: Decimal = 0
  var stockCost: Decimal = 0
  var goldValue: Decimal = 0
  var goldCost: Decimal = 0
  var savingsValue: Decimal = 0
  var cashCount = 0
  var stockCount = 0
  var goldCount = 0
  var savingsCount = 0
  var total: Decimal { cashValue + stockValue + goldValue + savingsValue }
  func load() async {
    do {
      async let accounts = AssetAccountRepository().fetchAll()
      async let assets = AssetRepository().fetchAll()
      async let deposits = SavingsDepositRepository().fetchAll()
      let (a, items, s) = try await (accounts, assets, deposits)
      cashCount = a.count
      cashValue = a.filter(\.isIncludedInNetWorth).reduce(0) {
        $0
          + FinanceCalculator.fxConvertedValue(
            amount: $1.balance,
            exchangeRate: $1.currency == .vnd ? 1 : ($1.currentExchangeRate ?? 0))
      }
      let stocks = items.filter {
        [
          .stock, .fundCertificate, .etf, .listedBond, .warrant, .foreignStock, .openEndFund,
          .otherSecurity,
        ].contains($0.category)
      }
      let gold = items.filter { GoldViewModel.categories.contains($0.category) }
      stockCount = stocks.count
      stockValue = stocks.reduce(0) { $0 + $1.quantity * $1.currentPrice }
      stockCost = stocks.reduce(0) { $0 + $1.quantity * $1.averageCost }
      goldCount = gold.count
      goldValue = gold.reduce(0) { $0 + $1.quantity * $1.currentPrice }
      goldCost = gold.reduce(0) { $0 + $1.quantity * $1.averageCost }
      savingsCount = s.count
      savingsValue = s.filter { $0.status == .active }.reduce(0) { $0 + $1.principal }
    } catch {}
  }
}

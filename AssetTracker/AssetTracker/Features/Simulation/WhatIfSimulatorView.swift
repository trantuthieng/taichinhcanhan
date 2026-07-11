import Observation
import SwiftUI

@MainActor @Observable final class SimulationViewModel {
  var valuation = PortfolioValuation(
    totalAssets: 0, totalLiabilities: 0, cash: 0, stocks: 0, gold: 0, savings: 0, other: 0)
  var flows: [ForecastCashFlow] = []
  var exposures: [ConcentrationExposure] = []
  func load(until: Date) async {
    valuation = (try? await SnapshotScheduler().currentValuation()) ?? valuation
    flows = (try? await CashFlowForecastService().forecast(to: until)) ?? []
    exposures = (try? await ConcentrationAnalyzer().analyze()) ?? []
  }
}
struct WhatIfSimulatorView: View {
  @State private var model = SimulationViewModel()
  @State private var stockChange = -10.0
  @State private var until = Calendar.current.date(byAdding: .month, value: 6, to: .now) ?? .now
  @AppStorage("concentrationThreshold") private var threshold = 30.0
  var simulated: Decimal {
    model.valuation.netWorth + model.valuation.stocks * Decimal(stockChange) / 100
  }
  var body: some View {
    List {
      Section("Kịch bản chứng khoán") {
        Slider(value: $stockChange, in: -100...100, step: 1)
        LabeledContent("Thay đổi", value: "\(Int(stockChange))%")
        HStack {
          Text("Tài sản ròng giả định")
          Spacer()
          CurrencyText(value: simulated)
        }
        Text("Kịch bản chỉ tính tạm thời, không sửa dữ liệu thật.").font(.caption).foregroundStyle(
          .secondary)
      }
      Section("Dự báo dòng tiền") {
        DatePicker("Đến ngày", selection: $until, displayedComponents: .date).onChange(of: until) {
          _, _ in Task { await model.load(until: until) }
        }
        ForEach(model.flows) { flow in
          HStack {
            VStack(alignment: .leading) {
              Text(flow.title)
              Text(flow.date.formatted(date: .numeric, time: .omitted)).font(.caption)
                .foregroundStyle(.secondary)
            }
            Spacer()
            CurrencyText(value: flow.amount)
          }
        }
      }
      Section("Thông tin tỷ trọng") {
        ForEach(model.exposures.filter { $0.percentage > Decimal(threshold) }) { x in
          Text(
            "\(x.name) đang chiếm \(x.percentage.description)%, cao hơn mức bạn đặt \(Int(threshold))%."
          )
        }
        Text("Thông tin mô tả tỷ trọng, không phải khuyến nghị mua/bán.").font(.caption)
          .foregroundStyle(.secondary)
      }
    }.navigationTitle("Mô phỏng tài chính").task { await model.load(until: until) }
  }
}

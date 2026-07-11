import SwiftUI

struct FinancialAlertSettingsView: View {
  @AppStorage("concentrationThreshold") private var concentration = 30.0
  @AppStorage("profitLossThreshold") private var profitLoss = 20.0
  @AppStorage("creditUtilizationThreshold") private var creditUtilization = 80.0
  var body: some View {
    Form {
      Section("Tỷ trọng") {
        Slider(value: $concentration, in: 5...100, step: 1)
        LabeledContent("Cảnh báo khi vượt", value: "\(Int(concentration))%")
      }
      Section("Lãi/lỗ") {
        Slider(value: $profitLoss, in: 1...100, step: 1)
        LabeledContent("Cảnh báo khi |lãi/lỗ| vượt", value: "\(Int(profitLoss))%")
      }
      Section("Hạn mức thẻ tín dụng") {
        Slider(value: $creditUtilization, in: 10...100, step: 1)
        LabeledContent("Cảnh báo khi tỷ lệ dùng vượt", value: "\(Int(creditUtilization))%")
      }
    }.navigationTitle("Ngưỡng cảnh báo")
  }
}

import Observation
import SwiftUI

@MainActor @Observable final class ReportsViewModel {
  var exportURL: URL?
  var pdfURL: URL?
  var errorMessage: String?
  func prepareCSV() async {
    do {
      async let assets = AssetRepository().fetchAll()
      async let transactions = AssetTransactionRepository().fetchAll()
      exportURL = try CSVExportService().export(
        assets: try await assets, transactions: try await transactions)
    } catch { errorMessage = error.localizedDescription }
  }
  func preparePDF() async {
    do {
      pdfURL = try PDFReportGenerator().generate(
        valuation: try await SnapshotScheduler().currentValuation())
    } catch { errorMessage = error.localizedDescription }
  }
}

struct ReportsView: View {
  @State private var vm = ReportsViewModel()
  var body: some View {
    NavigationStack {
      List {
        Section("Báo cáo") {
          NavigationLink("Tài sản ròng", systemImage: "chart.xyaxis.line") { NetWorthReportView() }
          NavigationLink("Lãi/lỗ", systemImage: "arrow.up.right.and.arrow.down.left") {
            ProfitLossReportView()
          }
          NavigationLink("Phân bổ tài sản", systemImage: "chart.pie") { AllocationReportView() }
          NavigationLink("Lịch đáo hạn", systemImage: "calendar") { MaturityReportView() }
          NavigationLink("Thu nhập thụ động", systemImage: "banknote") { PassiveIncomeReportView() }
          NavigationLink("Nợ phải trả", systemImage: "creditcard") { DebtReportView() }
        }
        Section("Xuất dữ liệu") {
          if let url = vm.exportURL {
            ShareLink(item: url) { Label("Chia sẻ CSV", systemImage: "square.and.arrow.up") }
          } else {
            Button("Chuẩn bị file CSV", systemImage: "tablecells") {
              Task { await vm.prepareCSV() }
            }
          }
          if let url = vm.pdfURL {
            ShareLink(item: url) { Label("Chia sẻ PDF", systemImage: "doc.richtext") }
          } else {
            Button("Chuẩn bị báo cáo PDF", systemImage: "doc.richtext") {
              Task { await vm.preparePDF() }
            }
          }
        }
      }.navigationTitle("Báo cáo").alert(
        "Không thể tạo báo cáo", isPresented: .constant(vm.errorMessage != nil)
      ) {
        Button("OK") { vm.errorMessage = nil }
      } message: {
        Text(vm.errorMessage ?? "")
      }
    }
  }
}

private struct GrowthHistoryReportView: View {
  @State private var snapshots: [ValuationSnapshot] = []
  var body: some View {
    ScrollView { GrowthLineChartView(snapshots: snapshots).padding() }.navigationTitle(
      "Lịch sử tài sản"
    ).task {
      snapshots =
        (try? await ValuationSnapshotRepository().fetchAll().sorted { $0.date < $1.date }) ?? []
    }
  }
}

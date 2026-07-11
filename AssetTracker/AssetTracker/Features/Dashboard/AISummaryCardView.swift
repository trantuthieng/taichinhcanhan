import Observation
import SwiftUI

private struct AISummaryResponse: Decodable {
  let summary: String
  let generatedAt: Date
}
@MainActor @Observable final class AISummaryViewModel {
  var summary: String?
  var isLoading = false
  var errorMessage: String?
  func load() async {
    isLoading = true
    defer { isLoading = false }
    do {
      let response: AISummaryResponse = try await SupabaseClientProvider.shared.functions.invoke(
        "generate-ai-summary")
      summary = response.summary
    } catch { errorMessage = error.localizedDescription }
  }
}
struct AISummaryCardView: View {
  @State private var model = AISummaryViewModel()
  var body: some View {
    GroupBox("Tóm tắt tự động") {
      VStack(alignment: .leading, spacing: 10) {
        if model.isLoading {
          ProgressView()
        } else if let summary = model.summary {
          Text(summary)
        } else {
          Text(model.errorMessage ?? "Chưa có tóm tắt").foregroundStyle(.secondary)
          Button("Tạo tóm tắt") { Task { await model.load() } }
        }
        Divider()
        Label(
          "Đây là tóm tắt tự động, không phải tư vấn đầu tư",
          systemImage: "exclamationmark.triangle.fill"
        ).font(.caption.bold()).foregroundStyle(.orange)
      }
    }.task { await model.load() }
  }
}

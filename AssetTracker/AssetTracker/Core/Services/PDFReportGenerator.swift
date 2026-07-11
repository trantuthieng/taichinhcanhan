import Foundation
import UIKit

@MainActor struct PDFReportGenerator {
  func generate(valuation: PortfolioValuation, generatedAt: Date = .now) throws -> URL {
    let url = FileManager.default.temporaryDirectory.appendingPathComponent(
      "AssetTracker-report-\(Int(generatedAt.timeIntervalSince1970)).pdf")
    let format = UIGraphicsPDFRendererFormat()
    let bounds = CGRect(x: 0, y: 0, width: 595, height: 842)
    let renderer = UIGraphicsPDFRenderer(bounds: bounds, format: format)
    try renderer.writePDF(to: url) { context in
      context.beginPage()
      let title =
        [.font: UIFont.boldSystemFont(ofSize: 24), .foregroundColor: UIColor.label]
        as [NSAttributedString.Key: Any]
      let body =
        [.font: UIFont.systemFont(ofSize: 15), .foregroundColor: UIColor.label]
        as [NSAttributedString.Key: Any]
      ("Báo cáo tổng tài sản" as NSString).draw(at: CGPoint(x: 48, y: 48), withAttributes: title)
      ("Ngày xuất: \(generatedAt.formatted(date:.long,time:.shortened))" as NSString).draw(
        at: CGPoint(x: 48, y: 88), withAttributes: body)
      let values = [
        ("Tổng tài sản", valuation.totalAssets), ("Tổng nợ", valuation.totalLiabilities),
        ("Tài sản ròng", valuation.netWorth), ("Tiền", valuation.cash),
        ("Chứng khoán", valuation.stocks), ("Vàng", valuation.gold),
        ("Tiết kiệm", valuation.savings), ("Tài sản khác", valuation.other),
      ]
      for (index, item) in values.enumerated() {
        ("\(item.0): \(item.1.description) VND" as NSString).draw(
          at: CGPoint(x: 48, y: 135 + CGFloat(index * 34)), withAttributes: body)
      }
      ("Tài liệu được tạo bởi AssetTracker." as NSString).draw(
        at: CGPoint(x: 48, y: 790),
        withAttributes: [
          .font: UIFont.systemFont(ofSize: 11), .foregroundColor: UIColor.secondaryLabel,
        ])
    }
    return url
  }
}

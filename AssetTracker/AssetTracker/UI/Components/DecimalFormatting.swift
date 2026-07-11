import Foundation

extension Decimal {
  /// Làm tròn theo số chữ số thập phân (dùng cho hiển thị %).
  func rounded(_ scale: Int) -> Decimal {
    var source = self
    var result = Decimal()
    NSDecimalRound(&result, &source, scale, .plain)
    return result
  }
}

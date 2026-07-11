import SwiftUI

struct CurrencyText: View {
  let value: Decimal
  var code: String = "VND"

  var body: some View {
    Text(value, format: .currency(code: code).precision(.fractionLength(code == "VND" ? 0 : 2)))
      .monospacedDigit()
      .privacySensitiveAmount()
  }
}

extension Decimal {
  var doubleValue: Double { NSDecimalNumber(decimal: self).doubleValue }
}

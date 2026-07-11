import SwiftUI

extension NavigationLink where Label == SwiftUI.Label<Text, Image> {
  /// Convenience initializer mirroring `Label(_:systemImage:)` for a navigation destination.
  init(
    _ titleKey: LocalizedStringKey, systemImage: String,
    @ViewBuilder destination: () -> Destination
  ) {
    self.init(destination: destination) {
      SwiftUI.Label(titleKey, systemImage: systemImage)
    }
  }
}

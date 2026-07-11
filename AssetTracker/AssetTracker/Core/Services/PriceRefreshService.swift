import Foundation
import Supabase

/// Gọi Edge Function lấy giá vàng/chứng khoán khi mở app (thay cho cron chạy nền),
/// có throttle để tránh gọi quá dày. Edge Function chỉ ghi khi giá đổi (dedupe),
/// nên server luôn nhẹ mà app vẫn có giá mới mỗi lần mở.
@MainActor
enum PriceRefreshService {
  private static var lastRefresh: Date = .distantPast
  private static var isRefreshing = false
  private static let minInterval: TimeInterval = 120  // 2 phút

  static func refreshIfNeeded(force: Bool = false) async {
    guard !isRefreshing else { return }
    if !force, Date().timeIntervalSince(lastRefresh) < minInterval { return }
    isRefreshing = true
    defer { isRefreshing = false }
    await withTaskGroup(of: Void.self) { group in
      for name in ["fetch-gold-price", "fetch-stock-price"] {
        group.addTask {
          try? await SupabaseClientProvider.shared.functions.invoke(name)
        }
      }
    }
    lastRefresh = Date()
  }
}

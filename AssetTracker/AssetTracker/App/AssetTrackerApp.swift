import SwiftUI

@main
struct AssetTrackerApp: App {
  @State private var auth = BiometricAuthManager()
  var body: some Scene {
    WindowGroup {
      AppRootView(auth: auth)
        .task {
          await PriceRefreshService.refreshIfNeeded()
          await PriceAlertService.shared.requestAuthorization()
          if let liabilities = try? await LiabilityRepository().fetchAll() {
            await ReminderScheduler.shared.refreshLiabilities(liabilities)
          }
          if let deposits = try? await SavingsDepositRepository().fetchAll() {
            await ReminderScheduler.shared.refreshSavings(deposits)
          }
          if let accounts = try? await AssetAccountRepository().fetchAll() {
            await ReminderScheduler.shared.refreshForeignExchange(accounts)
          }
          await OfflineSyncManager.shared.start()
          try? await OfflineSyncManager.shared.flushPendingWrites()
        }
    }
  }
}

private struct AppRootView: View {
  let auth: BiometricAuthManager
  @Environment(\.scenePhase) private var scenePhase
  @State private var shieldsContent = true

  var body: some View {
    ZStack {
      if auth.isUnlocked { MainTabView(auth: auth) } else { LockScreenView(manager: auth) }
      if shieldsContent {
        Color(.systemBackground).overlay { Image(systemName: "lock.shield.fill").font(.largeTitle) }
          .ignoresSafeArea()
      }
    }
    .task {
      shieldsContent = false
      await auth.authenticate()
    }
    .onChange(of: scenePhase) { _, phase in
      switch phase {
      case .active:
        shieldsContent = false
        Task { await PriceRefreshService.refreshIfNeeded() }
      case .inactive: shieldsContent = true
      case .background:
        shieldsContent = true
        auth.lock()
      @unknown default: shieldsContent = true
      }
    }
  }
}

private struct MainTabView: View {
  let auth: BiometricAuthManager
  var body: some View {
    TabView {
      DashboardView()
        .tabItem { Label("Tổng quan", systemImage: "chart.pie.fill") }

      AssetsTabView()
        .tabItem { Label("Tài sản", systemImage: "banknote.fill") }

      TransactionsView()
        .tabItem { Label("Giao dịch", systemImage: "arrow.left.arrow.right") }

      ReportsView()
        .tabItem { Label("Báo cáo", systemImage: "chart.xyaxis.line") }

      SettingsView(auth: auth)
        .tabItem { Label("Cài đặt", systemImage: "gearshape.fill") }
    }
  }
}

private struct PlaceholderView: View {
  let title: String
  let systemImage: String

  var body: some View {
    NavigationStack {
      ContentUnavailableView(title, systemImage: systemImage)
        .navigationTitle(title)
    }
  }
}

#Preview {
  MainTabView(auth: BiometricAuthManager())
}

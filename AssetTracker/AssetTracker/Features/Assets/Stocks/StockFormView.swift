import SwiftUI

struct StockFormView: View {
  @Environment(\.dismiss) private var dismiss
  let stock: Asset?
  let accounts: [AssetAccount]
  let onCreate: (Asset, Decimal, Decimal, Decimal) async -> Bool
  let onUpdate: (Asset) async -> Bool
  @State private var symbol = ""
  @State private var name = ""
  @State private var category = AssetCategory.stock
  @State private var accountID: UUID?
  @State private var date = Date()
  @State private var quantity: Decimal = 0
  @State private var price: Decimal = 0
  @State private var fee: Decimal = 0
  @State private var currentPrice: Decimal = 0
  @State private var targetPrice: Decimal = 0

  var body: some View {
    NavigationStack {
      Form {
        TextField("Mã chứng khoán", text: $symbol).textInputAutocapitalization(.characters)
        TextField("Tên", text: $name)
        Picker("Loại", selection: $category) {
          ForEach(securityCategories, id: \.self) { Text($0.rawValue).tag($0) }
        }
        Picker("Tài khoản", selection: $accountID) {
          Text("Không chọn").tag(UUID?.none)
          ForEach(accounts) { Text($0.name).tag(Optional($0.id)) }
        }
        DatePicker("Ngày mua", selection: $date, displayedComponents: .date)
        TextField("Số lượng", value: $quantity, format: .number).keyboardType(.decimalPad)
        TextField("Giá mua", value: $price, format: .number).keyboardType(.decimalPad)
        TextField("Phí", value: $fee, format: .number).keyboardType(.decimalPad)
        TextField("Giá hiện tại", value: $currentPrice, format: .number).keyboardType(.decimalPad)
        TextField("Giá mục tiêu (tùy chọn)", value: $targetPrice, format: .number).keyboardType(
          .decimalPad)
      }.navigationTitle(stock == nil ? "Thêm chứng khoán" : "Sửa chứng khoán").toolbar {
        ToolbarItem(placement: .cancellationAction) { Button("Hủy") { dismiss() } }
        ToolbarItem(placement: .confirmationAction) {
          Button("Lưu") { Task { await save() } }.disabled(symbol.isEmpty || quantity <= 0)
        }
      }.onAppear { prefill() }
    }
  }

  private var securityCategories: [AssetCategory] {
    [
      .stock, .fundCertificate, .etf, .listedBond, .warrant, .foreignStock, .openEndFund,
      .otherSecurity,
    ]
  }
  private func prefill() {
    guard let s = stock else { return }
    symbol = s.symbol ?? ""
    name = s.name
    category = s.category
    accountID = s.accountID
    quantity = s.quantity
    price = s.averageCost
    currentPrice = s.currentPrice
    targetPrice = s.targetPrice ?? 0
    date = s.acquisitionDate ?? .now
  }
  private func save() async {
    let now = Date()
    let value = Asset(
      id: stock?.id ?? UUID(), name: name.nilIfEmpty ?? symbol.uppercased(), category: category,
      accountID: accountID,
      symbol: symbol.uppercased(), brand: nil, unit: .share, quantity: quantity, averageCost: price,
      currentPrice: currentPrice,
      currency: .vnd, acquisitionDate: date, valuationDate: now, purchaseLocation: nil,
      storageLocation: nil, invoiceNumber: nil,
      invoiceAttachmentURL: nil, grossWeight: nil, pureGoldWeight: nil, goldPurity: nil,
      laborCost: nil, gemstoneValue: nil,
      depreciationRate: nil, expectedBuybackPrice: nil, note: nil,
      targetPrice: targetPrice > 0 ? targetPrice : nil, createdAt: stock?.createdAt ?? now,
      updatedAt: now)
    let ok = stock == nil ? await onCreate(value, quantity, price, fee) : await onUpdate(value)
    if ok { dismiss() }
  }
}
